#!/bin/bash
# shellcheck disable=SC1091 # Ignore not following sourced files
# cspell:ignore coregit,mapstruct
#
# NOTE: This file is maintained in the Qontigo/devops-gh-actions repo (scripts/common/core-git.sh) and that copy will overwrite any changes made in any repo using the file
#       If changes are necessary to this file then you will need to raise a PR in that repo and perform appropriate testing with repos which use this file

# Git related functions

__coregit_SCRIPT_DIR=$( cd -- "$( dirname -- "${BASH_SOURCE[0]}" )" &> /dev/null && pwd )

[[ -z "${LOGGING_INCLUDED}" ]] && source "${__coregit_SCRIPT_DIR}/core-logging.sh"
[[ -z "${VALIDATION_INCLUDED}" ]] && source "${__coregit_SCRIPT_DIR}/core-validation.sh"

# Ensure the functions are included only once
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


  # Validates that the supplied branch name meets our standard requirements:
  # - Branch names must start with one of the allowed prefixes (release, feature, relfix, hotfix, or 'dependabot' for dependabot branches)
  # - release branches must be in one of the following formats:
  #   - N.N.N   - e.g. release/1.2.3
  #   - N.N.N.N - e.g. release/24.23.22.21
  #   - YYYY.NN - e.g. release/2025.22
  # - feature/relfix/hotfix branches must be in one of two formats, depending on if it is for JIRA or for Digital.ai Agility:
  #   - For JIRA it is <prefix>/JIRA-NO or <prefix>/JIRA-NO-<suffix> - e.g. feature/JIRA-123 or hotfix/JIRA-123-FIX-TEST
  #   - For Digital.ai Agility is is <prefix>/D-<NNN>, <prefix>/S-<NNN>, <prefix>/D-<NNN>-<suffix>, or <prefix>/S-<NNN>-<suffix> - e.g. feature/D-123 or hotfix/S-4567-SUFFIX
  #     No other single letter prefixes are allowed
  # - dependabot branches must be in the format dependabot/<some description, generated by dependabot> - e.g. dependabot/npm/express-4.17.1 or dependabot/maven/org.mapstruct-mapstruct-processor-1.6.3
  # Inputs:
  # - Optionally provide the branch name; otherwise detect from the environment variables
  # Returns:
  # - 0 if the branch name is valid
  # - 1 if the branch name fails length checks
  # - 2 if the branch name fails naming convention checks
  #
  # Example Usage:
  #  # validate_branch_name
  function validate_branch_name() {
    local branch_name="$1"

    local allowed_branches=("develop" "main" "master" "prod") # Branch names to ignore from the convention
    local branch_name_regex='^(hotfix|feature|relfix)\/([A-Z]{2,}-[0-9]+|[DS]-[0-9]+)(-[a-zA-Z0-9]+)*$|^release\/([0-9]{4}\.[0-9]{2}|([0-9]+\.){2,3}[0-9]+)(-[a-zA-Z0-9]+)*$|^dependabot\/[a-zA-Z]{2,}.{2,}$'
    local min_length=3 # Min length of the branch name (excluding the prefix)
    local max_length=100  # Max length of the branch name (excluding the prefix)

    branch_name="$(get_branch_name "${branch_name}")"
    log_info "Validating branch name: ${branch_name}"

    # shellcheck disable=SC2076 # I want to compare it literally
    if [[ " ${allowed_branches[*]} " =~ " ${branch_name} " ]]; then
      IFS=',';log_skipped "Branch name '${branch_name}' is in the allow list: ${allowed_branches[*]} - skipping further checks"
      return 0
    fi

    local branch_prefix="${branch_name%%/*}"   # get up to the first /
    local base_branch_name="${branch_name#*/}" # strip off everything up to and including the first /
    local branch_name_length=${#base_branch_name}

    if [[ $branch_name_length -lt $min_length ]]; then
      log_error "Branch name '${base_branch_name}' is shorter than the minimum allowed length: At least ${min_length} characters after the ${branch_prefix}/ prefix"
      return 1
    fi

    if [[ $branch_name_length -gt $max_length ]]; then
      log_error "Branch name '${base_branch_name}' is longer than the maximum allowed length: At most ${max_length} characters after the ${branch_prefix}/ prefix"
      return 1
    fi

    if [[ ! "${branch_name}" =~ ${branch_name_regex} ]]; then
      log_error "Branch name '${branch_name}' does not match the allowed branch naming convention (feature|hotfix|relfix)/><JIRA>, dependabot/<description> or release/<version>"
      log "Branch name regex used: ${branch_name_regex}"
      return 2
    fi

    log_success "Branch name '${branch_name}' is valid"
  }

fi
