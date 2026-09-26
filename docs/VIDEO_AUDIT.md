# Video audit — `assets/kavach-demo-2min.mp4` (review-only, no re-render)

Date: 2026-09-22 (re-verified 2026-09-26). File: 9,854,214 bytes, 96.03s (under 120s limit),
1920x1080, 30fps H.264 + mono AAC 24kHz. Method: `ffprobe` + 11 frames
(1 per 10s, `/tmp/opencode/kavach_frames/f_001..011.png`) + caption bars
read verbatim + narration source `scripts/render_demo_video.py` SCENES.

## Act-by-act (matches `DEMO_2MIN_WINNABLE.md`)

| Time | Frame | What is shown | Verdict |
|------|-------|---------------|---------|
| 0–10s Act 1 hook | f_001, f_002 | Split Senior `Namaste / shield live` + Guardian `Safety 94 / 2 of 3 seats / Dad ACTIVE / Mom 1 ALERT`. Caption = $10B + two-sided + RevenueCat family model | Passes under limit. $10B now attributed in README (FBI IC3 US estimate). Battery 82%, Safety 94 are mock values — acceptable for rendered walkthrough, now labeled as such in README |
| 10–30s Act 2 roles | f_003 | `RoleSelectionActivity` router (Senior vs Guardian) + Senior advisor demo `RUKO! Never Share OTP`, flags OTP +3 / urgency +3 / police +2 | Matches `RoleSelectionActivity.kt` + `RuleEngine` weights. Caption matches narration verbatim |
| 30–50s Act 3 E2E | f_004, f_005, f_006 | `ECIES P-256 SESSION ACTIVE / Epoch #3`, SAS `🛡️⚡🌊🦅🌲🔑`, Keystore AES-256-GCM note, QR `PAIRING CODE: 9B4F2A`, `PARENT SEALED` | Crypto labels match `ShieldCrypto.kt` / `SasFingerprint.kt`. QR is a mock checkerboard (not a real QR) — do not present as scannable |
| 50–75s Act 4 ScamLab | f_007, f_008 | `SIMULATE LIVE ATTACK`, `Verdict SCAM 95% / Senior 100% QUIET / sha256(hid+num)`, E2E inbox with masked OTP `******`, `Block Sender Hash`, `PROTECTED` | Core honest claim. Hash-only + masked OTP matches `mobile.py` + `SmsHandler`. 95% is illustrative (rules give 0.65–0.95) |
| 75–95s Act 5 RevenueCat | f_009, f_010 | `Family Guardian Annual $79.99/yr / $6.67/mo / 3 parents`, `Pro Caregiver $4.99/mo`, `SHIPATON-JUDGE → PRO FAMILY SHIELD ACTIVE` | Matches `PaywallActivity` + `mobile_api.py` webhook TEST MODE. Prices are test-mode placeholders — fine as labeled |
| 95–96s Act 6 close | f_011 | `Encrypted Whisper / Remote Siren / Zero-Knowledge Blind Relay`, `Built by Krishiv Joshi (Age 13) Vadodara`, `61/61 Passed` | Close matches code (consent-gated commands, blind relay). Test count now 61 — matches `pytest` today |

## Audio

No whisper binary on host, so no independent STT. Audio is `edge-tts`
of the 6 `SCENES[].narration` strings by construction (`ensure_audio`);
caption bars in all 11 frames match those strings verbatim. No drift found.

## Issues fixed in this pass (de-vibe, review-only video)

- `scripts/render_demo_video.py`: repo-relative `Path(__file__)` dirs
  (`KAVACH_ASSETS_DIR` / `KAVACH_RENDER_DIR` / `KAVACH_AUDIO_DIR` overrides),
  `logging` instead of `print`, dropped `GOD-TIER` / party-popper copy,
  optional `KAVACH_ARTIFACT_VIDEO` copy instead of hardcoded
  `/home/k/.gemini/...` path.
- `scripts/robo/spark_robo.py`: `tempfile.gettempdir()` stop/log files.
- `README.md`: $10B attributed to FBI IC3 US estimates; demo labeled as
  rendered walkthrough (96s, mock UI + TTS), not live capture.

## Verification

- `pytest -q`: 61 passed.
- `ruff` on touched scripts: only pre-existing EXE001/FURB122/BLE001/RUF100 remain.
- Video untouched (review-only): duration still 96.03s.
