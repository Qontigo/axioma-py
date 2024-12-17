#!/bin/bash
# shellcheck disable=SC1091 # Ignore not following sourced files
# shellcheck disable=SC2155 # Ignore combined declaration and assignment
# spellchecker:words RETRYABLE,CORECURL,ratelimit
#
# NOTE: This file is maintained in the Qontigo/devops-gh-actions repo (scripts/common/core-curl.sh) and that copy will overwrite any changes made in any repo using the file
#       If changes are necessary to this file then you will need to raise a PR in that repo and perform appropriate testing with repos which use this file

# curl related functions
__corecurl_SCRIPT_DIR=$( cd -- "$( dirname -- "${BASH_SOURCE[0]}" )" &> /dev/null && pwd )

[[ -z "${LOGGING_INCLUDED}" ]] && source "${__corecurl_SCRIPT_DIR}/core-logging.sh"
[[ -z "${UTILITIES_INCLUDED}" ]] && source "${__corecurl_SCRIPT_DIR}/core-utilities.sh"
[[ -z "${VALIDATION_INCLUDED}" ]] && source "${__corecurl_SCRIPT_DIR}/core-validation.sh"

# Ensure the functions are included only once
if [[ -z "${CURL_INCLUDED}" ]]; then
  CURL_INCLUDED=1
  CURL_DEFAULT_CONNECTION_TIMEOUT=120
  CURL_DEFAULT_MAX_REQUEST_TIMEOUT=600
  CURL_NON_RETRYABLE_STATUSES=(400 401 403 404 422) # From the Octokit retry plugin: https://github.com/octokit/plugin-retry.js/blob/9a2443746c350b3beedec35cf26e197ea318a261/src/index.ts#L14)
  RATE_LIMIT_REMAINING_HEADER_KEY="x-ratelimit-remaining"
  RATE_LIMIT_RESET_HEADER_KEY="x-ratelimit-reset"
  RETRY_HEADER_KEY="retry-after"

  # Checks the supplied response headers to see if they are from a GitHub response
  # Inputs:
  # - The headers to check (by reference
  # Returns:
  # - 0 if the headers are from a GitHub response; 1 otherwise
  # Example Usage:
  # if is_github_response headers; then
  #   echo "This is a GitHub response"
  # fi
  #
  function is_github_response() {
    declare -n __resp_headers=$1
    for key in "${!__resp_headers[@]}"; do
      if [[ "$key" == "X-GitHub-Request-Id" || "$key" == "x-github-request-id" ]]; then
        return 0
      fi
    done
    return 1
  }

  # Internal implementation for get_retry_from_response which will log messages
  # that we do not want to see in normal output
  function __get_retry_from_response() {
    local response_status="$1"
    declare -n __retry_headers=$2
    local retry="${3:-0}"
    local retry_after=0

    if [[ -z "${__retry_headers[*]}" ]]; then
      log_warning "No Response Headers"
    else
      # Convert the header keys to lowercase so we can compare them case-insensitively
      local -A lowercase_headers=()
      local key=""
      for key in "${!__retry_headers[@]}"; do
        lowercase_headers["${key,,}"]="${__retry_headers[$key]}"
      done
      # Check if the response has a Retry-After header
      local retry_after_value="${lowercase_headers[$RETRY_HEADER_KEY]}"
      if [[ -n "${retry_after_value}" ]]; then
        # Check if it is a number or a HTTP date
        if [[ "$retry_after_value" =~ ^[0-9]+$ ]]; then
          retry_after=$((retry_after_value))
          log_info "'${RETRY_HEADER_KEY}' header specifies ${retry_after} seconds"
        else
          # This is a http date, which is always expressed in GMT: https://developer.mozilla.org/en-US/docs/Web/HTTP/Headers/Date
          local retry_after_date=$(date -d "$retry_after_value" +%s)
          local current_utc_time=$(date -u +%s)
          retry_after=$((retry_after_date - current_utc_time))
          log_info "'${RETRY_HEADER_KEY}' header specifies '${retry_after_value}' which is ${retry_after} seconds from now"
        fi
      fi
      # If this is a Github response then we should respect the X-RateLimit-Reset header if it is > the Retry-After header (if present)
      if is_github_response lowercase_headers; then
        if [[ -n "${lowercase_headers[$RATE_LIMIT_RESET_HEADER_KEY]}" ]]; then
          if [[ "${lowercase_headers[$RATE_LIMIT_REMAINING_HEADER_KEY]}" == "0" ]]; then
            local reset_seconds="${lowercase_headers[$RATE_LIMIT_RESET_HEADER_KEY]}"
            local reset_date=$(date -d "@$reset_seconds" +%s)
            local current_utc_seconds=$(date -u +%s)
            local reset_after=$((reset_seconds - current_utc_seconds))
            # If both the Retry-After and the X-RateLimit-Reset exist then we want to pick the greater of the two values
            if [[ "${retry_after}" != "0" ]]; then
              if [[ "${reset_after}" -gt "${retry_after}" ]]; then
                retry_after="${reset_after}"
                log_info "Github Response '${RATE_LIMIT_RESET_HEADER_KEY}' header specifies '${reset_seconds}' (${reset_date}) which is ${reset_after} seconds from now and more than the '${RETRY_HEADER_KEY}' value => use this"
              else
                log_info "Github Response '${RATE_LIMIT_RESET_HEADER_KEY}' header specifies '${reset_seconds}' (${reset_date}) which is ${reset_after} seconds from now and less than the '${RETRY_HEADER_KEY}' value => use the '${RETRY_HEADER_KEY}' value"
              fi
            else
              retry_after="${reset_after}"
              log_info "Github Response '${RATE_LIMIT_RESET_HEADER_KEY}' header specifies '${reset_seconds}' (${reset_date}) which is ${reset_after} seconds from now"
            fi
          else
            log_info "Github Response '${RATE_LIMIT_REMAINING_HEADER_KEY}' header specifies '${lowercase_headers[$RATE_LIMIT_REMAINING_HEADER_KEY]}' requests remaining => do not consider the '${RATE_LIMIT_REMAINING_HEADER_KEY}' header"
          fi
        else
          log_info "Github Response with a status code '${response_status}' but no retry headers found"
        fi
      fi
    fi

    if [[ "${retry_after}" != "0" ]]; then
      retry_after=$((retry_after + 1)) # Since the retry is "after" a certain period, add 1 second to the wait time to ensure we don't retry too soon
    else
      if [[ "${response_status}" == "429" ]] && is_github_response __retry_headers; then
        log_info "Github Response with a status code '429' but no retry headers found => wait at least 60 seconds"
        # See https://docs.github.com/en/rest/using-the-rest-api/rate-limits-for-the-rest-api?apiVersion=2022-11-28#exceeding-the-rate-limit
        retry_after=$((60 * (2 ** retry)))
      else
        log_info "Response with a status code of '${response_status}' but no retry headers found"
      fi
    fi

    echo "$retry_after"
  }

  # Calculates the number of seconds to wait before retrying a failed HTTP operation based on the response and the retry attempt #
  # This function should be called for any 429 response and, if it is a Github Response, for a 403 also since that can indicate a rate limit issue.
  # See https://docs.github.com/en/rest/using-the-rest-api/rate-limits-for-the-rest-api?apiVersion=2022-11-28#exceeding-the-rate-limit for info on the latter.
  # The logic, after discussing with Github support, is essentially:
  # - If the response is a 403
  #   - If the X-RateLimit-Remaining is 0 then we should respect the X-RateLimit-Reset header
  #   - If the X-RateLimit-Remaining is not 0 then we should not retry at all
  #
  #   - If the response is a 429
  #     - If the X-RateLimit-Remaining is 0 then we should respect the greater of the Retry-After header or the X-RateLimit-Reset header
  #     - If the X-RateLimit-Remaining is not 0 then
  #       - If there is a Retry-After header, we should respect that
  #       - If there is no Retry-After header, we should wait at least 1 minute before retrying
  #
  # Inputs:
  # - The HTTP response status code
  # - The headers from the response (by reference)
  # - The number of the retry attempt (0 for the first attempt)
  # Returns:
  # - The number of seconds to wait before retrying
  #
  # Example Usage:
  # retry=$(get_retry_from_response 429 headers 0)
  function get_retry_from_response() {
    local response_status="$1"
    declare -n __headers_ref=$2
    local retry="${3:-0}"

    result=$(__get_retry_from_response "${response_status}" __headers_ref "${retry}")
    exit_code=$?
    if [[ "0" -ne "${return_code}" ]]; then
      log_error "__get_retry_from_response failed with exit code: ${exit_code}) ${result}"
      return "${exit_code}"
    fi
    echo "${result}" | tail -n 1
  }

  # Internal implementation for curl_with_retry which will log debug messages
  function __curl_with_retry() {
    local url="$1"                                              # The url to access
    local max_retries="$2"                                      # Maximum retry attempts
    local backoff="$3"                                          # Initial backoff time (seconds)
    local max_wait="$4"                                         # Maximum wait time (seconds)
    local raw_response="$5"                                     # Do we want to get the raw response?
    local connect_timeout=${CURL_DEFAULT_CONNECTION_TIMEOUT}    # Max time to make the connection
    local max_request_time=${CURL_DEFAULT_MAX_REQUEST_TIMEOUT}  # Max time the request can take
    local retry=0                                               # Current retry

    if [[ "${raw_response}" != "true" ]]; then # can't log debug messages in "raw" mode
      log_debug "__curl_with_retry $*"
    fi

    shift 5 # Remove the first 5 arguments

    # see if we are overriding any defaulted curl arguments
    local curl_options=()
    while [[ $# -gt 0 ]]; do
        case "$1" in
            --connect-timeout)
                connect_timeout="$2"
                shift 2
                ;;
            --max-time|-m)
                max_request_time="$2"
                shift 2
                ;;
            *)
                curl_options+=("$1")
                shift
                ;;
        esac
    done

    local original_errexit="$(get_errexit)"
    local original_pipefail="$(get_pipefail)"
    local response
    set +eo pipefail

    while ((retry < max_retries + 1)); do
      if [[ "${raw_response}" != "true" ]]; then # can't log debug messages in "raw" mode
        log_debug "curl -w \"%{response_code}\" --connect-timeout ${connect_timeout} --max-time ${max_request_time} --silent --fail-with-body --show-error --dump-header - ${curl_options[*]} ${url}"
      fi

      # shellcheck disable=SC2068
      response=$(curl -w "%{response_code}" --connect-timeout "${connect_timeout}" --max-time "${max_request_time}" --silent --fail-with-body --show-error --dump-header - "${curl_options[@]}" "${url}")
      local exit_code=$?
      local -A response_headers
      # Loop through the response headers and store them in an associative array
      # The end of the response headers is marked by an empty line
      local is_first_line=true
      local capturing_headers=false
      local headers_done=false
      while IFS= read -r line; do
        if [[ "${is_first_line}" == "true" ]]; then
          is_first_line=false
          # If the first line starts with HTTP/ then we have headers
          if [[ "${line}" == HTTP/* ]]; then
            capturing_headers=true
            continue
          else
            # First line, no HTTP/ => no headers so capture the entire response and exit the loop
            body="${response}"$'\n'
            break
          fi
        fi
        if [[ "${headers_done}" == "false" ]]; then
          if [[ "${capturing_headers}" == "true" ]]; then
            line="${line%$'\r'}" # Remove carriage return if present (headers are separated by CRLF)
            if [[ "" = "${line}" ]]; then
              headers_done=true
            else
              local header_key="${line%%:*}"
              local header_value="${line##*: }"
              response_headers["${header_key,,}"]="${header_value}"
            fi
          fi
        else
          body+="${line}"$'\n'
        fi
      done <<< "${response}"

      # Remove the trailing newline character from the body
      body="${body%$'\n'}"
      local response_status="${body: -3}"
      local response_body="${body:0:-3}"

      if [[ "${raw_response}" != "true" ]]; then
        response_body="${response_body//[$'\t\r\n']}"
      fi
      reset_errexit "${original_errexit}"
      reset_pipefail "${original_pipefail}"
      if [[ "${response_body}" == "" ]]; then
        response_body="<empty>"
      fi
      if [[ "${raw_response}" != "true" ]]; then # can't log debug messages in "raw" mode
        local headers_string=""
        if [[ ${#response_headers[@]} -gt 0 ]]; then
          headers_string=", response headers: ["
          for header_key in "${!response_headers[@]}"; do
            headers_string+="${header_key}: ${response_headers["${header_key}"]}, "
          done
          headers_string="${headers_string%, }]"  # Remove the trailing comma and space
        fi
        log_debug "curl exit code: ${exit_code}, response status: ${response_status}, raw response: ${response_body}${headers_string}"
      fi

      # shellcheck disable=SC2076 # I want to compare literally to CURL_NON_RETRYABLE_STATUSES
      if [[ ${exit_code} -eq 0 || ${exit_code} -eq 22 ]]; then
        if [[ ${exit_code} -eq 0 && "${response_status}" =~ ^2 ]]; then
          # Success - return the response
          echo "${response_body}"
          echo "${response_status}"
          return 0
        elif [[ " ${CURL_NON_RETRYABLE_STATUSES[*]} " =~ " ${response_status} " ]]; then
          if [[ "${response_status}" == 403 ]] && is_github_response response_headers; then
            local rate_limit="${response_headers["${RATE_LIMIT_REMAINING_HEADER_KEY}"]}"
            if [[ "${rate_limit}" == "0" ]]; then
              log_warning "Github Request failed with: ${response_status} - ${response_body} with an '${RATE_LIMIT_REMAINING_HEADER_KEY}' value of '0' (can be retried)"
            else
              # There is no X-RateLimit-Remaining header or it is non-zero so assume it is a "normal" non-retryable 403 status not related to rate limits
              log_warning "Github Request failed with: ${response_status} - ${response_body} with an '${RATE_LIMIT_REMAINING_HEADER_KEY}' value of '${rate_limit}' (no point retrying)"
              echo "${response_body}"
              echo "${response_status}"
              return 1
            fi
          else
            log_warning "curl call to ${url} failed with: ${response_status} - ${response_body} (no point retrying)"
            echo "${response_body}"
            echo "${response_status}"
            return 1
          fi
        fi
        log_warning "curl call to ${url} failed with response: ${response_status} - ${response_body} (can be retried)"
      else
        log_warning "curl call to ${url} failed with exit code: ${exit_code} - ${response_body} (can be retried)"
        response_status=500 # emulate Internal Server error
      fi

      local wait_time
      if (( backoff == 0)); then
        wait_time=0 # retry immediately
      else
        local retry_after
        # Was this a 429 Too Many Requests error and we have headers to interrogate?
        # If we get here with a 403, it is because this was a Github response with an X-RateLimit-Remaining of 0, which is a rate limit exceeded error => can retry
        if [[ "${response_status}" == "403" || "${response_status}" == "429" ]]; then
          retry_after=$(get_retry_from_response "${response_status}" response_headers)
        fi
        if [[ -n "${retry_after}" ]]; then
          wait_time="${retry_after}"
          # If we would exceed the maximum wait time then we want to do this one last retry since it is an explicit retry from the API response
          # rather than us retying and praying :)
          if [[ "${wait_time}" -gt "${max_wait}" ]]; then
            max_wait=$((wait_time + 1))  # Ensure we wait at least the time specified
            retry=$((max_retries - 1))   # And force exit after this retry because we will have exceeded the maximum wait time
          fi
        else
          wait_time=$((backoff * (2 ** retry)))
          if (( retry > 1 )); then
            jitter=$((RANDOM % ((wait_time * 33) / 100)))  # Add up to 33% jitter (randomness) to the wait time
            wait_time=$((wait_time + jitter))
          fi
        fi
      fi

      # Exit if maximum wait time is exceeded
      if (( wait_time >= max_wait )); then
          echo "curl failed to obtain a valid response after ${max_wait} seconds from ${url} (exit code: ${exit_code} - ${response_status}: ${response_body}). Please check the server URL and network connection."
          echo "${response_body}"
          echo "${response_status}"
          return $(( exit_code ? exit_code : 1 )) # make sure we return a non-zero exit code - ideally the curl exit code
      fi

      retry=$((retry + 1))
      if (( retry < max_retries + 1 )); then
        if [[ "${raw_response}" != "true" ]]; then # can't log debug messages in "raw" mode
          log_debug "Waiting for ${wait_time} seconds before retry ${retry} of ${max_retries}..."
        fi
        sleep "${wait_time}"
      fi
    done

    message="curl failed to obtain a valid response from ${url} after ${retry} attempts (exit code: ${exit_code} - status: ${response_status}"
    if [[ "${response_body}" != "<empty>" && "${response_body}" != "" ]]; then
      message="${message}, Response: ${response_body}"
    fi
    echo "${message}). Please check the server URL and network connection."
    echo "${response_status}"
    return $(( exit_code ? exit_code : 1 )) # make sure we return a non-zero exit code - ideally the curl exit code
  }

  # makes a curl request with retry and exponential backoff
  # By default this will retry 4 times (ie 5 attempts in total), starting with a 5 second delay and increasing exponentially
  # specify --retry and --retry-delay respectively to control these
  # specify --raw-response if you want the "raw" output and not e.g. cr/lf stripped (the default)
  # Inputs:
  # - The url for the request - this must be the first argument
  # - Any other curl options
  # Returns:
  # The http status code and response body for success; the error message for a failure
  #
  # Example Usage:
  # GET with 2 retries with a 1 second delay before the first retry
  # response=$(curl_with_retry "http://example.com" --retry 2 --retry-delay 1)
  # return_code=$?
  # response_body=$(echo "${response}" | head -n 1)
  # response_status=$(echo "${response}" | tail -n 1)
  # if [[ ${return_code} -eq 0 ]]; then
  #   echo "Response: ${response_status} - ${response_body}"
  # else
  #   echo "Failure: ${return_code} - ${response_body}"
  # fi
  #
  # POST with retry disabled
  # curl_with_retry "https://httpbin.org/post" --request POST --data "Some body" -u "${token}" -H "Accept: application/json" --retry 0
  #
  # Get a raw log file
  # response=$(curl_with_retry "https://myserver.org/logs" -X "GET" -SL --raw-response)
  # logs=$(echo -e "${response}" | head -n -1 || true) # Remove the last line which is the response code
  #
  function curl_with_retry() {
    local url="$1"
    local max_retries=4        # Default number of retries
    local backoff=5            # Default initial backoff time (seconds)
    local max_wait=120         # Default Maximum retry wait time
    local raw_response="false" # Default to NOT get the raw response
    shift 1

    if ! (validate_mandatory_parameter "url" "${url}"); then
      exit 1
    fi

    # See if any of our default values have been overridden
    # If so, extract them and save the others to pass to curl
    local curl_options=()
    while [[ $# -gt 0 ]]; do
        case "$1" in
            --retry)
                max_retries="$2"
                shift 2
                ;;
            --retry-delay)
                backoff="$2"
                shift 2
                ;;
            --retry-max-time)
                max_wait="$2"
                shift 2
                ;;
            --raw-response)
                raw_response="true"
                shift
                ;;
            *)
                curl_options+=("$1")
                shift
                ;;
        esac
    done

    local response
    local response_body
    local response_status
    local return_code

    response=$(__curl_with_retry "${url}" "${max_retries}" "${backoff}" "${max_wait}" "${raw_response}" "${curl_options[@]}")
    return_code=$?
    if [[ "${raw_response}" == "true" ]]; then
      response_body=$(echo "${response}" | head -n -1 || true) # Remove the last line
    else
      response_body=$(echo "${response}" | tail -n 2 | head -n 1 || true) # We want the second last line only, which should be the entire response
    fi
    response_status=$(echo "${response}" | tail -n 1)
    echo "${response_body}"
    echo "${response_status}"
    return "${return_code}"
  }

fi
