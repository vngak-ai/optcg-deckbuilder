#!/bin/sh
# Post-deployment smoke test for the OPTCG Deck Builder.
# Usage: sh scripts/smoke-test.sh http://host.docker.internal:3001
set -e
BASE_URL="$1"
echo "Smoke testing $BASE_URL"

i=0
until curl -fsS "$BASE_URL/health" > /dev/null; do
  i=$((i + 1))
  if [ "$i" -ge 15 ]; then
    echo "FAIL: $BASE_URL/health not reachable"
    exit 1
  fi
  sleep 2
done
curl -fsS "$BASE_URL/health"; echo

STATUS=$(curl -s -o /dev/null -w "%{http_code}" "$BASE_URL/")
[ "$STATUS" = "200" ] || { echo "FAIL: GET / returned $STATUS"; exit 1; }

CARD_COUNT=$(curl -fsS "$BASE_URL/api/cards" | grep -o '"code"' | wc -l)
[ "$CARD_COUNT" -gt 0 ] || { echo "FAIL: /api/cards returned no cards"; exit 1; }

curl -fsS "$BASE_URL/metrics" | grep -q optcg_http_requests_total

echo "PASS: all smoke tests passed for $BASE_URL ($CARD_COUNT cards loaded)"
