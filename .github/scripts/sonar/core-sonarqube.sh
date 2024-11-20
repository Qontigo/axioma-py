#!/bin/bash
#
# NOTE: This file is maintained in the Qontigo/devops-gh-actions repo (scripts/sonar/core-sonarqube.sh) and that copy will overwrite any changes made in any repo using the file
#       If changes are necessary to this file then you will need to raise a PR in that repo and perform appropriate testing with repos which use this file

# SonarQube helper functions for building a command line to run a scan
#

__coresonarqube_SCRIPT_DIR=$( cd -- "$( dirname -- "${BASH_SOURCE[0]}" )" &> /dev/null && pwd )

[[ -z "${VALIDATION_INCLUDED}" ]] && source "${__coresonarqube_SCRIPT_DIR}/../common/core-validation.sh"
[[ -z "${CONVERT_INCLUDED}" ]] && source "${__coresonarqube_SCRIPT_DIR}/../common/core-convert.sh"
[[ -z "${CONFIG_INCLUDED}" ]] && source "${__coresonarqube_SCRIPT_DIR}/../common/core-config.sh"
[[ -z "${CURL_INCLUDED}" ]] && source "${__coresonarqube_SCRIPT_DIR}/../common/core-curl.sh"
[[ -z "${UTILITIES_INCLUDED}" ]] && source "${__coresonarqube_SCRIPT_DIR}/../common/core-utilities.sh"
[[ -z "${LOGGING_INCLUDED}" ]] && source "${__coresonarqube_SCRIPT_DIR}/../common/core-logging.sh"

