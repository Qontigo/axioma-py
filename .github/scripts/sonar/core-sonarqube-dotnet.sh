#!/bin/bash

# SonarQube dotnet specific function

__coresonarqubedotnet_SCRIPT_DIR=$( cd -- "$( dirname -- "${BASH_SOURCE[0]}" )" &> /dev/null && pwd )

[[ -z "${CONVERT_INCLUDED}" ]] && source "${__coresonarqubedotnet_SCRIPT_DIR}/../common/core-convert.sh"
[[ -z "${LOGGING_INCLUDED}" ]] && source "${__coresonarqubedotnet_SCRIPT_DIR}/../common/core-logging.sh"
[[ -z "${SONARQUBE_INCLUDED}" ]] && source "${__coresonarqubedotnet_SCRIPT_DIR}/core-sonarqube.sh"
[[ -z "${VALIDATION_INCLUDED}" ]] && source "${__coresonarqubedotnet_SCRIPT_DIR}/../common/core-validation.sh"

# Ensure Sonarqube functions are included only once
if [[ -z "${SONARQUBE_DOTNET_INCLUDED}" ]]; then
  SONARQUBE_DOTNET_INCLUDED=1

  # Adds the supplied .NET test report path(s) to the argument builder
  # Inputs:
  # - The builder
  # - The path(s) to the report(s) in vstest format
  #
  # Example Usage:
  # builder=()
  # with_dotnet_test_report_path builder "./path/to/tests"
  #
  with_dotnet_test_report_path() {
    # shellcheck disable=SC2178 # https://github.com/koalaman/shellcheck/issues/1309
    local -n __builder="$1"
    local test_paths="$2"

    if ! (validate_mandatory_parameter "builder" "$1"); then
      exit 1
    fi

    log_debug "with_dotnet_test_report_path ${test_paths}"

    if [[ -z "${test_paths}" ]]; then
      return 0
    fi

    local test_path_array
    local delimited_paths
    readarray -t test_path_array < <(string_to_array "${test_paths}" "<none>" || true)
    delimited_paths=$(array_to_csv "${test_path_array[@]}")
    __builder+=("-d:sonar.cs.vstest.reportsPaths=\"${delimited_paths}\"")
  }

  # Adds the .NET code coverage report path(s) to the argument builder
  # Inputs:
  # - The builder
  # - The path(s) to the coverage report(s) in dotCover HTML format
  #
  # builder=()
  # with_coverage_path builder "./path/to/coverage"
  with_dotnet_coverage_path() {

    # shellcheck disable=SC2178 # https://github.com/koalaman/shellcheck/issues/1309
    local -n __builder="$1"
    local coverage_paths="$2"

    if ! (validate_mandatory_parameter "builder" "$1"); then
      exit 1
    fi

    log_debug "with_dotnet_coverage_path ${coverage_paths}"

    if [[ -z "${coverage_paths}" ]]; then
      return 0
    fi

    local coverage_path_array
    local delimited_paths
    readarray -t coverage_path_array < <(string_to_array "${coverage_paths}" "<none>" || true)
    delimited_paths="$(array_to_csv "${coverage_path_array[@]}")"
    __builder+=("-d:sonar.cs.dotcover.reportsPaths=\"${delimited_paths}\"")
  }

fi
