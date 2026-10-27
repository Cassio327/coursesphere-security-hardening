#!/usr/bin/env sh
set -eu

base_url="${BASE_URL:-http://localhost:8080}"

echo "Requesting ${base_url}/api/health eight times:"
request_number=1
while [ "$request_number" -le 8 ]; do
    printf "%s: " "$request_number"
    curl --fail --silent --show-error "${base_url}/api/health"
    printf "\n"
    request_number=$((request_number + 1))
done

echo "Expected result: responses contain both backend-1 and backend-2."