# Ensure the functions are included only once
if [[ -z "${SONARQUBE_INCLUDED}" ]]; then
  SONARQUBE_INCLUDED=1

  __CONFIG_FILENAME=".sonarconfig"
  __DOTNET_ARG_PREFIX="-d:" # The prefix to use when adding arguments to the Sonar dotnet command line
  __CLI_ARG_PREFIX="-D"   # The prefix to use when adding arguments to the Sonar CLI command line


  # "Private" function to get the argument prefix
  # Inputs:
  # - The builder
  #
  # Example Usage:
  # builder=()
  # prefix=$(__get_arg_prefix builder)
  #
  function __get_arg_prefix() {
    # shellcheck disable=SC2178 # https://github.com/koalaman/shellcheck/issues/1309
    local -n __prefixbuilder="$1"

    # -k:<key> is the format for the dotnet scanner; otherwise it is the CLI scanner
    if [[ "${__prefixbuilder[*]}" =~ "-k:" ]]; then
      echo "${__DOTNET_ARG_PREFIX}"
    else
      echo "${__CLI_ARG_PREFIX}"
    fi
  }

  # "Private" function to add an array of properties to the supplied builder
  #
  # Inputs:
  # - The builder to contain the results
  # - The array of key=value properties
  # Output:
  # - The builder is populated with sonar properties read from the array in the form key=value
  #
  function __add_properties_to_builder() {
    # shellcheck disable=SC2178 # https://github.com/koalaman/shellcheck/issues/1309
    local -n __propbuilder="$1"
    local -n __properties="$2"

    # shellcheck disable=SC2155
    local prefix=$(__get_arg_prefix __propbuilder)

    local kv
    for kv in "${__properties[@]}"; do
      local key="${kv%%=*}"
      local value="${kv#*=}"

      local argument_key
      # The project name is special in the dotnet scanner - we need to replace it in a different way.
      if [[ "${key,,}" == "sonar.projectname" && "${prefix}" == "${__DOTNET_ARG_PREFIX}" ]]; then
        argument_key="-n:"
      else
        argument_key="${prefix}${key}="
      fi

      # Check if the key already exists in the arguments array
      if ! [[ " ${__propbuilder[*],,} " == " ${argument_key,,}"* ]]; then
        # Ensure the value is surrounded by quotes
        if ! [[ "${value}" == \"*\" ]]; then
            value="\"${value}\""
        fi
        __propbuilder+=("${argument_key}${value}")
      else
        log_debug "${key} already exists in the argument list => Ignoring"
      fi
    done
  }


  # Checks if the project with the supplied key exists in SonarQube
  # Inputs:
  # - project key to check - e.g Axioma.Utilities
  # - URL to the Sonar instance - e.g. https://sonarqube.qontigo.com
  # - SonarQube Token to use.
  # Output:
  # - Global response_code will contain the http response from the SonarQube server
  # - Global response_body will contain the body of the response from the SonarQube server
  #
  # Returns:
  # 0 if the project exists in SonarQube
  # 1 if the project does not exist in SonarQube
  # 2 if there is any other problem in retrieving/parsing the response
  #
  # Example usage:
  # check_sonarqube_project_exists "Axioma.Utilities" "https://sonarqube.qontigo.com" "${token}"
  # result_code="$?"
  # if [[ "$result_code" -ne 0 ]]; then
  #  echo "SonarQube project check failed with code $result_code."
  # fi
  #

  # Global variables to pass back to caller.
  sonarqube_response_code="" # SonarQube response code
  sonarqube_response_body="" # SonarQube response body
  check_sonarqube_project_exists() {

    local project_key="$1"
    local server_url="$2"
    local token="$3"

    if ! (validate_mandatory_parameter "project_key" "${project_key}" && \
          validate_mandatory_parameter "server_url" "${server_url}" && \
          validate_mandatory_parameter "token" "${token}" ); then
      exit 1
    fi

    local sonar_uri="${server_url}/api/settings/values?component=${project_key}"
    log_debug "Checking uri: ${sonar_uri} to see if the project exists..."

    local response=""
    local curl_exit_code
    response=$(curl_with_retry "${sonar_uri}" -s -u "${token}:" -H "Accept: application/json")
    curl_exit_code=$?
    sonarqube_response_code=$(echo "${response}" | tail -n 1)
    sonarqube_response_body=$(echo "${response}" | head -n 1)
    if [[ ${curl_exit_code} -ne 0 ]]; then
      log_error "${sonarqube_response_body}"
      exit 2
    fi

    log_debug "sonarqube_response_code: ${sonarqube_response_code}"
    log_debug "sonarqube_response_body: ${sonarqube_response_body}"

    # Check if curl command was successful
    if [[ "${sonarqube_response_code}" == "000" || (${curl_exit_code} -ne 0 && ${curl_exit_code} -ne 22) ]]; then
      log_error "curl failed to connect to the server at ${server_url} (exit code: ${curl_exit_code}). Please check the server URL and network connection."
      exit 2
    fi

    if [[ ${sonarqube_response_code} -eq 404 ]]; then
      log_debug "404 response => Do not run the analysis for ${project_key}.  Now we have to figure out why...."

      local component_key=""
      # Look for Component key '<project>' in the not found error message
      msg=$(echo "${sonarqube_response_body}" | jq -r '.errors[].msg')
      component_key="${msg#*Component key \'}"
      component_key="${component_key%%\'*}"
      if [[ "${component_key}" == "${project_key}" ]]; then
        log_debug "SonarQube: Project key '${project_key}' does not exist in '${server_url}'"
        return 1
      else
        log_error "Failed to extract the component key '${project_key}' from the response from GET ${server_url}: ${sonarqube_response_code} - ${sonarqube_response_body}" true
        return 2
      fi
    elif [[ ${sonarqube_response_code} -ne 200 ]]; then
      log_error "Failed checking for the component key from the response from GET ${server_url}: ${sonarqube_response_code} - ${sonarqube_response_body}" true
      return 2
    fi

    return 0
  }

  # Given a settings JSON response from Sonar and a settings key, return the values from that key
  # If 'values' does not exit but 'value' does then use that as the result
  # Inputs:
  # - SonarQube JSON response body from a call to GET /api/settings/values?component=<project>
  # - The name of the key for which you want to retrieve the value
  # - The name of the array to populate
  # Output:
  # The array of values
  #
  # Example usage:
  # get_sonarqube_setting_values "${sonarqube_response_json}" "sonar.inclusions" all_inclusions
  #
  function get_sonarqube_setting_values() {
    local response="$1"
    local key="$2"
    local -n __values_array="$3"

    if ! (validate_mandatory_parameter "response" "${response}" && \
      validate_mandatory_parameter "key" "${key}" && \
      validate_mandatory_parameter "values_array" "$3" ); then
      exit 1
    fi

    values=$(jq -r --arg key "${key}" '.settings[] | select(.key == $key) | if has("values") then .values[] else .value end' <<< "${response}")
    if [[ -n "${values}" ]]; then
      local line
      while IFS= read -r line; do
        __values_array+=("$line")
      done <<< "${values}"
    fi
  }

  # Create a SonarQube command builder with the core set of arguments
  # Inputs:
  # - SonarQube Server Url
  # - Token for accessing same
  # - The type of scanner being used - "dotnet" or "cli"
  # - SonarQube project key for the project you want to analyse
  # - Version of the build project/component
  # - Optional build string to add to the analysis.  Default: version + GITHUB_RUN_NUMBER
  # - Optional override wait for Sonar analysis to complete. Usually this should be false/not supplied - ie, you WANT to wait for analysis
  # - Optional inclusions - this could be a single or multi-line string or a JSON array - but NOT a BASH array
  #
  # Example Usage:
  # builder=("$(sonar_command_builder "${{ inputs.sonar-url }}" "${{ inputs.token }}" "dotnet" "${{ inputs.project-key }}" "${version}" )" "${{ inputs.inclusions }}")
  #
  function sonar_command_builder() {

    local server_url="$1"
    local token="$2"
    local scanner_type="$3"
    local project_key="$4"
    local version="$5"
    local build_string="$6"
    local do_not_wait_for_results="$7"
    local inclusions="$8"
    local supported_scanner_types=("dotnet" "cli")

    if ! (validate_mandatory_parameter "server_url" "${server_url}" && \
          validate_mandatory_parameter "token" "${token}" && \
          validate_mandatory_parameter "scanner_type" "${scanner_type}" &&
          validate_mandatory_parameter "project_key" "${project_key}" &&
          validate_mandatory_parameter "version" "${version}" ); then
      exit 1
    fi
    if ! (validate_parameter_value false "${scanner_type}" "${supported_scanner_types[@]}"); then
      log_error "Invalid scanner_type '${scanner_type}'. Supported scanner types are: [${supported_scanner_types[*]}]"
      exit 1
    fi

    if [[ -z "${build_string}" ]]; then
      if [[ "${version}" =~ (\.|\+)$GITHUB_RUN_NUMBER$ ]]; then
        build_string="${version}" # Version already includes the run number
      else
        build_string="${version}+${GITHUB_RUN_NUMBER}"
      fi
    fi

    local wait_for_results
    wait_for_results=$([[ "${do_not_wait_for_results}" == "true" ]] && echo "false" || echo "true")

    local prefix
    local begin=""
    local project_param=""
    local version_param=""
    if [[ "${scanner_type}" == "dotnet" ]]; then
      prefix="${__DOTNET_ARG_PREFIX}"
      local begin="begin"
      project_param="-k:\"${project_key}\""
      version_param="-v:\"${version}\""
    else
      prefix="${__CLI_ARG_PREFIX}"
      project_param="${prefix}sonar.projectKey=\"${project_key}\""
      version_param="${prefix}sonar.projectVersion=\"${version}\""
    fi

    local builder=("${begin}"
        "${project_param}"
        "${prefix}sonar.token=\"${token}\""
        "${prefix}sonar.host.url=\"${server_url}\""
        "${prefix}sonar.qualitygate.wait=${wait_for_results}"
        "${prefix}sonar.buildString=\"${build_string}\""
        "${version_param}"
    )
    with_inclusions builder "${inclusions}"

    echo "${builder[@]}"
  }

  # Adds the supplied list of inclusions to the argument builder
  # Inputs:
  # - The builder
  # - The inclusions - this could be a single or multi-line string or a JSON array - but NOT a BASH array
  #
  # Example Usage:
  # builder=()
  # with_inclusions builder "Inc1 Inc2"
  #
  function with_inclusions() {
    # shellcheck disable=SC2178 # https://github.com/koalaman/shellcheck/issues/1309
    local -n __builder="$1"
    local inclusions=""
    inclusions=$(trim "$2")

    if ! (validate_mandatory_parameter "builder" "$1"); then
      exit 1
    fi

    local inclusions_array=()
    if [[ -n "${inclusions}" ]]; then
      local line
      while IFS= read -r line; do
        inclusions_array+=("$line")
      done < <(string_to_array "${inclusions}" || true)

      local csv=""
      local inclusion
      for inclusion in "${inclusions_array[@]}"; do
        if [[ -n "$csv" ]]; then
          csv="${csv},${inclusion}"
        else
          csv="${inclusion}"
        fi
      done
      # shellcheck disable=SC2155
      local prefix=$(__get_arg_prefix __builder)
      __builder+=("${prefix}sonar.inclusions=\"${csv}\"")
    fi
  }

  # Adds the branch/PR parameters to the argument builder based on the supplied parameters and github event
  # Inputs:
  # - The builder
  # - The default branch
  # - The branch being built
  # - The github event name that triggered the workflow
  # - The reference branch for new code comparisons.
  #   Set to "auto" by default, which should be fine in most cases except for relfixes) to allow the function to work it out as follows:
  #     - building a 'develop' or 'feature/XXX' branch => compare to the default branch
  #     - building the 'master' or 'main' branch => defer to the default for the project as defined in SonarQube itself (typically 'prod' for an application and 'previous version' for anything else)
  #     - building a 'release/XXX' branch => compare to the 'prod' branch (typically applies to application builds only)
  #     - building a 'relfix/XXX' branch => compare to the 'prod' branch - ideally this is where you override to specify the release the relfix is for
  #     - building the 'prod' branch => defer to the default for the project as defined in SonarQube itself (typically applies to application builds only and set to 'previous version')
  #     - building a 'hotfix/XXX' branch => compare to the 'prod' branch (typically applies to application builds only)
  # - The next three are applicable to PRs only and are mandatory for them
  #   - The target branch - e.g. form github.event.pull_request.base.ref (master)
  #   - The source branch - e.g. from github.event.pull_request.head.ref (feature/JIRA-123)
  #   - The PR number - e.g. from github.event.pull_request.number (456)
  #
  # Example Usage:
  # builder=()
  # with_github_event builder "master" "${{ github.ref_name}}" "release/1.2.3" "${{ github.event_name }}" "${{ github.event.pull_request.base.ref }}" "${{ github.event.pull_request.head.ref }}" "${{ github.event.pull_request.number }}"
  #
  function with_github_event() {

    # shellcheck disable=SC2178 # https://github.com/koalaman/shellcheck/issues/1309
    local -n __builder="$1"
    local default_branch="$2"
    local build_branch="$3"
    local reference_branch="${4:-auto}"
    local event_name="$5"
    local target_branch="$6"
    local source_branch="$7"
    local pr_number="$8"

    if ! (validate_mandatory_parameter "builder" "$1" && \
          validate_mandatory_parameter "default_branch" "${default_branch}" && \
          validate_mandatory_parameter "build_branch" "${build_branch}" && \
          validate_mandatory_parameter "reference_branch" "${reference_branch}" && \
          validate_mandatory_parameter "event_name" "${event_name}" ); then
      exit 1
    fi

    log_debug "with_github_event ${default_branch} ${build_branch} ${reference_branch} ${event_name} ${target_branch} ${source_branch} ${pr_number}"

    # shellcheck disable=SC2155
    local prefix=$(__get_arg_prefix __builder)

    if [[ "${event_name}" == "pull_request" ]]; then
      log_info "Scanning Pull Request: pull/${pr_number} to ${target_branch} ${build_branch}"

      if ! (validate_mandatory_parameter "target_branch" "${target_branch}" && \
            validate_mandatory_parameter "source_branch" "${source_branch}" && \
            validate_mandatory_parameter "pr_number" "${pr_number}"); then
        exit 1
      fi

      __builder+=("${prefix}sonar.pullrequest.base=\"${target_branch}\"")
      __builder+=("${prefix}sonar.pullrequest.branch=\"${source_branch}\"")
      __builder+=("${prefix}sonar.pullrequest.key=\"${pr_number}\"")
    else
      __builder+=("${prefix}sonar.links.scm=\"${GITHUB_SERVER_URL}/${GITHUB_REPOSITORY}/tree/${GITHUB_REF}\"")
      __builder+=("${prefix}sonar.links.ci=\"${GITHUB_SERVER_URL}/${GITHUB_REPOSITORY}/actions/runs/${GITHUB_RUN_ID}\"")
      __builder+=("${prefix}sonar.branch.name=\"${build_branch}\"")

      if [[ "${reference_branch}" == "auto" || -z "${reference_branch}" ]]; then
        case "${build_branch}" in
            develop|feature/*)
              reference_branch="${default_branch}"
              log_info "Scanning Branch: ${build_branch} w.r.t. the default branch ${reference_branch}"
              ;;
            master|main)
              reference_branch=""
              log_info "Scanning Branch: ${build_branch} w.r.t. the SonarQube project default for this branch"
              ;;
            release/*)
              reference_branch="prod"
              log_info "Scanning Release Branch: ${build_branch} w.r.t. ${reference_branch}"
              ;;
            relfix/*)
              reference_branch="prod"
              log_warning "Scanning Relfix Branch: ${build_branch} w.r.t. ${reference_branch} - typically it is preferable to specify an explicit release branch to compare to"
              ;;
            prod)
              reference_branch=""
              log_info "Scanning Branch: ${build_branch} w.r.t. the SonarQube project default for this branch"
              ;;
            hotfix/*)
              reference_branch="prod"
              log_info "Scanning Hotfix Branch: ${build_branch} w.r.t. ${reference_branch}"
              ;;
            *)
              log_warning "Scanning Branch: ${build_branch} w.r.t. ${reference_branch} - not a configured branch type so this may be incorrect"
              ;;
        esac
      fi

      if [[ -n "${reference_branch}" ]]; then
        __builder+=("${prefix}sonar.newCode.referenceBranch=\"${reference_branch}\"")
      fi
    fi
  }


  # Reads additional settings from the supplied array of key=value strings
  # Entries that already exist in the builder will not be overwritten with ones from the array
  #
  # Inputs:
  # - The builder to contain the results
  # - The properties - this could be a single or multi-line string or a JSON array but NOT a bash array
  # Output:
  # - The builder is populated with sonar properties read from the array in the form key=value
  #
  # Example Usage:
  # builder=()
  # with_sonar_properties builder "foo=bar"
  #
  function with_sonar_properties() {

    # shellcheck disable=SC2178 # https://github.com/koalaman/shellcheck/issues/1309
    local -n __builder="$1"
    local additional_properties=""
    additional_properties=$(trim "$2")

    if ! (validate_mandatory_parameter "builder" "$1"); then
      exit 1
    fi

    log_debug "with_sonar_properties ${additional_properties}"

    if [[ -n "${additional_properties}" ]]; then
      # shellcheck disable=SC2034 # https://github.com/koalaman/shellcheck/issues/1309
      readarray -t properties_array < <(string_to_array "${additional_properties}" "<none>" || true)
      __add_properties_to_builder __builder properties_array
    fi
  }

  # Reads additional settings from a Sonar config file (if it exists) to the argument builder
  # The file is in the standard 'ini' file format.
  # The settings can be first, outside any [Section] header or they can be inside a [Properties]
  # section anywhere in the file.
  # Entries that already exist in the builder will not be overwritten with ones from the file
  #
  # Inputs:
  # - The builder to contain the results
  # - Optional name of a Sonar property config file to apply - defaults to .sonarconfig
  # Output:
  # - The builder is populated with sonar properties read from the file in the form key=value
  #
  # Example usage:
  # builder=()
  # with_sonar_properties_file builder ".sonarconfig"
  #
  function with_sonar_properties_file() {

    # shellcheck disable=SC2178 # https://github.com/koalaman/shellcheck/issues/1309
    local -n __builder="$1"
    local properties_file="${2}"

    if ! (validate_mandatory_parameter "builder" "$1" && \
          validate_mandatory_parameter "properties_file" "${properties_file}"); then
      exit 1
    fi

    log_debug "with_sonar_properties_file ${properties_file}"

    # shellcheck disable=SC2034 # https://github.com/koalaman/shellcheck/issues/1309
    local file_props=()
    get_ini_file_section "${properties_file}" "Properties" file_props
    __add_properties_to_builder __builder file_props
  }

  # Adds the supplied property to the argument builder if it does not already exist.
  # This would normally be called after all other props have been added e.g. directly or via with_sonar_properties_file
  # Inputs:
  # - The builder
  # - The property key
  # - The property value
  #
  # Example Usage:
  # builder=()
  # with_sonar_properties_file builder "sonar.links.homepage" "${{ inputs.homepage-link }}"
  #
  function with_property_if_missing() {

    # shellcheck disable=SC2178 # https://github.com/koalaman/shellcheck/issues/1309
    local -n __builder="$1"
    local key="$2"
    local value="$3"

    if ! (validate_mandatory_parameter "builder" "$1" && \
          validate_mandatory_parameter "key" "${key}" ); then
      exit 1
    fi

    log_debug "with_property_if_missing ${key} ${value}"

    # shellcheck disable=SC2155
    local prefix=$(__get_arg_prefix __builder)

    if ! [[ " ${__builder[*]} " == *" ${prefix}${key}="* ]]; then
      __builder+=("${prefix}${key}=\"${value}\"")
    else
      log_debug "${key} key already supplied, ignoring"
    fi
  }

  # Sets Sonar logging to be verbose
  function with_verbose_logging() {
    # shellcheck disable=SC2178 # https://github.com/koalaman/shellcheck/issues/1309
    local -n __builder="$1"
    # shellcheck disable=SC2155
    local prefix=$(__get_arg_prefix __builder)

    __builder+=("${prefix}sonar.verbose=true")
  }

  # Returns the report location for a SonarQube report depending on if it is a PR or a branch analysis
  # Inputs:
  # - The event name
  # - The SonarQube server url
  # The build branch
  # The PR number (if any)
  # Returns:
  # The report location
  #
  # Example Usage:
  # report_location=$(get_report_location "${{ github.event_name }}" "${{ vars.SONARQUBE_SERVER_URL }}" "${{ github.ref_name }}" "${{ github.event.pull_request.number }}")
  #
  function get_report_location() {

    local event_name="$1"
    local server_url="$2"
    local build_branch="$3"
    local pr_number="$4"

    if ! (validate_mandatory_parameter "event_name" "${event_name}" && \
          validate_mandatory_parameter "server_url" "${server_url}"); then
      exit 1
    fi

    if [[ "${event_name}" == "pull_request" ]]; then
      if ! (validate_mandatory_parameter "pr_number" "${pr_number}"); then
        exit 1
      fi
      report_location="${server_url}/dashboard?pullRequest=${pr_number}"
    else
      if ! (validate_mandatory_parameter "build_branch" "${build_branch}"); then
        exit 1
      fi
      encoded_branch=$(printf '%s' "${build_branch}" | jq -s -R -r @uri)
      report_location="${server_url}/dashboard?branch=${encoded_branch}"
    fi
    echo "${report_location}"
  }

  # Gets the location of the .sonarconfig file (if any), starting with the project folder and moving up to the root
  # Inputs:
  # - The root folder - this is the highest level that will be checked
  # - The project folder name
  # Returns:
  # - The path to the config file or an empty string if there is none.
  # Example Usage:
  # config_file=$(get_config_file_location "." "Foo" | tail -n 1)
  function get_config_file_location() {

    local ROOT="$1"
    local project="$2"

    if ! (validate_mandatory_parameter "root" "${ROOT}" && \
          validate_mandatory_parameter "project" "${project}"); then
      exit 1
    fi

    log_debug "get_config_file_location ${ROOT} ${project}"

    local config_file="${ROOT}/src/${project}/${__CONFIG_FILENAME}"

    # First see if we can find a project-specific file
    if [[ ! -e "${config_file}" ]]; then
      log_debug "${config_file} not found => look for ${ROOT}/src/${__CONFIG_FILENAME}"
      config_file="${ROOT}/src/${__CONFIG_FILENAME}"
      if [[ ! -e "${config_file}" ]]; then
        log_debug "${config_file} not found => look for ${ROOT}/${__CONFIG_FILENAME}"
        config_file="${ROOT}/${__CONFIG_FILENAME}"
        if [[ ! -e "${config_file}" ]]; then
          log_debug "${config_file} not found => There is no file based configuration available"
          config_file=""
        fi
      fi
    fi

    echo "${config_file}"
  }

fi
