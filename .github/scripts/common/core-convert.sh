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
      mapfile -t array <<< "$(echo "${json_input}" | tr -d '\r')"
    else
      # Input is a multi-line string
      IFS=$'\n' read -r -d '' -a lines <<< "${input}"
      local line
      for line in "${lines[@]}"; do
        # Strip leading and trailing spaces from each line
        line="${line#"${line%%[![:space:]]*}"}"
        line="${line%"${line##*[![:space:]]}"}"
        if [[ -z "${separator}" ]]; then
          parts=("${line}")
        else
          IFS="${separator}" read -ra parts <<< "$line"
        fi
        local part
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

  # Converts an array into a json array
  # Inputs:
  # - The array to convert - e.g. ("foo" "bar")
  # Output:
  # - The json array - e.g. ["foo","bar"]
  #
  # Example usage:
  # data=("foo" "bar")
  # json=$(array_to_json "${data[@]}")
  #
  array_to_json() {
    local values=("$@")
    if [ ${#values[@]} -eq 0 ]; then
      echo '[]'
    else
      printf '%s\n' "${values[@]}" | jq -R . | jq -s -c .
    fi
  }

  # Converts a path to be cross-platform
  # Inputs:
  # - The path
  # - Optional root - eg. if the input was c:\foo we might want to map this to /mnt/c/foo
  # Output:
  # The path in a cross platform format
  #
  # Example usage:
  # echo "$(to_crossplatform_path "D:\foo\bar")"
  #
  to_crossplatform_path() {
    local path="$1"
    local root="$2"

    path="${path//\\//}" # Replace \ with /
    # Remove colon and add a leading / if necessary - e.g C:/ => /c
    if [[ "${path}" == *":"* ]]; then
      local drive="${path%%:*}"
      path="/${drive,,}${path#*:}"
    fi

    if [ -n "${root}" ]; then
      if [[ "${path}" != /* ]]; then
        root="${root}/"
      fi
    fi
    echo "${root}${path}"
  }

  # Converts a string (typically a path) to be a valid Github artifact name
  # It removes characters known to cause problems cross-platform
  # Inputs:
  # - The string to convert to a valid artifact name
  # Output:
  # A valid artifact name
  #
  # Example usage:
  # echo "$(to_artifact_name "D:\foo\bar")"
  #
  to_artifact_name() {
    local input="$1"
    echo -e "${input}" | tr -d '\":<>\|\*\?\r\n\\/\/ '
  }
fi
