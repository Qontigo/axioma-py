#!/bin/bash
#
# NOTE: This file is maintained in the Qontigo/devops-gh-actions repo (scripts/common/core-versioning.sh) and that copy will overwrite any changes made in any repo using the file
#       If changes are necessary to this file then you will need to raise a PR in that repo and perform appropriate testing with repos which use this file

# Versioning functions

__coreversioning_SCRIPT_DIR=$( cd -- "$( dirname -- "${BASH_SOURCE[0]}" )" &> /dev/null && pwd )

[[ -z "${LOGGING_INCLUDED}" ]] && source "${__coreversioning_SCRIPT_DIR}/core-logging.sh"
[[ -z "${VALIDATION_INCLUDED}" ]] && source "${__coreversioning_SCRIPT_DIR}/core-validation.sh"

# Ensure versioning functions are included only once
if [[ -z "${VERSIONING_INCLUDED}" ]]; then
  VERSIONING_INCLUDED=1

  __VERSION_PATTERN="([0-9]+)\.([0-9]+)\.([0-9]+)"
  __GITVERSION_FILENAME="GitVersion.yml"
  __NERDBANKVERSION_FILENAME="version.json"
  __SUPPORTED_VERSION_FORMATS=("GitVersion" "Nerdbank")

  # "internal" implementation of get_version_from_string
  __get_version_from_string() {
    local format="$1"
    local data="$2"

    log_debug 'get_version_from_string '"${format}"' '"${data}"

    case "${format,,}" in
      gitversion)
        log_debug "GitVersion file => get next-version property"
        version=$(echo "${data}" | grep -oE 'next-version:\s*\S+' | cut -d' ' -f2)
        ;;
      nerdbank)
        log_debug "Nerdbank version file => get version property"
        version=$(echo "${data}" | jq -r '.version')
        ;;
      *)
        log_error "${format} is not recognised as either the GitVersion or Nerdbank formats => cannot retrieve version details"
        return 1
        ;;
    esac

    if [[ "${version}" == "" ]]; then
      log_error 'Version info not found in the '"${format}"' format input data: '"${data}"' => cannot retrieve version details'
      return 1
    fi

    echo "${version}"
  }

  # "internal" implementation of get_version_from_file
  __get_version_from_file() {
    local version_file="$1"
    local filename=""
    local data=""
    local exit_code

    log_debug "get_version_from_file ${version_file}"

    format=$(get_version_format_from_filename "${version_file}")
    exit_code=$?
    if [[ ${exit_code} -ne 0 ]]; then
      echo "${format}"
      return $exit_code
    fi

    data=$(cat "${version_file}")
    __get_version_from_string "${format}" "${data}"
  }

  # Returns the version format based on the supplied file name
  # Inputs:
  # - The path to the file
  # Output:
  # - The format of the file
  #
  # Example usage:
  # format=$(get_version_format_from_filename "./GitVersion.yml")
  # echo "Format: ${format}"
  #
  get_version_format_from_filename() {
    local filename
    filename=$(basename "$1")

    if ! (validate_mandatory_parameter "filename" "${filename}"); then
      exit 1
    fi

    if [[ "${filename}" == "${__GITVERSION_FILENAME}" ]]; then
      echo "GitVersion"
    elif [[ "${filename}" == "${__NERDBANKVERSION_FILENAME}" ]]; then
      echo "Nerdbank"
    else
      log_error "${filename} is not recognised as either a GitVersion or a Nerdbank version file => cannot retrieve version details"
      return 1
    fi
  }

  # Returns the version number from the supplied string representation of a format file
  # Inputs:
  # - The format of the provided string - either GitVersion or NerdBank
  # - The string to parse in the specified format
  # Output:
  # - The version number from the data
  #
  # Example usage:
  # version=$(get_version_from_string "GitVersion" "next-version: 1.2.3")
  # echo "Version: ${version}"
  #
  get_version_from_string() {
    local format="$1"
    local data="$2"
    local exit_code

    if ! (validate_mandatory_parameter "format" "${format}"); then
      exit 1
    fi

    if ! (validate_parameter_value false "${format}" "${__SUPPORTED_VERSION_FORMATS[@]}"); then
      log_error "Invalid version file format '${format}'. Supported formats are: [${__SUPPORTED_VERSION_FORMATS[*]}]"
      exit 1
    fi

    local raw_output
    raw_output="$(__get_version_from_string "${format}" "${data}")"
    exit_code=$?
    if [[ ${exit_code} -ne 0 ]]; then
      echo "${raw_output}"
    else
      echo "${raw_output}" | tail -n 1
    fi
    return $exit_code
  }

  # Returns the version number from the supplied GitVersion or Nerdbank version file
  # Inputs:
  # - The path to the file
  # Output:
  # - The version number read from the file (next-version from a GitVersion.yml file)
  #
  # Example usage:
  # version=$(get_version_from_file "./GitVersion.yml")
  # echo "Version: ${version}"
  #
  get_version_from_file() {
    local version_file="$1"
    local exit_code

    if ! (validate_mandatory_parameter "version_file" "${version_file}"); then
      exit 1
    fi

    if [[ ! -e "${version_file}" ]]; then
      log_error "Filename ${version_file} does not exist => cannot retrieve version details"
      return 1
    fi

    local raw_output
    raw_output="$(__get_version_from_file "${version_file}")"
    exit_code=$?

    if [[ ${exit_code} -ne 0 ]]; then
      echo "${raw_output}"
    else
      echo "${raw_output}" | tail -n 1
    fi
    return $exit_code
  }

  # Returns the major version number from the supplied version string or 1 if not found
  # Inputs:
  # - The version string
  # Output:
  # - The major version number
  #
  # Example usage
  # major_info="$(get_major_version "1.0.0")
  #
  get_major_version() {
    local version="$1"

    [[ "${version}" =~ $__VERSION_PATTERN ]]
    local major_version="${BASH_REMATCH[1]}"
    if [[ -z "${major_version}" ]]; then
      # Not a semver number but lets see if we can extract a major version from what we have anyway:
      major_version=$(echo "${version}" | grep -o '^[0-9]*')
    fi
    if [[ -n "${major_version}" ]]; then
      echo "${major_version}"
    else
      echo "Unable to extract major version from '${version}"
      return 1
    fi
  }

  # Compare two semantic versions to see if the next is greater than the previous version
  # Inputs:
  # - The previous version string
  # - The next version string
  # Output:
  # - Array of booleans to indicate major, minor, patch is greater respectively
  #
  # Example usage
  # version_info=("$(compare_versions "1.0.0" "1.0.1")")
  # major_is_greater="${version_info[0]}"
  # minor_is_greater="${version_info[1]}"
  # patch_is_greater="${version_info[0]}"
  #
  compare_versions() {

    local prev_version="$1"
    local next_version="$2"

    if ! (validate_mandatory_parameter "prev_version" "${prev_version}" && \
          validate_mandatory_parameter "next_version" "${next_version}" ); then
      exit 1
    fi

    # Extract major, minor, and patch versions from prev-version
    [[ "${prev_version}" =~ $__VERSION_PATTERN ]]
    local prev_major="${BASH_REMATCH[1]}"
    local prev_minor="${BASH_REMATCH[2]}"
    local prev_patch="${BASH_REMATCH[3]}"

    # Extract major, minor, and patch versions from next-version
    [[ "${next_version}" =~ $__VERSION_PATTERN ]]
    local next_major="${BASH_REMATCH[1]}"
    local next_minor="${BASH_REMATCH[2]}"
    local next_patch="${BASH_REMATCH[3]}"

    local major_is_greater=false
    local minor_is_greater=false
    local patch_is_greater=false
    if [[ "${next_major}" -gt "${prev_major}" ]]; then
      major_is_greater=true
    fi
    if [[ "${next_minor}" -gt "${prev_minor}" ]]; then
      minor_is_greater=true
    fi
    if [[ "${next_patch}" -gt "${prev_patch}" ]]; then
      patch_is_greater=true
    fi

    result=("${major_is_greater}" "${minor_is_greater}" "${patch_is_greater}")
    echo "${result[@]}"
  }

  # Compare a JSON dictionary of components with their previous and next semantic versions to see if the next is greater than the previous version.
  # Inputs:
  # - The JSON dictionary of the form:
  #    {
  #      "component1": {
  #        "prevVersion": "1.2.3",
  #        "nextVersion": "4.5.6"
  #      },
  #      "component2": {
  #        "prevVersion": "2.3.4",
  #        "nextVersion": "1.0.0"
  #      }
  #    }
  # Output:
  # - JSON dictionary which is the input dictionary augmented by an isGreater property for each entry - e.g.:
  #    {
  #      "component1": {
  #        "prevVersion": "1.2.3",
  #        "nextVersion": "4.5.6",
  #        "isGreater": true
  #      },
  #      "component2": {
  #        "prevVersion": "2.3.4",
  #        "nextVersion": "1.0.0",
  #        "isGreater": false
  #      }
  #    }
  #
  # Example usage
  # json_output=$(compare_multiple_versions "${json_input}")
  #
  compare_multiple_versions() {
    local input_json="$1"
    local output_json="{"

    if ! (validate_mandatory_parameter "input_json" "${input_json}"); then
      exit 1
    fi

    local raw_keys=""
    local components=()
    raw_keys=$(jq -r 'keys[]' <<< "${input_json}" | tr -d '\r')
    IFS=$'\n' read -d '' -r -a components <<< "${raw_keys}" || true # Don't want it to fail if there is only one key
    local component
    for component in "${components[@]}"; do
        local value=""
        local prev_version=""
        local next_version=""
        local version_info_result=""
        local version_info=()

        value=$(echo "${input_json}" | jq -r --arg key "${component}" '.[$key]')
        prev_version=$(jq -r '.prevVersion' <<< "${value}")
        next_version=$(jq -r '.nextVersion' <<< "${value}")
        version_info_result=$(compare_versions "${prev_version}" "${next_version}")
        readarray -t version_info <<< "${version_info_result}"

        local is_greater=false
        if [[ "${version_info[*]}" =~ "true" ]]; then
          is_greater=true
        fi

        # Now add this new property to the original property object for the component
        value="${value%\}}" # Remove the trailing }
        output_json+="\"${component}\": ${value}, \"isGreater\": ${is_greater}},"
    done

    echo "${output_json%,}}" | jq -c . # Remove the trailing comma and add a closing }
  }

  # Returns the informational version string to use to stamp an assembly
  # Inputs:
  # - The base version number
  # - The commit SHA
  # - The branch name
  # - The github run number name
  # - The PR number if it is a pull request
  # Output:
  # - The informational version string
  #
  # Example usage:
  # info_version=$(get_informational_version "1.2.3" "80f1a2e37283c3f7e578b83a28bc6dc32551395d" "feature/JIRA-789" "456" "104")
  # echo "${info_version}"
  #
  get_informational_version() {
    local version="$1"
    local sha="$2"
    local branch_name="$3"
    local run_number="$4"
    local pull_request="$5"

    info_version="${version}+${run_number}-${branch_name}"
    if [[ "${pull_request}" != "" ]]; then
      info_version="${info_version}(pull/${pull_request})"
    fi
    echo "${info_version}#${sha:0:7}"
  }

  # Returns the "cleaned" branch name that should be used in generating a branch-specific version
  # - For main/master/prod/release it will simply return an empty string as we typcially do no suffix these versions
  # - For relfix/XXX or hotfix/XXX branches it will return <version>-(relfix|hotfix)XXX with [-_/] stripped from it
  # - For feature branches and any other branches, it will return XXX where XXX is anything after the first "/" in the branch name, with [-_/] stripped from it
  # Inputs:
  # - The branch name
  # Output:
  # - The "cleaned" branch name
  #
  # Example usage:
  # clean_branch_name_for_version "main" # Returns ""
  # clean_branch_name_for_version "feature/JIRA-456-fix" # Returns JIRA456fix
  # clean_branch_name_for_version "relfix/JIRA-456" # Returns relfixJIRA456
  # clean_branch_name_for_version "hotfix/JIRA-456" # Returns hotfixJIRA456
  # clean_branch_name_for_version "some/other/branch" # Returns otherbranch
  #
  clean_branch_name_for_version() {
    local branch_name="$1"
    local stripped_branch=""
    case "${branch_name}" in
      main|master|prod|release/*)
        stripped_branch=""
        ;;
      relfix/*|hotfix/*)
        # Remove hyphens, underscores and slashes
        stripped_branch="${branch_name//[-_\/]}"
        ;;
      *)
        if [[ "${branch_name}" == */* ]]; then
          stripped_branch="${branch_name#*/}" # Extract the part after the first "/"
        fi
        # Remove hyphens, underscores, and any remaining slashes
        stripped_branch="${stripped_branch//[-_\/]}"
        ;;
    esac
    echo "${stripped_branch}"
  }

  # Returns the full version to use for the given version number and branch
  # - For main/master/prod/release/xxx it will simply return the supplied version number
  # - For relfix/XXX or hotfix/XXX branches it will return <version>-(relfix|hotfix)XXX with [-_/] stripped from it
  # - For feature branches and any other branches, it will return <version>-XXX where XXX is anything after the first "/", with [-_/] stripped from it
  # Inputs:
  # - The base version number
  # - The branch name
  # Output:
  # - The full version for the branch
  #
  # Example usage:
  # get_branch_version "1.2.3" "main" # Returns 1.2.3
  # get_branch_version "1.2.3" "release/24.3.2" # Returns 1.2.3
  # get_branch_version "1.2.3" "feature/JIRA-456-fix" # Returns 1.2.3-JIRA456fix
  # get_branch_version "1.2.3" "relfix/JIRA-456" # Returns 1.2.3-relfixJIRA456
  # get_branch_version "1.2.3" "hotfix/JIRA-456" # Returns 1.2.3-hotfixJIRA456
  # get_branch_version "1.2.3" "some/other/branch" # Returns 1.2.3-otherbranch
  #
  get_branch_version() {
    local version="$1"
    local branch_name="$2"
    local stripped_branch=""

    if ! (validate_mandatory_parameter "version" "${version}"); then
      exit 1
    fi

    stripped_branch=$(clean_branch_name_for_version "${branch_name}")
    if [[ "${stripped_branch}" == "" ]]; then
      echo "${version}"
    else
      echo "${version}-${stripped_branch}"
    fi
  }

fi
