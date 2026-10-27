#!/usr/bin/env sh
set -eu

base_url="${BASE_URL:-http://localhost:8080}"
temporary_file="$(mktemp)"
trap 'rm -f "$temporary_file"' EXIT

status="$(curl --silent --output "$temporary_file" --write-out "%{http_code}" \
    --request POST "${base_url}/api/users/query" \
    --header "Content-Type: application/json" \
    --data '{"query":"security check"}')"

if [ "$status" != "401" ]; then
    echo "FAIL: protected query returned HTTP ${status}; expected 401."
    exit 1
fi

headers="$(curl --silent --head "${base_url}/api/health")"
echo "$headers" | grep -qi "x-content-type-options: nosniff" || {
    echo "FAIL: X-Content-Type-Options header was not found."
    exit 1
}

echo "PASS: unauthenticated access was rejected and security headers are active."
