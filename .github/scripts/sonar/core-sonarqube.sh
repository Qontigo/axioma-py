#!/bin/bash

__coresonarqube_SCRIPT_DIR=$( cd -- "$( dirname -- "${BASH_SOURCE[0]}" )" &> /dev/null && pwd )

[[ -z "${VALIDATION_INCLUDED}" ]] && source "${__coresonarqube_SCRIPT_DIR}/../common/core-validation.sh"
[[ -z "${CONVERT_INCLUDED}" ]] && source "${__coresonarqube_SCRIPT_DIR}/../common/core-convert.sh"
[[ -z "${CONFIG_INCLUDED}" ]] && source "${__coresonarqube_SCRIPT_DIR}/../common/core-config.sh"
[[ -z "${CURL_INCLUDED}" ]] && source "${__coresonarqube_SCRIPT_DIR}/../common/core-curl.sh"
[[ -z "${UTILITIES_INCLUDED}" ]] && source "${__coresonarqube_SCRIPT_DIR}/../common/core-utilities.sh"
[[ -z "${LOGGING_INCLUDED}" ]] && source "${__coresonarqube_SCRIPT_DIR}/../common/core-logging.sh"

# Ensure Sonarqube functions are included only once
if [[ -z "${SONARQUBE_INCLUDED}" ]]; then
  SONARQUBE_INCLUDED=1

  __CONFIG_FILENAME=".sonarconfig"

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
    response=$(curl_with_retry "${sonar_uri}" -s -u "${token}:" -H "Accept: application/json")
    curl_exit_code=$?
    sonarqube_response_code=$(echo "${response}" | tail -n 1)
    sonarqube_response_body=$(echo "${response}" | head -n 1)
    if [[ ${curl_exit_code} -ne 0 ]]; then
      log_error "${sonarqube_response_body}"
      return 2
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
      component_key=$(echo "${sonarqube_response_body}" | grep -oP "Component key '\\K[^']+")
      if [[ "${component_key}" == "${project_key}" ]]; then
        log_debug "SonarQube: Project key '${project_key}' does not exist in '${server_url}'"
        exit 1
      else
        log_error "Failed to extract the component key '${project_key}' from the response from GET ${server_url}: ${sonarqube_response_code} - ${sonarqube_response_body}" true
        exit 2
      fi
    elif [[ ${sonarqube_response_code} -ne 200 ]]; then
      log_error "Failed checking for the component key from the response from GET ${server_url}: ${sonarqube_response_code} - ${sonarqube_response_body}" true
      exit 2
    fi

    exit 0
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
      readarray -t __values_array <<< "${values}"
    fi
  }

  # Create a SonarQube command builder with the core set of arguments
  # Inputs:
  # - SonarQube Server Url
  # - Token for accessing same
  # - SonarQube project key for the project you want to analyse
  # - Version of the build project/component
  # - Optional build string to add to the analysis.  Default: "${version}+${GITHUB_RUN_NUMBER}"
  # - Optional override wait for Sonar analysis to complete. Usually this should be false/not supplied - ie, you WANT to wait for analysis
  #
  # Example Usage:
  # builder=("$(sonar_command_builder "${{ inputs.sonar-url }}" "${{ inputs.token }}" "${{ inputs.project-key }}" "${version}" )"")
  #
  sonar_command_builder() {

    local server_url="$1"
    local token="$2"
    local project_key="$3"
    local version="$4"
    local build_string="${5:-${version}+${GITHUB_RUN_NUMBER}}"
    local do_not_wait_for_results="$6"

    if ! (validate_mandatory_parameter "server_url" "${server_url}" && \
          validate_mandatory_parameter "token" "${token}" && \
          validate_mandatory_parameter "project_key" "${project_key}" &&
          validate_mandatory_parameter "version" "${version}" ); then
      exit 1
    fi

    wait_for_results=$([ "${do_not_wait_for_results}" == "true" ] && echo "false" || echo "true")

    local builder=("begin"
        "/k:\"${project_key}\""
        "/d:sonar.token=\"${token}\""
        "/d:sonar.host.url=\"${server_url}\""
        "/d:sonar.qualitygate.wait=${wait_for_results}"
        "/d:sonar.buildString=\"${build_string}\""
        "/v:\"${version}\""
    )
    echo "${builder[@]}"
  }

  # Adds the supplied list of inclusions to the argument builder
  # Inputs:
  # - The builder
  # - The inclusions - this could be a single or multi-line string or a JSON array
  #
  # Example Usage:
  # builder=()
  # with_inclusions builder "Inc1 Inc2"
  #
  with_inclusions() {
    # shellcheck disable=SC2178 # https://github.com/koalaman/shellcheck/issues/1309
    local -n __builder="$1"
    local inclusions=""
    inclusions=$(trim "$2")

    if ! (validate_mandatory_parameter "builder" "$1"); then
      exit 1
    fi

    log_debug "with_inclusions ${inclusions}"

    if [[ -n "${inclusions}" ]]; then
      readarray -t inclusions_array < <(string_to_array "${inclusions}" || true)
      local csv=""
      for inclusion in "${inclusions_array[@]}"; do
        if [[ -n "$csv" ]]; then
          csv="${csv},${inclusion}"
        else
          csv="${inclusion}"
        fi
      done
      __builder+=("/d:sonar.inclusions=\"${csv}\"")
    fi
  }

  # Adds the supplied .NET reports test path to the argument builder
  # Inputs:
  # - The builder
  # - The vstest reports path
  #
  # Example Usage:
  # builder=()
  # with_dotnet_test_path builder "./path/to/tests"
  #
  with_dotnet_test_path() {
    # shellcheck disable=SC2178 # https://github.com/koalaman/shellcheck/issues/1309
    local -n __builder="$1"
    local test_path="$2"

    if ! (validate_mandatory_parameter "builder" "$1"); then
      exit 1
    fi

    log_debug "with_dotnet_test_path ${test_path}"

    if [[ "${test_path}" != "" ]]; then
      __builder+=("/d:sonar.cs.vstest.reportsPaths=\"${test_path}\"")
    fi
  }

  # Adds the .NET code coverage report path to the argument builder
  # Inputs:
  # - The builder
  # - The coverate reports path
  #
  # builder=()
  # with_coverage_path builder "./path/to/coverage"
  with_dotnet_coverage_path() {

    # shellcheck disable=SC2178 # https://github.com/koalaman/shellcheck/issues/1309
    local -n __builder="$1"
    local coverage_path="$2"

    if ! (validate_mandatory_parameter "builder" "$1"); then
      exit 1
    fi

    log_debug "with_dotnet_coverage_path ${coverage_path}"

    if [[ "${coverage_path}" != "" ]]; then
      __builder+=("/d:sonar.cs.dotcover.reportsPaths=\"${coverage_path}\"")
    fi
  }

  # Adds the branch/PR parameters to the argument builder based on the supplied parameters and github event
  # Inputs:
  # - The builder
  # - The default branch
  # - The branch being built
  # - The github event name that triggered the workflow
  # - If this is a PR then this should be the base.ref
  # - If this is a PR then this should be the head.ref
  # - If this is a PR then this should be the PR number
  #
  # Example Usage:
  # builder=()
  # with_github_event builder "master" "${{ github.ref_name}}" "${{ github.event_name }}" "${{ github.event.pull_request.base.ref }}" "${{ github.event.pull_request.head.ref }}" "${{ github.event.pull_request.number }}"
  #
  with_github_event() {

    # shellcheck disable=SC2178 # https://github.com/koalaman/shellcheck/issues/1309
    local -n __builder="$1"
    local default_branch="$2"
    local build_branch="$3"
    local event_name="$4"
    local base_ref="$5"
    local head_ref="$6"
    local pr_number="$7"

    if ! (validate_mandatory_parameter "builder" "$1" && \
          validate_mandatory_parameter "default_branch" "${default_branch}" && \
          validate_mandatory_parameter "build_branch" "${build_branch}" &&
          validate_mandatory_parameter "event_name" "${event_name}" ); then
      exit 1
    fi

    log_debug "with_github_event ${default_branch} ${build_branch} ${event_name} ${base_ref} ${head_ref} ${pr_number}"

    if [[ "${event_name}" == "pull_request" ]]; then
      log_info "Scanning Pull Request: pull/${pr_number} to ${base_ref} ${build_branch}"

      if ! (validate_mandatory_parameter "base_ref" "${base_ref}" && \
            validate_mandatory_parameter "head_ref" "${head_ref}" && \
            validate_mandatory_parameter "pr_number" "${pr_number}"); then
        exit 1
      fi

      __builder+=("/d:sonar.pullrequest.base=\"${base_ref}\"")
      __builder+=("/d:sonar.pullrequest.branch=\"${head_ref}\"")
      __builder+=("/d:sonar.pullrequest.key=\"${pr_number}\"")
    else
      __builder+=("/d:sonar.links.scm=\"${GITHUB_SERVER_URL}/${GITHUB_REPOSITORY}/tree/${GITHUB_REF}\"")
      __builder+=("/d:sonar.links.ci=\"${GITHUB_SERVER_URL}/${GITHUB_REPOSITORY}/actions/runs/${GITHUB_RUN_ID}\"")
      __builder+=("/d:sonar.branch.name=\"${build_branch}\"")
      if [[ "${build_branch}" == feature/* ]]; then
          log_info "Scanning Branch: ${build_branch} w.r.t. ${default_branch} (SonarQube project default)"
      else
          log_info "Scanning Branch: ${build_branch} w.r.t. the previous version (SonarQube project default)"
      fi
    fi
  }

  # Reads additional settings from a Sonar config file (if it exists) to the argument builder
  # The file is in the standard 'ini' file format.
  # The settings can be first, outside any [Section] header or they can be inside a [Properties]
  # section anywhere in the file
  #
  # Inputs:
  # - The builder to contain the results
  # - Optional name of a Sonar property config file to apply - defaults to .sonarconfig
  # Output:
  # - The builder is populated with sonar properties read from the file in the form /d:key=value
  #
  # Example usage:
  # builder=()
  # with_sonar_properties_file builder ".sonarconfig"
  #
  with_sonar_properties_file() {

    # shellcheck disable=SC2178 # https://github.com/koalaman/shellcheck/issues/1309
    local -n __builder="$1"
    local properties_file="${2}"

    if ! (validate_mandatory_parameter "builder" "$1" && \
          validate_mandatory_parameter "properties_file" "${properties_file}"); then
      exit 1
    fi

    log_debug "with_sonar_properties_file ${properties_file}"

    file_props=()
    get_ini_file_section "${properties_file}" "Properties" file_props

    for kv in "${file_props[@]}"; do
      key="${kv%%=*}"
      value="${kv#*=}"

      # The project name is special - we need to replace it in a different way.
      if [[ "${key,,}" == "sonar.projectname" ]]; then
        local argument_key="/n:"
      else
        local argument_key="/d:${key}="
      fi

      # Check if the key already exists in the arguments array
      if ! [[ " ${__builder[*],,} " == " ${argument_key,,}"* ]]; then
        __builder+=("${argument_key}\"${value}\"")
      else
        log_debug "${key} already exists in the argument list => Ignoring"
      fi
    done
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
  with_property_if_missing() {

    # shellcheck disable=SC2178 # https://github.com/koalaman/shellcheck/issues/1309
    local -n __builder="$1"
    local key="$2"
    local value="$3"

    if ! (validate_mandatory_parameter "builder" "$1" && \
          validate_mandatory_parameter "key" "${key}" ); then
      exit 1
    fi

    log_debug "with_property_if_missing ${key} ${value}"

    if ! [[ " ${__builder[*]} " == *" /d:${key}="* ]]; then
      __builder+=("/d:${key}=\"${value}\"")
    else
      log_debug "${key} key already supplied, ignoring"
    fi
  }

  # Sets Sonar logging to be verbose
  with_verbose_logging() {
    # shellcheck disable=SC2178 # https://github.com/koalaman/shellcheck/issues/1309
    local -n __builder="$1"
    __builder+=("/d:sonar.verbose=true")
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
  get_report_location() {

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
  get_config_file_location() {

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
