#!/bin/bash

# Logging functions

__corelogging_SCRIPT_DIR=$( cd -- "$( dirname -- "${BASH_SOURCE[0]}" )" &> /dev/null && pwd )

[[ -z "${UTILITIES_INCLUDED}" ]] && source "${__corelogging_SCRIPT_DIR}/core-utilities.sh"

# Ensure logging functions are included only once
if [[ -z "${LOGGING_INCLUDED}" ]]; then
  LOGGING_INCLUDED=1

  # internal log message
  __log() {
    local type="$1"
    local prefix="$2"
    local message="$3"
    local log_as_notice="$4"
    if [[ "${log_as_notice}" == "true" ]]; then
      type="::notice::"
    fi
    echo "${type}${prefix}${message}"
  }

  # internal log summary message
  __log_summary() {
    local prefix="$1"
    local message="$2"
    local summary_message=""
    summary_message=$(__log "${prefix}" "${message}")
    if [[ -n "${GITHUB_ACTIONS}" ]]; then
      echo "${summary_message}" >> "${GITHUB_STEP_SUMMARY}"
    else
      echo "::summary::${summary_message}"
    fi
  }

  # Logs a message to debug
  log_debug() {
    __log "::debug::" "" "${1}"
  }

  # Logs a message (usually a variable assignment) to GITHUB_ENV if running in an action, otherwise just logs it at debug level
  # Inputs:
  # - The message to log
  #
  log_env() {
    log_debug "$*"
    if [[ -n "${GITHUB_ACTIONS}" ]]; then
      echo "$*" >> "${GITHUB_ENV}"
    fi
  }

  # Logs a message (usually a variable assignment) to GITHUB_OUTPUT if running in an action, otherwise just logs it at debug level
  # Inputs:
  # - The message to log
  #
  log_output() {
    log_debug "$*"
    if [[ -n "${GITHUB_ACTIONS}" ]]; then
      echo "$*" >> "${GITHUB_OUTPUT}"
    fi
  }

  # Logs a message
  # Inputs:
  # - The message to log
  # - Optional parameter to log as a notice message - true | false/not supplied (default)
  #
  log() {
    __log "" "" "$1" "$2"
  }

  # Logs a success message
  # Inputs:
  # - The message to log
  # - Optional parameter to log as a notice message - true | false/not supplied (default)
  #
  log_success() {
    __log "" "✅ " "$1" "$2"
  }

  # Logs an info level message
  # Inputs:
  # - The message to log
  # - Optional parameter to log as a notice message - true | false/not supplied (default)
  #
  log_info() {
    __log "" "ℹ️ " "$1" "$2"
  }

  # Logs a warning message
  # Inputs:
  # - The message to log
  # - Optional parameter to log as a notice message - true | false/not supplied (default)
  #
  log_warning() {
    __log "::warning::" "⚠️ " "$1" "$2"
  }

  # Logs a skipped message
  # Inputs:
  # - The message to log
  # - Optional parameter to log as a notice message - true | false/not supplied (default)
  #
  log_skipped() {
    __log "" "✖️ " "$1" "$2"
  }

  # Logs a failure message
  # Inputs:
  # - The message to log
  # - Optional parameter to log as a notice message - true | false/not supplied (default)
  #
  log_error() {
    __log "::error::" "❌ " "$1" "$2"
  }

  # Logs a summary message
  # Inputs:
  # - The message to log
  #
  log_summary() {
    __log_summary "" "$1"
  }

  # Logs a summary step info message
  # Inputs:
  # - The message to log
  #
  log_summary_info() {
    __log_summary "ℹ️ " "$1"
  }

  # Logs a summary step success message
  # Inputs:
  # - The message to log
  #
  log_summary_success() {
    __log_summary "✅ " "$1"
  }

  # Logs a summary step skipped message
  # Inputs:
  # - The message to log
  #
  log_summary_skipped() {
    __log_summary "✖️ " "$1"
  }

  # Logs a summary step failed message
  # Inputs:
  # - The message to log
  #
  log_summary_warning() {
    __log_summary "⚠️ " "$1"
  }

  # Logs a summary step failed message
  # Inputs:
  # - The message to log
  #
  log_summary_error() {
    __log_summary "❌ " "$1"
  }

  # Logs an array
  # Inputs:
  # - A label for the array
  # - The name of the array to print out
  # - Should the array always be logged or only in debug mode?  Default: debug mode
  #
  # Example usage:
  # all_changed_files=("file1.txt" "file2.txt" "file3.txt")
  # log_array "All files changed" all_changed_files
  #
  function log_array() {
    local label="$1"
    local -n __array="$2"
    local always="${3:-false}"
    original_errexit="$(get_errexit)"
    set +e

    if [[ "${always}" == "false" ]]; then
      logger=log_debug
    else
      logger=log
    fi

    $logger "${label}:"
    local item
    for item in "${__array[@]}"; do
      $logger "  - ${item}"
    done
    reset_errexit "${original_errexit}"
  }

  # Logs a JSON dictionary, typically workflow_dispatch inputs
  # Inputs:
  # - A label for the dictionary
  # - The JSON dictionary
  # - Should the array always be printed or only in debug mode?  Default: debug mode
  #
  # Example usage:
  # log_json_dictionary 'Input Parameters' '${{ toJson(inputs) }}'
  #
  function log_json_dictionary() {
    local label="$1"
    local json_dictionary="$2"
    local always="${3:-false}"
    original_errexit="$(get_errexit)"
    set +e

    if [[ "${always}" == "false" ]]; then
      logger=log_debug
    else
      logger=log
    fi

    $logger "${label}:"
    echo "${json_dictionary}" | jq -r 'to_entries[] | .key as $k | .value | if type=="string" then fromjson? // . else . end | [$k, .] | "\(.[0]) \(.[1])"' | \
    awk '
        BEGIN {
            max_width = 0
        }
        {
          # Calculate the width of the widest key
          if (length($1) > max) {
              max_width = length($1) + 1
          }
          lines[NR] = $0
        }
        END {
          for (i = 1; i <= NR; i++) {
              split(lines[i], arr, " ")
              key = arr[1]
              sub(arr[1] " ", "", lines[i])
              printf "%-*s: %s\n", max_width, key, lines[i]
          }
        }
    ' | while read -r line; do
        $logger "  - ${line}"
    done
    reset_errexit "${original_errexit}"
 }

fi
