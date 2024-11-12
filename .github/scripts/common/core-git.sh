#!/bin/bash
#
# NOTE: This file is maintained in the Qontigo/devops-gh-actions repo (scripts/common/core-git.sh) and that copy will overwrite any changes made in any repo using the file
#       If changes are necessary to this file then you will need to raise a PR in that repo and perform appropriate testing with repos which use this file

# Git related functions

__coregit_SCRIPT_DIR=$( cd -- "$( dirname -- "${BASH_SOURCE[0]}" )" &> /dev/null && pwd )

[[ -z "${VALIDATION_INCLUDED}" ]] && source "${__coregit_SCRIPT_DIR}/core-validation.sh"

# Ensure git functions are included only once
if [[ -z "${GIT_INCLUDED}" ]]; then
  GIT_INCLUDED=1

  # Gets the name of the branch whether we are in a pull request or in a branch
  # Inputs:
  # - Optionally provide a branch name/github ref; otherwise detect from the environment variables
  # Example Usage:
  # branch="$(get_branch_name)"
  # branch="$(get_branch_name "refs/heads/feature/JIRA-123")"
  #
  function get_branch_name() {
    local ref="$1"
    if [[ "" == "${ref}" ]]; then
      echo "${GITHUB_HEAD_REF:-${GITHUB_REF#refs/heads/}}"
    else
      echo "${ref#refs/heads/}"
    fi
  }

  # Determines if the supplied reference is a pull request reference or not- e.g pull/123/merge
  # Inputs:
  # - The ref to check
  # Outputs:
  # - true if this is a PR ; false otherwise
  # Example Usage:
  # is_pr=$(is_pull_request "pull/123")
  #
  function is_pull_request() {
    local pull_request_ref="$1"

    if ! (validate_mandatory_parameter "pull_request_ref" "${pull_request_ref}"); then
      return 1
    fi

    if [[ "${pull_request_ref}" =~ ^(\/?(refs/)?pull\/[0-9]+(\/.*)?) ]]; then
      echo true
    else
      echo false
    fi
  }


  # Returns the PR number from the supplied string, which could be of the form:
  # * "refs/pull/<PR Number>/<something>"
  # * "pull/<PR Number>/<something>"
  # * "pull/<PR Number>"
  # * "<PR Number>"
  # Inputs:
  # - The PR string
  # Outputs:
  # - The PR number
  # Example Usage:
  # pr=$(get_pull_request_number "pull/123")
  #
  function get_pull_request_number() {
    local pull_request_ref="$1"

    if ! (validate_mandatory_parameter "pull_request_ref" "${pull_request_ref}"); then
      return 1
    fi

    if [[ "${pull_request_ref}" =~ ^((\/?refs\/)?(\/?pull\/)?([0-9]+)(\/.*)?)$ ]]; then
      echo "${BASH_REMATCH[4]}"
    else
      echo "PR number not found in '${pull_request_ref}'"
      return 1
    fi
  }

  # Determines if the supplied reference is a pull request merge reference - e.g pull/123/merge
  # Inputs:
  # - The ref to check
  # Outputs:
  # - true if this is a PR merge reference; false otherwise
  # Example Usage:
  # is_merge=$(is_merge_ref "pull/123")
  #
  function is_merge_ref() {
    local pull_request_ref="$1"

    if ! (validate_mandatory_parameter "pull_request_ref" "${pull_request_ref}"); then
      return 1
    fi

    if [[ "${pull_request_ref}" =~ ^([0-9]+\/merge)$ || "${pull_request_ref}" =~ (pull\/[0-9]+\/merge)$ ]]; then
      echo true
    else
      echo false
    fi
  }

fi