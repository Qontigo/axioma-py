#!/bin/bash
#
# NOTE: This file is maintained in the Qontigo/devops-gh-actions repo (scripts/common/core-nuget.sh) and that copy will overwrite any changes made in any repo using the file
#       If changes are necessary to this file then you will need to raise a PR in that repo and perform appropriate testing with repos which use this file

# Functions relating to nuget packages

__corenuget_SCRIPT_DIR=$( cd -- "$( dirname -- "${BASH_SOURCE[0]}" )" &> /dev/null && pwd )

[[ -z "${LOGGING_INCLUDED}" ]] && source "${__corenuget_SCRIPT_DIR}/core-logging.sh"
[[ -z "${VALIDATION_INCLUDED}" ]] && source "${__corenuget_SCRIPT_DIR}/core-validation.sh"

# Ensure the functions are included only once
if [[ -z "${NUGET_INCLUDED}" ]]; then
  NUGET_INCLUDED=1

  NUGET_COMPONENTS="nuget-components"
  NUGET_DEVOPS="nuget-devops"
  NUGET_FEATURES="nuget-features"

  # Returns the component name and version from a package file of the form my.package.1.2.3.nupkg
  # Inputs:
  # - The full package name
  # Returns:
  # The component name followed by the version.
  #
  # Example Usage:
  # read -r name version < <(get_component_name_and_version "myPackage.1.2.3.nupkg")
  # echo "Component: ${name}, Version: ${version}"
  #
  function get_component_name_and_version() {
    local package="$1"

    if ! (validate_mandatory_parameter "package" "${package}") ; then
        exit 1
    fi
    package=$(basename "${package}" .nupkg)
    if [[ "${package}" =~ ^(.+)\.((0|[1-9][0-9]*)\.(0|[1-9][0-9]*)\.(0|[1-9][0-9]*)(-((0|[1-9][0-9]*|[0-9]*[a-zA-Z-][0-9a-zA-Z-]*)(\.(0|[1-9][0-9]*|[0-9]*[a-zA-Z-][0-9a-zA-Z-]*))*))?(\+([0-9a-zA-Z-]+(\.[0-9a-zA-Z-]+)*))?)$ ]]; then
        local component="${BASH_REMATCH[1]}"
        local version="${BASH_REMATCH[2]}"
        echo "${component} ${version}"
    else
        return 1
    fi
  }

  # Gets the correct component target repo for the supplied github ref
  # Inputs:
  # - The github.ref
  # - The package type - component or devops.  Defaults to component
  # Returns:
  # - The nuget repo to publish to
  #
  # Example Usage:
  # repo="$(get_component_target_nuget_repository "${{ github.ref }}")"
  #
  function get_component_target_nuget_repository() {
    local github_ref="$1"
    local package_type="${2:-component}"

    if ! (validate_mandatory_parameter "github_ref" "${github_ref}") ; then
        exit 1
    fi

    local branch="${github_ref#refs/heads/}"
    if [[ "${branch}" == "master" || "${branch}" == "main" ]]; then
        if [[ "${package_type}" == "component" ]]; then
            echo "${NUGET_COMPONENTS}"
        elif [[ "${package_type}" == "devops" ]]; then
            echo "${NUGET_DEVOPS}"
        else
            log_error "unrecognized/unsupported package type: ${package_type} - only 'component' and 'devops' are supported currently"
            exit 1
        fi
    elif [[ "${branch}" == feature/* ]] ; then
        echo "${NUGET_FEATURES}"
    else
        log_error "unrecognized/unsupported branch: ${github_ref} - only master/main and feature/XXX branches are supported"
        exit 1
    fi
  }


  # Gets the correct "other" component repo for the supplied github ref
  # ie, if we are targeting the nuget-components repo then return the nuget-features repo and vice-versa
  # Inputs:
  # - The github.ref
  # - The package type - component or devops.  Defaults to component
  # Returns:
  # - The nuget repo which we are NOT publishing to
  #
  # Example Usage:
  # repo="$(get_other_nuget_repository "${{ github.ref }}")"
  #
  function get_component_non_target_nuget_repository() {
    local github_ref="$1"
    local package_type="${2:-component}"

    if ! (validate_mandatory_parameter "github_ref" "${github_ref}") ; then
        exit 1
    fi

    local target_repo
    target_repo=$(get_component_target_nuget_repository "${github_ref}" "${package_type}")
    local ret_val=$?
    if [[ ${ret_val} -ne 0 ]]; then
        exit "${ret_val}"
    fi

    if [[ "${target_repo}" == "${NUGET_COMPONENTS}" || "${target_repo}" == "${NUGET_DEVOPS}" ]]; then
        echo "${NUGET_FEATURES}"
    else
        if [[ "${package_type}" == "component" ]]; then
            echo "${NUGET_COMPONENTS}"
        elif [[ "${package_type}" == "devops" ]]; then
            echo "${NUGET_DEVOPS}"
        else
            log_error "unrecognized/unsupported package type: ${package_type} - only 'component' and 'devops' are supported currently"
            exit 1
        fi
    fi
  }

fi
