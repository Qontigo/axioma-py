#!/bin/bash
# shellcheck disable=SC2155 # Ignore combined declaration and assignment

__coreutilities_SCRIPT_DIR=$( cd -- "$( dirname -- "${BASH_SOURCE[0]}" )" &> /dev/null && pwd )

# Ensure convert functions are included only once
if [[ -z "${UTILITIES_INCLUDED}" ]]; then
  UTILITIES_INCLUDED=1

  # Returns enabled if set -e or disabled if set +e is in effect
  #
  # Example Usage:
  # errexit="$(get_errexit)"
  #
  get_errexit() {
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
  reset_errexit() {

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
  get_pipefail() {
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
  reset_pipefail() {

    local original_pipefail="$1"
    if [[ "${original_pipefail}" == "enabled" ]]; then
      set -o pipefail
    else
      set +o pipefail
    fi
  }

  # Trims the incoming string
  # Example Usage:
  # trimmed=$(trim " A String ")
  trim() {
    echo "$1" | awk '{$1=$1};1'
  }

  # Gets the name of the branch whether we are in a pull request or in a branch
  # Inputs:
  # - Optionally provide a branch name/github ref; otherwise detect from the environment variables
  # Example Usage:
  # branch="$(get_branch_name)"
  # branch="$(get_branch_name "refs/heads/feature/JIRA-123")"
  get_branch_name() {
    local ref="$1"
    if [[ "" == "${ref}" ]]; then
      echo "${GITHUB_HEAD_REF:-${GITHUB_REF#refs/heads/}}"
    else
      echo "${ref#refs/heads/}"
    fi
  }

fi