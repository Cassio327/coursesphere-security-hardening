#!/usr/bin/env sh
set -eu

base_url="${BASE_URL:-http://localhost:8080}"
evidence_file="$(mktemp)"
trap 'rm -f "$evidence_file"' EXIT

curl --fail --silent --show-error \
    --retry 15 --retry-delay 1 --retry-all-errors \
    "${base_url}/healthz" > /dev/null

echo "Requesting ${base_url}/api/health eight times:"
request_number=1
while [ "$request_number" -le 8 ]; do
    printf "%s: " "$request_number"
    response="$(curl --fail --silent --show-error "${base_url}/api/health")"
    printf "%s" "$response"
    printf "%s\n" "$response" >> "$evidence_file"
    printf "\n"
    request_number=$((request_number + 1))
done

grep -q '"instance":"backend-1"' "$evidence_file" || {
    echo "FAIL: backend-1 was not observed."
    exit 1
}

grep -q '"instance":"backend-2"' "$evidence_file" || {
    echo "FAIL: backend-2 was not observed."
    exit 1
}

echo "PASS: responses were distributed between backend-1 and backend-2."
