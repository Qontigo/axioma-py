#!/bin/bash
#
# NOTE: This file is maintained in the Qontigo/devops-gh-actions repo (scripts/sonar/core-sonarqube-dotnet.sh) and that copy will overwrite any changes made in any repo using the file
#       If changes are necessary to this file then you will need to raise a PR in that repo and perform appropriate testing with repos which use this file

# SonarQube DOTNET scanner functions to support the core-sonarqube-dotnet-begin and core-sonarqube-dotnet-end actions
# Note that these are very specifically tied to these actions and not really intended for other uses
#

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
  # - The path(s) to the coverage report(s)
  #
  # builder=()
  # with_coverage_path builder "./path/to/coverage"
  #  - If the coverage path contains "SonarQube.xml" then the input is assumed to be in Sonar generic format - https://docs.sonarsource.com/sonarqube/latest/analyzing-source-code/test-coverage/test-coverage-parameters/#all-languages
  #  - If the coverage path contains any other .xml file then the input is assumed to be in VS Coverage XML format
  #  - Otherwise the input is assumed to be in dotCover HTML format
  with_dotnet_coverage_path() {

    # shellcheck disable=SC2178 # https://github.com/koalaman/shellcheck/issues/1309
    local -n __builder="$1"
    local coverage_paths="$2"

    if ! (validate_mandatory_parameter "builder" "$1"); then
      exit 1
    fi

    if [[ -z "${coverage_paths}" ]]; then
      return 0
    fi

    local coverage_path_array
    local delimited_paths
    if [[ "${coverage_paths}" == *"SonarQube.xml"* ]]; then
      coverage_key="sonar.coverageReportPaths"
    elif [[ "${coverage_paths}" == *".xml"* ]]; then
      coverage_key="sonar.cs.vscoveragexml.reportsPaths"
    else
      coverage_key="sonar.cs.dotcover.reportsPaths"
    fi
    readarray -t coverage_path_array < <(string_to_array "${coverage_paths}" "<none>" || true)
    delimited_paths="$(array_to_csv "${coverage_path_array[@]}")"

    __builder+=("-d:${coverage_key}=\"${delimited_paths}\"")
  }

fi
