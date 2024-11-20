#!/bin/bash
#
# NOTE: This file is maintained in the Qontigo/devops-gh-actions repo (scripts/common/core-validation.sh) and that copy will overwrite any changes made in any repo using the file
#       If changes are necessary to this file then you will need to raise a PR in that repo and perform appropriate testing with repos which use this file

# Validation functions

# Ensure the functions are included only once
if [[ -z "${VALIDATION_INCLUDED}" ]]; then
  VALIDATION_INCLUDED=1

  # Validates that the supplied parameter is not empty
  # Inputs:
  # - Name of the parameter
  # - Parameter value
  # Returns:
  # 1 if empty, 0 otherwise
  #
  # Example Usage:
  # if ! (validate_mandatory_parameter "sonar-url" "${{ inputs.sonar-url }}" ); then
  #   exit 1
  # fi
  #
  function validate_mandatory_parameter() {
    local name="$1"
    local value="$2"

    if [[ -z "${value}" || -z "${value// /}" ]]; then
        echo "::error::❌ ${name} is mandatory but has no value => cannot proceed."
        return 1
    fi
    return 0
  }

  # Validates that the supplied parameter's value is one of the supplied values
  # Inputs:
  # - Parameter value
  # - Is this a case-sensitive comparison?
  # - Array of values that are valid for this parameter
  # Returns:
  # 0 if valid, 1 otherwise
  #
  # Example Usage:
  # fruit=("apple" "orange" "grape")
  # if ! (validate_parameter_value "false" "apple" "${fruit[@]}"); then
  #   exit 1
  # fi
  #
  function validate_parameter_value() {
    local case_sensitive="$1"
    shift
    local value="$1"
    shift
    local valid_values=("$@")
    if [[ "${case_sensitive,,}" == "true" ]]; then
      if [[ " ${valid_values[*]} " == *" ${value} "* ]]; then
        return 0
      fi
    else
      if [[ " ${valid_values[*],,} " == *" ${value,,} "* ]]; then
        return 0
      fi
    fi
    return 1
  }

fi