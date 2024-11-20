#!/bin/bash
#
# NOTE: This file is maintained in the Qontigo/devops-gh-actions repo (scripts/common/core-nuget-publish.sh) and that copy will overwrite any changes made in any repo using the file
#       If changes are necessary to this file then you will need to raise a PR in that repo and perform appropriate testing with repos which use this file

# Functions relating to publishing packages to nuget.

__corenugetpublish_SCRIPT_DIR=$( cd -- "$( dirname -- "${BASH_SOURCE[0]}" )" &> /dev/null && pwd )

[[ -z "${LOGGING_INCLUDED}" ]] && source "${__corenugetpublish_SCRIPT_DIR}/core-logging.sh"
[[ -z "${CURL_INCLUDED}" ]] && source "${__corenugetpublish_SCRIPT_DIR}/core-curl.sh"
[[ -z "${GIT_INCLUDED}" ]] && source "${__corenugetpublish_SCRIPT_DIR}/core-git.sh"
[[ -z "${NUGET_INCLUDED}" ]] && source "${__corenugetpublish_SCRIPT_DIR}/core-nuget.sh"
[[ -z "${UTILITIES_INCLUDED}" ]] && source "${__corenugetpublish_SCRIPT_DIR}/core-utilities.sh"
[[ -z "${VALIDATION_INCLUDED}" ]] && source "${__corenugetpublish_SCRIPT_DIR}/core-validation.sh"

