#!/usr/bin/env bash
# Next Gen pre-submission gate. Usage: scripts/nextgen_verify.sh [BASE_URL]
# Fails loudly on anything a judge would flag: proof endpoint, demo loop,
# block-case relay mutation, 1024 icon, 1179x2556 screenshot, LICENSE, pack.
set -euo pipefail
BASE="${1:-http://localhost:7860}"
fail() { echo "NEXTGEN-FAIL: $1"; exit 1; }
ok() { echo "ok: $1"; }

curl -fsS "$BASE/api/nextgen/proof" > /tmp/ng_proof.json || fail "proof endpoint unreachable"
python3 - > /tmp/ng_check.txt <<'PY' || fail "proof shape invalid"
import json
p = json.load(open("/tmp/ng_proof.json"))
assert p["track"] == "Next Gen", "track"
rc = p["revenuecat"]
assert "SHIPATON-JUDGE" in rc["judge_promo"], "promo"
assert "shield_protection" in rc["entitlements"], "entitlement"
assert p["repo"]["license_mit"], "LICENSE missing"
assert p["repo"]["submission_pack"], "docs/SUBMISSION_NEXTGEN.md missing"
assert p["repo"]["icon_1024"], "icon-1024.png missing"
assert p["repo"]["screenshot_1179x2556"], "screenshot missing"
print("proof json green")
PY
ok "$(cat /tmp/ng_check.txt)"

ATTACK=$(curl -fsS -X POST "$BASE/api/demo/attack" -H 'Content-Type: application/json' \
  -d '{"senior_id":"nextgen-verify","scenario":"bank_otp"}')
echo "$ATTACK" | grep -Eq '"verdict":"(SCAM|SUSPICIOUS)"' || fail "demo attack did not flag"
IID=$(echo "$ATTACK" | python3 -c "import json,sys; print(json.load(sys.stdin)['incident_id'])")
BLOCK=$(curl -fsS -X POST "$BASE/api/family/block-case" -H 'Content-Type: application/json' \
  -d "{\"senior_id\":\"nextgen-verify\",\"incident_id\":$IID}")
echo "$BLOCK" | grep -q '"ok":true' || fail "block-case not a real mutation"
ok "demo attack $IID flagged + block-case mutation green"

python3 - <<'PY' || fail "asset dimensions wrong"
from PIL import Image
try:
    im = Image.open("assets/icon-1024.png"); assert im.size == (1024, 1024), im.size
    sh = Image.open("assets/screenshot-1179x2556.png"); assert sh.size == (1179, 2556), sh.size
    print("assets 1024 + 1179x2556 exact")
except ImportError:
    import struct
    def png_size(p):
        with open(p, "rb") as f:
            d = f.read(33)
            return struct.unpack(">II", d[16:24])
    assert png_size("assets/icon-1024.png") == (1024, 1024), "icon size"
    assert png_size("assets/screenshot-1179x2556.png") == (1179, 2556), "screenshot size"
    print("assets 1024 + 1179x2556 exact (stdlib)")
PY
ok "assets exact"
test -f LICENSE || fail "LICENSE missing at root"
test -f docs/SUBMISSION_NEXTGEN.md || fail "submission pack missing"
echo "NEXT GEN VERIFY GREEN — safe to submit (consent form + .edu email still on you)"
