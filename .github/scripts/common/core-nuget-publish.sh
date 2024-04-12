#!/bin/bash

# Functions relating to publishing to nuget.

__corenugetpublish_SCRIPT_DIR=$( cd -- "$( dirname -- "${BASH_SOURCE[0]}" )" &> /dev/null && pwd )

[[ -z "${LOGGING_INCLUDED}" ]] && source "${__corenugetpublish_SCRIPT_DIR}/core-logging.sh"
[[ -z "${CURL_INCLUDED}" ]] && source "${__corenugetpublish_SCRIPT_DIR}/core-curl.sh"

# Ensure publishing functions are included only once
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
  check_we_would_publish_from_here_at_all() {
    local github_event_name="$1"
    local github_ref="$2"
    local github_base_ref="$3"
    local default_branch="$4"

    if [[ "${github_event_name}" == "pull_request" ]]; then
      log_info "This is a pull request to ${github_base_ref}. PR components are not published to any nuget repo => Do nothing" true
      return 1
    fi

    if [[ "${github_ref}" != "refs/heads/${default_branch}" && "${github_ref}" != refs/heads/feature/* ]]; then
      log_info "This is not the ${default_branch} branch or a feature branch => will not publish component to any nuget repo" true
      return 1
    fi

    return 0
  }

  # Gets the correct target repo for the supplied github ref
  # Inputs:
  # - The github.ref
  # Returns:
  # - The nuget repo to publish to
  #
  # Example Usage:
  # repo="$(get_target_nuget_repository "${{ github.ref }}")"
  #
  get_target_nuget_repository() {
    local github_ref="$1"
    if [[  "${github_ref}" == feature/* || "${github_ref}" == refs/heads/feature/* ]]; then
      echo "nuget-features"
    else
      echo "nuget-components"
    fi
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
  # check_package_does_not_already_exist_in_the_nuget_repo "https://artifactory-server.com" "nuget-components" "Foo.1.2.3.nupkg" "${{ inputs.artifactory-api-key }}"
  #
  check_package_does_not_already_exist_in_the_nuget_repo() {
    local server="$1"
    local api_key="$2"
    local repo="$3"
    local package="$4"
    local needs_publish="$5"
    local search_url="${server}/artifactory/api/search/artifact?name=${package}&repos=${repo}"
    local response
    local response_body
    local response_code

    response=$(curl_with_retry "${search_url}" -SL -H "X-JFrog-Art-Api: ${api_key}")
    local curl_exit_code=$?
    response_code=$(echo "${response}" | tail -n 1)
    response_body=$(echo "${response}" | head -n 1)
    # Check if curl command was successful
    if [[ ${curl_exit_code} -ne 0 ]]; then
      log_error "${response_body}"
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

  # Checks if the supplied package can be published
  # Inputs:
  # - github.event_name - e.g. pull_request
  # - github.event.action - e.g. closed
  # - github.event.pull_request.merged - e.g. true
  # - github.ref
  # - The package - e.g. Foo.1.2.3.nupkg
  # - Does it need to be published or not? If any sources for the component changed then usually yes
  # Package name
  # Package version
  # Example Usage:
  # Returns:
  # - 0 if we we can publish
  # - 1 if we would not.
  # check_can_publish_package "${{ github.event_name }}" "${{ github.event.action }}" "${{ github.event.pull_request.merged }}" "${{ github.ref }}" "Foo.1.2.3.nupkg" "${{ inputs.sources-changed }}"
  #
  check_can_publish_package() {
    local github_event_name="$1"
    local github_event_action="$2"
    local github_pr_merged="$3"
    local github_ref="$4"
    local package="$5"
    local needs_publish="$6"

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

fi