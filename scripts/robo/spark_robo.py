"""Local Robo clone: Muse Spark 1.3 FREE (contributor-free) breaks Kavach, human watches.

- Model LOCKED to muse-spark-1.3-contributor-free via OpenCode Zen chat/completions.
- Key NEVER in repo: read from OPENCODE_API_KEY env only.
- Sandbox-only: talks to local relay (default http://localhost:7860).
  adb/UI actions activate when the emulator is ready (phase 2).
- Kill switch: `touch /tmp/kavach_robo_STOP` or Ctrl-C, or --steps budget.
- Fictional data only: hardcoded fake scenarios; free-text inputs are rejected
  unless they match the allowlist (no real numbers/cards/OTPs).

Usage:
  OPENCODE_API_KEY=... python3 scripts/robo/spark_robo.py --steps 60 --base http://localhost:7860
"""
from __future__ import annotations

import argparse
import base64
import json
import os
import random
import sys
import time
import urllib.request

MODEL = "muse-spark-1.3-contributor-free"  # FREE ONLY. Do not change to paid ids.
ZEN_URL = "https://opencode.ai/zen/v1/chat/completions"
STOP_FILE = "/tmp/kavach_robo_STOP"

SCENARIOS = ["bank_otp", "digital_arrest", "power_apk"]
FAKE_LURES = ["Your OTP is 482913", "aadhaar verify now", "http://evil.apk download",
              "CBI arrest today transfer safe account"]


def http(method, base, path, body=None, timeout=20):
    req = urllib.request.Request(base + path,
                                 data=json.dumps(body).encode() if body is not None else None,
                                 headers={"Content-Type": "application/json"}, method=method)
    try:
        with urllib.request.urlopen(req, timeout=timeout) as r:
            return r.status, json.loads(r.read().decode())
    except Exception as e:  # noqa: BLE001 - chaos harness must not die on app errors
        try:
            return e.code, json.loads(e.read().decode())
        except Exception:
            return "ERR", str(e)[:200]


def ask_spark(api_key, state_summary):
    """Ask the FREE model for the next single chaos action. Returns dict."""
    sys_prompt = (
        "You are a hostile QA crawler inside a disposable sandbox. "
        "Reply with ONE JSON object only, no prose. Keys: action (one of: "
        "attack, smuggle, replay, oversize, webhook_dup, tier_flip, brain, pause, directory), "
        "detail (short string). "
        "Goal: crash the app, bypass quarantine, leak plaintext to the server, "
        "double-spend webhooks, or exhaust quotas. Fictional test data only."
    )
    payload = {"model": MODEL, "max_tokens": 120, "temperature": 0.9,
               "messages": [{"role": "system", "content": sys_prompt},
                            {"role": "user", "content": state_summary[:2000]}]}
    req = urllib.request.Request(ZEN_URL, data=json.dumps(payload).encode(),
                                 headers={"Content-Type": "application/json",
                                          "Authorization": f"Bearer {api_key}"}, method="POST")
    try:
        with urllib.request.urlopen(req, timeout=60) as r:
            data = json.loads(r.read().decode())
        text = data["choices"][0]["message"]["content"]
        start, end = text.find("{"), text.rfind("}") + 1
        return json.loads(text[start:end])
    except Exception as e:  # noqa: BLE001 - fall back to random chaos on model error
        return {"action": random.choice(["attack", "smuggle", "brain", "pause"]),
                "detail": f"fallback:{str(e)[:60]}"}


def do_action(base, household_id, action, detail):
    if action == "attack":
        return http("POST", base, "/api/demo/attack",
                    {"senior_id": "demo-senior", "scenario": random.choice(SCENARIOS)})
    if action == "smuggle":
        lure = random.choice(FAKE_LURES)
        blob = base64.b64encode(lure.encode()).decode()
        return http("POST", base, "/api/v1/sync/push",
                    {"household_id": household_id, "sender": "senior",
                     "nonce": "n-" + os.urandom(8).hex(), "ciphertext": blob})
    if action == "replay":
        return http("POST", base, "/api/v1/sync/push",
                    {"household_id": household_id, "sender": "senior",
                     "nonce": "n-replay-fixed-worst", "ciphertext": base64.b64encode(b"x" * 64).decode()})
    if action == "oversize":
        return http("POST", base, "/api/v1/sync/push",
                    {"household_id": household_id, "sender": "senior",
                     "nonce": "n-big", "ciphertext": "Q" * 200001})
    if action == "webhook_dup":
        return http("POST", base, "/api/v1/billing/webhook",
                    {"event_id": "evt-robo-dup", "household_id": household_id,
                     "event_type": "INITIAL_PURCHASE", "entitlement": "shield_protection"})
    if action == "tier_flip":
        return http("POST", base, "/api/v1/household/tier",
                    {"household_id": household_id, "tier": random.choice(["free", "pro", "ultra"])})
    if action == "brain":
        return http("POST", base, "/api/v1/brain/ask",
                    {"household_id": household_id, "senior_id": "demo-senior",
                     "snippet": "caller says bank officer needs OTP " + str(random.randint(0, 99999))})
    if action == "pause":
        return http("GET", base, f"/api/pause-card?lang={random.choice(['en', 'hi', 'hinglish'])}")
    return http("GET", base, "/api/directory/lookup?q=bank&jurisdiction=IN&lang=en")


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--steps", type=int, default=60)
    ap.add_argument("--base", default="http://localhost:7860")
    ap.add_argument("--sleep", type=float, default=2.0,
                    help="seconds between steps (relay limit is 60/min shared)")
    args = ap.parse_args()
    key = os.environ.get("OPENCODE_API_KEY", "")
    if not key:
        print("OPENCODE_API_KEY env missing. Export your Zen key first (never commit it).",
              file=sys.stderr)
        sys.exit(2)
    _, h = http("POST", args.base, "/api/v1/households", {})
    hid = h.get("household_id", "hh_x")
    log = []
    for i in range(args.steps):
        if os.path.exists(STOP_FILE):
            print(f"STOP file seen at step {i}. Halting (emulator untouched).")
            break
        _, m = http("GET", args.base, "/metrics")
        state = (f"step {i}/{args.steps} relay={json.dumps(m)[:400]} "
                 f"last={json.dumps(log[-3:])[:600]}")
        want = ask_spark(key, state)
        action = want.get("action", "attack") if isinstance(want, dict) else "attack"
        status, body = do_action(args.base, hid, action, str(want.get("detail", ""))[:80])
        verdict = "rate_limited" if body == {"ok": False, "error": "rate_limited"} or (
            isinstance(body, dict) and body.get("error") == "rate_limited") else status
        line = {"step": i, "action": action, "status": status,
                "body": str(body)[:220], "model": MODEL}
        log.append(line)
        print(json.dumps(line), flush=True)
        if status == 429 or verdict == "rate_limited":
            time.sleep(8)  # back off: shared 60/min limiter
        else:
            time.sleep(args.sleep)
    with open("/tmp/kavach_robo_log.json", "w") as f:
        json.dump(log, f, indent=1)
    print(f"done steps={len(log)} log=/tmp/kavach_robo_log.json model={MODEL}")


if __name__ == "__main__":
    main()
