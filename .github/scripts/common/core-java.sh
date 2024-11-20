#!/bin/bash
#
# NOTE: This file is maintained in the Qontigo/devops-gh-actions repo (scripts/common/core-java.sh) and that copy will overwrite any changes made in any repo using the file
#       If changes are necessary to this file then you will need to raise a PR in that repo and perform appropriate testing with repos which use this file

# Functions relating to java builds

__corejava_SCRIPT_DIR=$( cd -- "$( dirname -- "${BASH_SOURCE[0]}" )" &> /dev/null && pwd )

[[ -z "${LOGGING_INCLUDED}" ]] && source "${__corejava_SCRIPT_DIR}/core-logging.sh"

# Ensure the functions are included only once
if [[ -z "${JAVA_INCLUDED}" ]]; then
  JAVA_INCLUDED=1

  # Returns the version of java currently installed, or 1 if java is not installed
  #
  # Example Usage:
  # installed_version="$(get_java_version)"
  #
  function get_java_version() {
    local java_binary
    if command -v java &> /dev/null; then
      java_binary="java"
    elif [[ -n "${JAVA_HOME}" ]] && [[ -x "${JAVA_HOME}/bin/java" ]]; then
      java_binary="${JAVA_HOME}/bin/java"
    else
      log_error "Java is not installed or not found in the path or in JAVA_HOME at ${JAVA_HOME}/bin/java"
      return 1
    fi

    version=$("$java_binary" -version 2>&1 | grep -o 'version "[^"]\+"' | cut -d'"' -f2)
    echo "${version}"
  }

  # Get the version number from the POM file
  # Output:
  # The version from the POM file if successful
  # Note:
  # Required maven to be installed, on the path, and this function to be called from the root build folder
  #
  # Returns:
  # - 0 if successful
  # - 1 if the pom.xml file cannot be found in the current folder
  # - 2 if maven is not installed
  # - 3 if fetching the version from the POM file failed
  #
  # Example Usage:
  # pom_version="$(get_pom_version)"
  #
  function get_pom_version() {
    local pom_version=""

    if [[ ! -f "pom.xml" ]]; then
        log_error "pom.xml does not exist in the current folder."
        return 1
    fi

    if ! command -v mvn -v &> /dev/null; then
      log_error "Maven is not installed or is not found in the path"
      return 2
    fi

    if pom_version="$(mvn -q -Dexec.executable=echo -Dexec.args="\${project.version}" --non-recursive exec:exec)"; then
      echo "${pom_version//-SNAPSHOT/}" # if the version is <major>.<minor>-SNAPSHOT then we only want <major>.<minor>
    else
      log_error "Failed to fetch the POM version: ${pom_version}"
      return 3
    fi
  }

fi
