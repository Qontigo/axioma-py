#!/bin/bash

__coresonarqubecli_SCRIPT_DIR=$( cd -- "$( dirname -- "${BASH_SOURCE[0]}" )" &> /dev/null && pwd )

[[ -z "${VALIDATION_INCLUDED}" ]] && source "${__coresonarqubecli_SCRIPT_DIR}/../common/core-validation.sh"
[[ -z "${CONVERT_INCLUDED}" ]] && source "${__coresonarqubecli_SCRIPT_DIR}/../common/core-convert.sh"
[[ -z "${CONFIG_INCLUDED}" ]] && source "${__coresonarqubecli_SCRIPT_DIR}/../common/core-config.sh"
[[ -z "${CURL_INCLUDED}" ]] && source "${__coresonarqubecli_SCRIPT_DIR}/../common/core-curl.sh"
[[ -z "${UTILITIES_INCLUDED}" ]] && source "${__coresonarqubecli_SCRIPT_DIR}/../common/core-utilities.sh"

[[ -z "${LOGGING_INCLUDED}" ]] && source "${__coresonarqubecli_SCRIPT_DIR}/../common/core-logging.sh"
[[ -z "${SONARQUBE_INCLUDED}" ]] && source "${__coresonarqubecli_SCRIPT_DIR}/core-sonarqube.sh"

