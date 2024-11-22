#!/bin/bash
#
# NOTE: This file is maintained in the Qontigo/devops-gh-actions repo (scripts/common/core-dotnet.sh) and that copy will overwrite any changes made in any repo using the file
#       If changes are necessary to this file then you will need to raise a PR in that repo and perform appropriate testing with repos which use this file

# function related to dotnet builds

__coredotnet_SCRIPT_DIR=$( cd -- "$( dirname -- "${BASH_SOURCE[0]}" )" &> /dev/null && pwd )

[[ -z "${LOGGING_INCLUDED}" ]] && source "${__coredotnet_SCRIPT_DIR}/core-logging.sh"
[[ -z "${CONVERT_INCLUDED}" ]] && source "${__coredotnet_SCRIPT_DIR}/core-convert.sh"
[[ -z "${VALIDATION_INCLUDED}" ]] && source "${__coredotnet_SCRIPT_DIR}/core-validation.sh"

# Ensure the functions are included only once
if [[ -z "${DOTNET_INCLUDED}" ]]; then
  DOTNET_INCLUDED=1

  # Gets the runtime version for the supplied SDK version from the Microsoft.NETCoreSdk.BundledVersions.props file that comes with every SDK
  # Inputs:
  # - The SDK version to get the runtime version for
  # Outputs:
  # - The runtime version for the supplied SDK version or an error message if it cannot be found
  # Return codes:
  # - 0 if successful
  # - 1 if dotnet cannot be found
  # - 2 if the SDK version is not supplied
  # - 3 if the Microsoft.NETCoreSdk.BundledVersions.props file for the supplied SDK version cannot be determined
  # - 4 if the BundledNETCoreAppPackageVersion element is not found in the Microsoft.NETCoreSdk.BundledVersions.props file
  # - 5 if the version cannot be extracted from the BundledNETCoreAppPackageVersion element in the Microsoft.NETCoreSdk.BundledVersions.props file
  #
  # Example Usage:
  # framework_version=$(get_runtime_framework_version_for_sdk "8.0.403")
  # exit_code=$?
  # if [[ "${exit_code}" -ne "0" ]]; then
  #   log_error "Failed to get runtime framework version for SDK version: ${{ steps.setup.outputs.dotnet-version }} - exit code ${exit_code}"
  #   echo "${framework_version}"
  #   exit $exit_code
  # else
  #  log "Runtime framework version for SDK version: ${{ steps.setup.outputs.dotnet-version }} is ${framework_version}"
  # fi
  #
  function get_runtime_framework_version_for_sdk() {
    local sdk_version="$1"

    if ! (validate_mandatory_parameter "sdk_version" "${sdk_version}"); then
      exit 1
    fi

    if ! dotnet_version_output=$(dotnet --version 2>&1); then
      log_error "dotnet is not installed or not found in the path: ${dotnet_version_output}, cannot determine the runtime version"
      return 2
    fi

    # Find the path to the supplied SDK version
    local line
    local sdk_path
    while IFS= read -r line; do
      if [[ "${line}" == "${sdk_version} "* ]]; then
        sdk_path="${line#* }"
        sdk_path=$(to_crossplatform_path "${sdk_path//[\[\]$'\r']/}") # Get a cleaned up cross-platform path
        break
      fi
    done < <(dotnet --list-sdks)

    if [[ -z "${sdk_path}" ]]; then
      log_error "SDK version ${sdk_version} not found, cannot determine the runtime version"
      log "Installed SDKs:"
      dotnet --list-sdks
      return 3
    fi

    local sdk_version_path="${sdk_path%\\*}/${sdk_version}"
    if [[ ! -d "${sdk_version_path}" ]]; then
      log_error "SDK version ${sdk_version}: Path '${sdk_version_path}' not found, cannot determine the runtime version"
      log "SDKs in this path:"
      ls "${sdk_path}"
      return 3
    fi

    local props_file="${sdk_version_path}/Microsoft.NETCoreSdk.BundledVersions.props" # This file comes with every sdk
    if [[ ! -f "${props_file}" ]]; then
      log_error "SDK version ${sdk_version}: Path ${sdk_version_path} does not contain the required file ${props_file}, cannot determine the runtime version"
      return 3
    fi

    # Now extract the runtime version from the props file
    local version_line
    version_line=$(grep "BundledNETCoreAppPackageVersion" "${props_file}")
    if [[ -z "${version_line}" ]]; then
      log_error "SDK version ${sdk_version}: Props file at ${props_file} does not contain a 'BundledNETCoreAppPackageVersion' element, cannot determine the runtime version"
      return 4
    fi

    local runtime_version
    local regex='<BundledNETCoreAppPackageVersion>([^<]+)</BundledNETCoreAppPackageVersion>'
    if [[ "${version_line}" =~ ${regex} ]]; then
      runtime_version="${BASH_REMATCH[1]}"
    else
      log_error "SDK version ${sdk_version}: Props file at ${props_file} does not contain a valid 'BundledNETCoreAppPackageVersion' element (version line: '${version_line}'), cannot determine the runtime version"
      return 5
    fi

    echo "${runtime_version}"
  }

fi