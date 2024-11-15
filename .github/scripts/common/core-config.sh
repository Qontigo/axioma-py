#!/bin/bash
# shellcheck disable=SC2155 # Ignore combined declaration and assignment
#
# NOTE: This file is maintained in the Qontigo/devops-gh-actions repo (scripts/common/core-config.sh) and that copy will overwrite any changes made in any repo using the file
#       If changes are necessary to this file then you will need to raise a PR in that repo and perform appropriate testing with repos which use this file

# Configuration related functions

__coreconfig_SCRIPT_DIR=$( cd -- "$( dirname -- "${BASH_SOURCE[0]}" )" &> /dev/null && pwd )

[[ -z "${LOGGING_INCLUDED}" ]] && source "${__coreconfig_SCRIPT_DIR}/core-logging.sh"
[[ -z "${VALIDATION_INCLUDED}" ]] && source "${__coreconfig_SCRIPT_DIR}/core-validation.sh"

# Ensure config functions are included only once
if [[ -z "${CONFIG_INCLUDED}" ]]; then
  CONFIG_INCLUDED=1

  # Reads settings from an ini file (if it exists)
  # The file is in the standard 'ini' file format.
  # Any settings which are outside a section will be assumed to be in the "Properties" section
  #
  # Inputs:
  # - The full path to the config file
  # - Section name to read.
  # - The array to contain the results
  # - Optional boolean to fail if the file does not exist - Default: false
  # Output:
  # The builder is populated with lines of key=value pairs from the file
  #
  # Example usage:
  # properties=()
  # get_ini_file_section "./.sonarconfig" "Workflow" properties
  #
  function get_ini_file_section() {

    local ini_file="$1"
    local section="$2"
    # shellcheck disable=SC2178 # https://github.com/koalaman/shellcheck/issues/1309
    local -n __properties="$3"
    local must_exist="$4"
    local current_section=""

    if ! (validate_mandatory_parameter "ini_file" "${ini_file}" && \
          validate_mandatory_parameter "section" "${section}" && \
          validate_mandatory_parameter "properties" "$3"); then
      exit 1
    fi

    log_debug "get_ini_file_section ${ini_file} ${section} ${__properties} ${must_exist}"

    if [[ -f "${ini_file}" ]]; then
      log_debug "${ini_file} found - reading parameters from the file..."

      # Process the file, allowing for no empty line at the end and allowing for CRLF instead of just LF
      local line
      while IFS='=' read -r line || [ -n "${line}" ]; do
        line=$(trim "${line}")

        # Ignore empty lines and comment lines
        if [[ -z "${line}" || "${line}" == "#"* ]]; then
          continue
        fi

        if [[ "${line}" =~ ^\[[^]]+\]$ ]]; then
          current_section=$(trim "${line:1:-1}")  # Remove brackets and surrounding whitespace
        elif [[ "${line}" =~ ^[A-Za-z0-9_.]+= ]]; then
          local key=$(trim "${line%%=*}")
          local value=$(trim "${line#*=}")

          # If the section is empty, use "Properties" as the default section
          current_section="${current_section:-Properties}"

          # Check if the specified section matches the current section (case-insensitive)
          if [[ "${current_section,,}" == "${section,,}" ]]; then
            # Check if the key/value pair already exists in the builder array
            if ! [[ " ${__properties[*],,} " == " ${key,,}=${value,,} " ]]; then
              __properties+=("${key}=${value}")
            else
              log_debug "${key} already exists in the argument list => Ignoring"
            fi
          fi
        fi
      done < <(tr -d '\r' < "${ini_file}") # Read the file stripping off CR's if the file is in windows format
    else
      if [[ "${must_exist,,}" == "true" ]]; then
        log_error "${ini_file} not found"
        exit 1
      else
        log_skipped "${ini_file} not found - skip reading parameters from the file..."
      fi
    fi
  }

  # Get the value for the supplied key from the array of key=value properties
  # Inputs:
  # - The array of key=value properties
  # - The key of the property to return
  # - Optional default value to return if it is not found.  Defaults to ""
  # Returns:
  # The value for the supplied key or the default value if not found
  #
  # Example Usage:
  # properties=("foo=bar" "fail.OnMissingProject=always")
  # value=$(get_option_value properties "fail.OnMissingProject")
  #
  function get_option_value () {
    # shellcheck disable=SC2178 # https://github.com/koalaman/shellcheck/issues/1309
    local -n __properties="$1"
    local key="${2,,}"
    local default_value="$3"
    local kv

    for kv in "${__properties[@]}"; do
      local item_key="${kv%%=*}"
      if [[ "${item_key,,}" == "${key}" ]]; then
        echo "${kv#*=}"
        return
      fi
    done
    echo "${default_value}"
  }

fi