# Ensure Sonarqube functions are included only once
if [[ -z "${SONARQUBE_CLI_INCLUDED}" ]]; then
  SONARQUBE_CLI_INCLUDED=1

  # "Private" function to convert an array of file/folder paths to csv, optionally expanding any wildcard paths found (for Sonar arguments which do not support wildcards natively)
  # Sonar parameters such as sonar.junit.reportPaths do not accept wildcard paths so "**/target/surefire-reports/" for example would need to be expanded.
  # Inputs:
  # - Multi-line string or a JSON array of file/folder paths
  # - Should wildcards be expanded?  Default: false
  # Output:
  # - The comma separated values
  #
  # Example usage:
  # files=("**/target/surefire-reports/")
  # delimited=$(__string_to_sonar_array "${files[@]}" true)
  #
  __string_to_sonar_array() {
    local paths="$1"
    local expand_wildcards="${2:-false}"
    local path_array=()
    readarray -t path_array < <(string_to_array "${paths}" "<none>" || true)

    if [[ "${expand_wildcards}" == "true" ]]; then
      local expanded_paths=()
      local path
      for path in "${path_array[@]}"; do
        if [[ "${path}" == *"**"* ]]; then
          path="${path%/}" # Remove trailing slash if present
          local this_expanded_path=()
          readarray -t this_expanded_path < <(find . -type d -path "${path}" -o -type f -path "${path}")
          expanded_paths+=("${this_expanded_path[@]}")
        else
          expanded_paths+=("${path}")
        fi
      done
      array_to_delimited_string "," "${expanded_paths[@]}"
    else
      array_to_delimited_string "," "${path_array[@]}"
    fi
  }

  # Adds the supplied reports test report path(s) to the argument builder, depending on the language
  # Inputs:
  # - The builder
  # - The language the tests are for - one of 'generic', 'go', 'python', 'java'
  # - The path(s) to the test report(s) in the relevant format:
  #   - generic => Sonar generic format described here: https://docs.sonarsource.com/sonarqube/latest/analyzing-source-code/test-coverage/generic-test-data/
  #   - go => output of 'go test ...' in json format
  #   - java => Surefire XML format reports
  #   - python => python xUnit format test reports
  #
  # Example Usage:
  # builder=()
  # with_test_report_path builder "java" "./path/to/junit/tests"
  #
  with_test_report_path() {
    # shellcheck disable=SC2178 # https://github.com/koalaman/shellcheck/issues/1309
    local -n __builder="$1"
    local language="$2"
    local test_paths="$3"
    local supported_languages=("generic" "go" "java" "javascript" "python" "typescript")

    if [[ -z "${test_paths}" ]]; then
      return 0
    fi

    if ! (validate_mandatory_parameter "builder" "${1}"); then
      exit 1
    fi
    if ! (validate_parameter_value false "${language}" "${supported_languages[@]}"); then
      log_error "with_test_report_path - Invalid language type '${language}'. Supported languages for test reports are: [${supported_languages[*]}]"
      exit 1
    fi

    local param_name=""
    case "${language,,}" in
      go)
        param_name="sonar.go.tests.reportPaths"
        ;;
      java)
        param_name="sonar.junit.reportPaths"
        ;;
      python)
        param_name="sonar.python.xunit.reportPath"
        ;;
      *)
        param_name="sonar.testExecutionReportPaths" # generic format
        ;;
    esac

    local delimited_paths
    delimited_paths="$(__string_to_sonar_array "${test_paths}" true)"
    __builder+=("${__CLI_ARG_PREFIX}${param_name}=\"${delimited_paths}\"")
  }

  # Adds the supplied code coverage report path(s) to the argument builder, depending on the language
  # Inputs:
  # - The builder
  # - The language the coverage is for - one of 'generic', 'go', 'python', 'java'
  # - The path(s) to the coverage report(s) in the relevant format:
  #   - generic => Sonar generic format described here: https://docs.sonarsource.com/sonarqube/latest/analyzing-source-code/test-coverage/generic-test-data/#generic-test-coverage
  #   - go => output of 'go test ...' with coverage in json format
  #   - java => JaCoCo format reports
  #   - javascript => LCOV format reports
  #   - python => Cobertura XML-format reports e.g. from [pytest coverage report]
  #   - typescript => LCOV format reports
  #
  # Example Usage:
  # builder=()
  # with_coverage_path builder "typescript" "./path/to/lcov/reports"
  #
  with_coverage_path() {

    # shellcheck disable=SC2178 # https://github.com/koalaman/shellcheck/issues/1309
    local -n __builder="$1"
    local language="$2"
    local coverage_paths="$3"
    local supported_languages=("generic" "go" "java" "javascript" "python" "typescript")

    if [[ -z "${coverage_paths}" ]]; then
      return 0
    fi

    if ! (validate_mandatory_parameter "builder" "${1}"); then
      exit 1
    fi
    if ! (validate_parameter_value false "${language}" "${supported_languages[@]}"); then
      log_error "with_coverage_path - Invalid language type '${language}'. Supported languages for coverage types are: [${supported_languages[*]}]"
      exit 1
    fi

    local param_name=""
    case "${language,,}" in
      go)
        param_name="sonar.go.coverage.reportPaths"
        ;;
      java)
        param_name="sonar.coverage.jacoco.xmlReportPaths"
        ;;
      javascript|typescript)
        param_name="sonar.javascript.lcov.reportPaths"
        ;;
      python)
        param_name="sonar.python.coverage.reportPaths"
        ;;
      *)
        param_name="sonar.coverageReportPaths" # generic format
        ;;
    esac

    local delimited_paths
    delimited_paths="$(__string_to_sonar_array "${coverage_paths}" true)"
    __builder+=("${__CLI_ARG_PREFIX}${param_name}=\"${delimited_paths}\"")
  }

  # Adds the supplied SARIF formatted reports to the argument builder
  # Inputs:
  # - The builder
  # - The path(s) to the SARIF format report(s)
  #
  # Example Usage:
  # builder=()
  # with_sarif_reports builder "./path/to/sarif/reports"
  #
  function with_sarif_reports() {

    # shellcheck disable=SC2178 # https://github.com/koalaman/shellcheck/issues/1309
    local -n __builder="$1"
    local report_paths="$2"

    if ! (validate_mandatory_parameter "builder" "${1}"); then
      exit 1
    fi

    log_debug "with_sarif_reports ${report_paths}"

    if [[ -z "${report_paths}" ]]; then
      return 0
    fi

    local delimited_paths
    delimited_paths="$(__string_to_sonar_array "${report_paths}" true)"
    __builder+=("${__CLI_ARG_PREFIX}sonar.sarifReportPaths=\"${delimited_paths}\"")
  }

  # Adds the supplied Sonar generic issue reports to the argument builder
  # Described here: https://docs.sonarsource.com/sonarqube/latest/analyzing-source-code/importing-external-issues/generic-issue-import-format/
  # Inputs:
  # - The builder
  # - The path(s) to the generic format report(s)
  #
  # Example Usage:
  # builder=()
  # with_generic_reports builder "./path/to/generic/reports"
  #
  function with_generic_reports() {

    # shellcheck disable=SC2178 # https://github.com/koalaman/shellcheck/issues/1309
    local -n __builder="$1"
    local report_paths="$2"

    if ! (validate_mandatory_parameter "builder" "${1}"); then
      exit 1
    fi

    log_debug "with_generic_reports ${report_paths}"

    if [[ -z "${report_paths}" ]]; then
      return 0
    fi

    local delimited_paths
    delimited_paths="$(__string_to_sonar_array "${report_paths}" true)"
    __builder+=("${__CLI_ARG_PREFIX}sonar.externalIssuesReportPaths=\"${delimited_paths}\"")
  }

fi