# Ensure the functions are included only once
if [[ -z "${NUGET_PUBLISH_INCLUDED}" ]]; then
  NUGET_PUBLISH_INCLUDED=1

  # Checks if this is a branch we would publish from at all
  # Inputs:
  # - The github event name
  # - The github.ref
  # - The github base ref
  # - The default branch name
  # Returns:
  # - 0 if we would publish from here
  # - 1 if we would not.
  #
  # Example Usage:
  # check_we_would_publish_from_here_at_all "${{ github.event_name }}" "${{ github.ref }}" "${{ github.base_ref }}" "${{ github.base_ref }}"
  function check_we_would_publish_from_here_at_all() {
    local github_event_name="$1"
    local github_ref="$2"
    local github_base_ref="$3"
    local default_branch="$4"

    if ! (validate_mandatory_parameter "github_event_name" "${github_event_name}" && \
          validate_mandatory_parameter "github_ref" "${github_ref}") ; then
      exit 1
    fi

    if [[ "${github_event_name}" == "pull_request" ]]; then
      log_info "This is a pull request to ${github_base_ref}. PR components are not published to any nuget repo => will not publish component to any nuget repo" true
      return 1
    fi

    if [[ "${github_ref}" != "refs/heads/${default_branch}" && "${github_ref}" != refs/heads/feature/* ]]; then
      log_info "This is not the ${default_branch} branch or a feature branch => will not publish component to any nuget repo" true
      return 1
    fi

    return 0
  }

  # Checks if the supplied package already exists in the repo
  # Inputs:
  # - The artifactory repo server url
  # - The Artifactory API key to access the repo
  # - The repo to check - e.g. nuget-components|nuget-features
  # - The package to check - e.g. Foo.1.2.3.nupkg
  # - Does it need to be published or not? If any sources for the component changed then usually yes
  # Returns:
  # - 0 if it does not already exist (or exists and we are not overwriting); 1 if it does and we would need to overwrite it;2 otherwise
  #
  # Example Usage:
  # check_package_does_not_already_exist_in_the_nuget_repo "https://artifactory-server.com" "${{ inputs.artifactory-api-key }}" "nuget-components" "Foo.1.2.3.nupkg"
  #
  function check_package_does_not_already_exist_in_the_nuget_repo() {
    local server="$1"
    local api_key="$2"
    local repo="$3"
    local package="$4"
    local needs_publish="$5"
    local search_url
    local response
    local response_body
    local response_code
    local curl_exit_code

    if ! (validate_mandatory_parameter "server" "${server}" && \
          validate_mandatory_parameter "api_key" "${api_key}" && \
          validate_mandatory_parameter "repo" "${repo}" && \
          validate_mandatory_parameter "package" "$package") ; then
      exit 1
    fi

    search_url="${server}/artifactory/api/search/artifact?name=${package}&repos=${repo}"
    response=$(curl_with_retry "${search_url}" -SL -H "X-JFrog-Art-Api: ${api_key}")
    curl_exit_code=$?
    response_code=$(echo "${response}" | tail -n 1)
    response_body=$(echo "${response}" | head -n 1)
    # Check if curl command was successful
    if [[ ${curl_exit_code} -ne 0 ]]; then
      log_error "Curl exited with code: ${curl_exit_code} - ${response_body}"
      return 2
    fi

    log_debug "Response from ${search_url}: ${response_code} - ${response_body}"
    if [[ $(echo "${response_body}" | jq '.results | length') -eq 0 ]]; then
      log_success "${package} does not already exist in the ${repo} repo => It would be Ok to publish it." true
    else
      if [[ "${needs_publish}" == "true" ]]; then
        log_error "${package} already exists in the ${repo} repo and you cannot overwrite it => Cannot publish this package version.%0ADelete it from the ${repo} repo if you really must re-publish this version" true
        return 1
      else
        log_debug "${package} already exists but we don't need to publish it => Ok to continue"
      fi
    fi
    return 0
  }

  # Looks for the package across all nuget repos and returns an array of the ones found
  # Inputs:
  # - The artifactory repo server url
  # - The Artifactory API key to access the repo
  # - The package to check - e.g. Foo.1.2.3.nupkg
  # Returns:
  # - An array of repos the package is in; or an empty array if not in any
  #
  # Example Usage:
  # repos=$(get_existing_nuget_repos_for_package "https://artifactory-server.com" "<artifactory key>" "Foo.1.2.3.nupkg")
  # for r in $repos; do
  #  echo "- ${r}"
  # done
  #
  function get_existing_nuget_repos_for_package() {
    local server="$1"
    local api_key="$2"
    local package="$3"
    local search_url
    local response
    local response_body
    local response_code
    local curl_exit_code

    if ! (validate_mandatory_parameter "server" "${server}" && \
          validate_mandatory_parameter "api_key" "${api_key}" && \
          validate_mandatory_parameter "package" "$package") ; then
      exit 1
    fi

    search_url="${server}/artifactory/api/search/artifact?name=${package}"
    response=$(curl_with_retry "${search_url}" -SL -H "X-JFrog-Art-Api: ${api_key}")
    curl_exit_code=$?
    response_code=$(echo "${response}" | tail -n 1)
    response_body=$(echo "${response}" | head -n 1)
    # Check if curl command was successful
    if [[ ${curl_exit_code} -ne 0 ]]; then
      log_error "${response_body}"
      exit 2
    fi

    # The response is an array of uri's each like this: <artifactory base url>/artifactory/api/storage/<repository>/<component>
    # so we need to extract the repository from the urls
    uris=$(echo "${response_body}" | jq -r '.results[].uri')

    local repository_names=()
    local uri
    while IFS= read -r uri; do
        repository_name="${uri#*storage/}"
        repository_name="${repository_name%%/*}"
        if [[ "${repository_name}" != "" ]]; then
          repository_names+=("$repository_name")
        fi
    done <<< "${uris}"

    echo "${repository_names[@]}"
  }

  # Checks if the supplied package should be published, depending on the event that triggered the workflow
  # Inputs:
  # - github.event_name - e.g. pull_request
  # - github.event.action - e.g. closed
  # - github.event.pull_request.merged - e.g. true
  # - github.ref
  # - The package - e.g. Foo.1.2.3.nupkg
  # - Does it need to be published or not? If any sources for the component changed then usually yes
  # Returns:
  # - 0 if we we can publish
  # - 1 if we would not.
  #
  # Example Usage:
  # if (check_should_publish_package "${{ github.event_name }}" "${{ github.event.action }}" "${{ github.event.pull_request.merged }}" "${github_ref}" "${package}" "${sources_changed}"); then
  #   allowed=true
  # else
  #   allowed=false
  # fi
  #
  function check_should_publish_package() {
    local github_event_name="$1"
    local github_event_action="$2"
    local github_pr_merged="$3"
    local github_ref="$4"
    local package="$5"
    local needs_publish="$6"

    if ! (validate_mandatory_parameter "github_event_name" "${github_event_name}" && \
          validate_mandatory_parameter "package" "${package}" ) ; then
      exit 1
    fi

    if [[ "${needs_publish}" == "true" ]]; then
      if [[ ("${github_event_name}" == "push") || ("${github_event_name}" == "workflow_dispatch") ]]; then
        log_info "src/* or other changes that would affect the built component found in a '${github_event_name}' event => Should publish ${package}" true
        return 0
      elif [[ ("${github_event_name}" == "pull_request") && ( "${github_event_action}" == "closed" ) && ( "${github_pr_merged}" == "true") ]] ; then
        log_info "src/* or other changes that would affect the built component found in a merged pull request => Should publish ${package}" true
        return 0
      else
        log_info "src/* or other changes that would affect the built component found for a '${github_event_name}' event for '${github_ref}' (not a branch we expect to publish from) => will not publish ${package}" true
        return 1
      fi
    else
      log_info "No src/* or other changes that would affect the built component found => will not publish ${package}" true
      return 1
    fi
  }

  # Checks if the component could be published depending on if the same version already exists
  # somewhere and if it overwriting that version is allowed
  # If the same version does not exist anywhere then publishing would be allowed
  function check_if_component_could_be_published() {
    local package="$1"
    local github_ref="$2"
    local artifactory_uri="$3"
    local artifactory_key="$4"

    if ! (validate_mandatory_parameter "package" "${package}" && \
          validate_mandatory_parameter "github_ref" "${github_ref}" && \
          validate_mandatory_parameter "artifactory_uri" "${artifactory_uri}" && \
          validate_mandatory_parameter "artifactory_key" "${artifactory_key}" ) ; then
      exit 1
    fi

    # Validate that the package filename contains the package name and semver
    local component_name_and_version="" component_name="" component_version=""
    component_name_and_version=$(get_component_name_and_version "${package}")
    exit_code=$?
    if [[ ${exit_code} -eq 0 ]]; then
      read -r component_name component_version <<< "${component_name_and_version}"
    fi
    if [[ ${exit_code} -ne 0"" || "${component_name}" == "" || "${component_version}" == "" ]]; then
      log_error "Cannot extract name and semantic version from the package file: ${package}"
      exit 1
    fi

    local branch_name="" target_repo="" other_repo=""
    branch_name="$(get_branch_name "${github_ref}")"
    target_repo="$(get_component_target_nuget_repository "${branch_name}")"
    other_repo="$(get_component_non_target_nuget_repository "${branch_name}")"

    local can_overwrite_in_this_repo=false
    if [[ "${branch_name}" == "master" || "${branch_name}" == "main" ]]; then
      can_overwrite_in_this_repo=false
    else
      can_overwrite_in_this_repo=true
    fi

    local existing_repos
    read -ra existing_repos <<< "$(get_existing_nuget_repos_for_package "${artifactory_uri}" "${artifactory_key}" "${package}")" || true

    if [[ "${#existing_repos[@]}" != "0" ]]; then
      log_debug "Found ${package} in $(IFS=", "; echo "${existing_repos[*]}") - checking if this is okay..."

      # shellcheck disable=SC2076 # I want to compare it literally
      if [[ " ${existing_repos[*]} " =~ " ${target_repo} " ]]; then
        if [[ "${can_overwrite_in_this_repo}" == "true" ]]; then
          log_info "Found ${package} in ${target_repo} already but overwrite is allowed => would be okay to publish"
        else
          log_error "Found ${package} in ${target_repo} already and this cannot be overwritten - please increment the version number or contact the Pipeline (DevXP) team if the existing package must be deleted"
          return 1
        fi
      fi
      # shellcheck disable=SC2076 # I want to compare it literally
      if [[ " ${existing_repos[*]} " =~ " ${other_repo} " ]]; then
        if [[ "${other_repo}" == "${NUGET_FEATURES}" ]]; then
          # Should be possible to clean up the packages in nuget-features so offer that as a solution.
          log_error "Found ${package} in ${other_repo} - you cannot publish the exact same version to ${target_repo} - please increment the version number or run the 'Cleanup Component Artifacts' action on this branch to remove the package in ${other_repo} or contact the Pipeline (DevXP) team if you cannot resolve the problem yourself."
        else
          log_error "Found ${package} in ${other_repo} - you cannot publish the exact same version to ${target_repo} - please increment the version number or contact the Pipeline (DevXP) team if the package in ${other_repo} must be deleted"
        fi
        return 1
      fi
    else
      log_info "${package} does not exist in either the ${target_repo} or ${other_repo} repository => would be okay to publish"
    fi
  }

fi
