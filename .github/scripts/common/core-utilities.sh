#!/bin/bash
# shellcheck disable=SC2155 # Ignore combined declaration and assignment
#
# NOTE: This file is maintained in the Qontigo/devops-gh-actions repo (scripts/common/core-utilities.sh) and that copy will overwrite any changes made in any repo using the file
#       If changes are necessary to this file then you will need to raise a PR in that repo and perform appropriate testing with repos which use this file

# These are utility functions that have no real other home.
# Functions should only be added here after due consideration and determination that there really is no other suitable home for them

__coreutilities_SCRIPT_DIR=$( cd -- "$( dirname -- "${BASH_SOURCE[0]}" )" &> /dev/null && pwd )

# Ensure convert functions are included only once
if [[ -z "${UTILITIES_INCLUDED}" ]]; then
  UTILITIES_INCLUDED=1

  # Returns enabled if set -e or disabled if set +e is in effect
  #
  # Example Usage:
  # errexit="$(get_errexit)"
  #
  function get_errexit() {
    # The below is very sensitive to changes - do not change "$- =~ e" unless you have a very good reason to.
    if [[ $- =~ e ]]; then
      echo "enabled"
    else
      echo "disabled"
    fi
  }

  # Resets set +e or set -e as it was originally
  # Inputs:
  # - enabled/disabled to indicate if set -e or set +e respectively should be in effect
  #
  # Example Usage:
  # original_errexit="$(get_errexit)"
  # reset_errexit "${original_errexit}"
  function reset_errexit() {

    local original_errexit="$1"
    if [[ "${original_errexit}" == "enabled" ]]; then
      set -e
    else
      set +e
    fi
  }

  # Returns enabled if set -o pipefail or disabled if set +o pipefail was called
  #
  # Example Usage:
  # pipefail="$(get_pipefail)"
  #
  function get_pipefail() {
    if ! set -o | grep -q "pipefail.*on"; then
      echo "disabled"
    else
      echo "enabled"
    fi
  }

  # Resets set -o pipefail or set +o pipefail as it was originally
  # Inputs:
  # - enabled/disabled to indicate if set -o pipefail or set +o pipefail respectively should be in effect
  #
  # Example Usage:
  # original_pipefail="$(get_pipefail)"
  # reset_pipefail "${original_pipefail}"
  function reset_pipefail() {

    local original_pipefail="$1"
    if [[ "${original_pipefail}" == "enabled" ]]; then
      set -o pipefail
    else
      set +o pipefail
    fi
  }

  # Trims leading and trailing spaces from the incoming string
  # Inputs:
  # - The string to be trimmed
  # Example Usage:
  # trimmed=$(trim " A String ")
  #
  function trim() {
    local input="$1"
    input="${input#"${input%%[![:space:]]*}"}"  # Remove leading whitespace
    input="${input%"${input##*[![:space:]]}"}"  # Remove trailing whitespace
    echo "${input}"
  }

  # Sets environment variables from an array
  # Inputs:
  # - The array of key=value environment variable values
  #
  # Example usage:
  # env_vars=("foo=bar" "baz=buzz")
  # set_environment_variables "${env_vars[@]}"
  #
  function set_environment_variables() {
    local entries
    local entry
    if [[ $# -eq 0 ]]; then
      return # No parameters
    fi

    eval "entries=($*)"
    for entry in "${entries[@]}"; do
      entry=$(trim "${entry}")
      if [[ -n "${entry}" ]]; then
        export "${entry?}"
      fi
    done
  }

fi
