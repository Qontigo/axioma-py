#!/bin/bash

# Functions relating to java builds

__corejava_SCRIPT_DIR=$( cd -- "$( dirname -- "${BASH_SOURCE[0]}" )" &> /dev/null && pwd )

[[ -z "${LOGGING_INCLUDED}" ]] && source "${__corejava_SCRIPT_DIR}/core-logging.sh"

# Ensure publishing functions are included only once
if [[ -z "${JAVA_INCLUDED}" ]]; then
  JAVA_INCLUDED=1

  # Returns the version of java currently installed, or 1 if java is not installed
  #
  # Example Usage:
  # installed_version="$(get_java_version)"
  #
  get_java_version() {
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

fi
