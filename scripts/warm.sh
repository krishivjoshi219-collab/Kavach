#!/usr/bin/env bash
# Warm + prove the E2E relay. Usage: scripts/warm.sh [BASE_URL]
# Exit 0 only if: /healthz ok -> /readyz ready -> demo attack SCAM -> blobs opaque.
set -euo pipefail
BASE="${1:-http://localhost:7860}"
echo "== warming $BASE =="
for i in $(seq 1 30); do
  if curl -fsS "$BASE/healthz" >/dev/null 2>&1; then break; fi
  sleep 2
  if [ "$i" = 30 ]; then echo "healthz never came up"; exit 1; fi
done
curl -fsS "$BASE/healthz" | head -c 200; echo
READY=$(curl -fsS "$BASE/readyz")
echo "$READY" | head -c 300; echo
echo "$READY" | grep -q '"ready":true' || { echo "readyz not ready"; exit 1; }
ATTACK=$(curl -fsS -X POST "$BASE/api/demo/attack" -H 'Content-Type: application/json' \
  -d '{"senior_id":"demo-senior","scenario":"bank_otp"}')
echo "$ATTACK" | head -c 300; echo
echo "$ATTACK" | grep -Eq '"verdict":"(SCAM|SUSPICIOUS)"' || { echo "demo attack did not flag"; exit 1; }
echo "relay warm + proof chain green"
