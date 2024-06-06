#!/bin/bash

# data conversion functions

__coreconvert_SCRIPT_DIR=$( cd -- "$( dirname -- "${BASH_SOURCE[0]}" )" &> /dev/null && pwd )

[[ -z "${UTILITIES_INCLUDED}" ]] && source "${__coreconvert_SCRIPT_DIR}/core-utilities.sh"

# Ensure convert functions are included only once
if [[ -z "${CONVERT_INCLUDED}" ]]; then
  CONVERT_INCLUDED=1

  # Convert a multi-line string or a JSON array to a bash array
  # Inputs:
  # - The string to convert
  # - Optional separator between elements if it is NOT a JSON array.  Defaults to space in addition to newline
  #   or set to <none> if each line should be considered a separate entry
  # Output:
  # - The array created from the string
  #
  # Example usage:
  # multi_line_string="**/*.sln
  # **/*.csproj"
  # readarray -t my_array < <(string_to_array "${multi_line_string}")
  # for a in "${my_array[@]}"; do
  #  echo "- ${a}"
  # done
  #
  string_to_array() {
    local input="$1"
    local separator="$2"

    # shellcheck disable=SC2155
    local original_errexit="$(get_errexit)"
    set +e

    # Check if separator is not provided, default to space
    if [[ -z "${separator}" ]]; then
      separator=$' '
    elif [[ "${separator}" == "<none>" ]]; then
      separator=''
    fi

    local array=()

    # Check if the input is JSON array or multi-line string
    if [[ "${input}" == "["* && "${input}" == *"]" ]]; then
      # Input is a JSON array
      json_input=$(jq -r '.[]' <<< "${input}")
      mapfile -t array <<< "${json_input}"
    else
      # Input is a multi-line string
      IFS=$'\n' read -r -d '' -a lines <<< "${input}"
      for line in "${lines[@]}"; do
        # Strip leading and trailing spaces from each line
        line="${line#"${line%%[![:space:]]*}"}"
        line="${line%"${line##*[![:space:]]}"}"
        if [[ -z "${separator}" ]]; then
          parts=("${line}")
        else
          IFS="${separator}" read -ra parts <<< "$line"
        fi
        for part in "${parts[@]}"; do
          if [[ -n "${part}" && ! "${part}" =~ ^[[:space:]]*$ ]]; then
            array+=("${part}")
          fi
        done
      done
    fi

    # Return the array if non-empty
    if [[ ${#array[@]} -ne 0 ]]; then
      printf "%s\n" "${array[@]}"
    fi
    reset_errexit "${original_errexit}"
  }

  # Convert a string such as a response body to a compact JSON representation
  # Inputs:
  # - The string to convert
  # Output:
  # - The json representation
  #
  # Example usage:
  # response_body='[{"name":"Steve","age":69},{"name":"Elon","age":52}]'
  # json_result=$(response_body_to_json "$response_body")
  #
  string_to_json() {
    local raw_data="$1"
    jq -c '.' <<< "${raw_data}"
  }

  # Converts an array into a delimited string
  # Inputs:
  # - The delimiter to use
  # - The array to convert
  # Output:
  # - The delimited string
  #
  # Example usage:
  # data=("foo" "bar")
  # delimited=$(array_to_delimited_string ";" "${data[@]}")
  #
  array_to_delimited_string() {
    local IFS="$1"
    shift
    echo "$*"
  }

  # Converts an array into a csv string
  # Inputs:
  # - The array to convert
  # Output:
  # - The comma separated values
  #
  # Example usage:
  # data=("foo" "bar")
  # delimited=$(array_to_csv "${data[@]}")
  #
  array_to_csv() {
    local values=("$@")
    array_to_delimited_string "," "${values[@]}"
  }

fi
