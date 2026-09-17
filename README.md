# Kavach 🛡️ (कवच — Shield)

### Pause pressure. Verify independently. Bring family. *Without uploading calls.*

[![RevenueCat Shipaton 2026](https://img.shields.io/badge/RevenueCat-Shipaton_2026_Next_Gen-ff4a5a?style=for-the-badge)](https://revenuecat-shipaton-2026.devpost.com)
[![CI](https://img.shields.io/badge/CI-31_tests_passing-00c853?style=for-the-badge&logo=githubactions&logoColor=white)](https://github.com/krishivjoshi219-collab/Kavach/actions)
[![Android](https://img.shields.io/badge/Android-SDK_34_Kotlin_2.0-3ddc84?style=for-the-badge&logo=android&logoColor=white)](https://developer.android.com)
[![E2E](https://img.shields.io/badge/E2E-Google_Tink_ECIES_P--256-4285f4?style=for-the-badge&logo=google&logoColor=white)](https://github.com/google/tink)
[![TEST MODE](https://img.shields.io/badge/Next_Gen-TEST_MODE_no_charges-ff9800?style=for-the-badge)](https://revenuecat-shipaton-2026.devpost.com)
[![License: MIT](https://img.shields.io/badge/License-MIT-yellow?style=for-the-badge)](./LICENSE)

> **The call comes at 11:40 AM.** *"Mummy, it's the bank. Your account is frozen. Share the OTP right now, or the police will arrest you today."*
> Your mother panics. She almost shares it.
> **Unless Kavach is on her phone.** The SMS never buzzes. A calm siren rises instead: *"Ruko. OTP mat do."* In 10 seconds, you — at work — read the full decrypted lure, tap **Block**, and when they call back, the phone kills it **before the first ring**. Then you both see the proof: the server holds nothing but noise.
>
> That is Kavach. Not a chatbot that *talks* about scams — a shield that **acts** on them.

Elder fraud is a **$10B+/year global epidemic**. The theft hurts; the shame destroys. Seniors who get scammed stop trusting phones, banks, even family. Kavach exists for one belief: **protection for people who cannot verify, proof for the families who can — with dignity intact, in Hindi, Hinglish, and English.**

Built by a **13-year-old student** for the **RevenueCat Shipaton 2026 — Next Gen Award** (video + open-source code, no store release needed). **TEST MODE throughout: no cards, no charges** — judges unlock Pro with promo `SHIPATON-JUDGE`.

---

## 🎬 Watch it save Asha in 90 seconds

```
0:00  Senior idle. Manager war-room clean. Safety Score 86.
0:15  🔴 Simulated attack: Bank-OTP SMS lands → zero buzz → siren on BOTH phones
0:40  Manager opens the full decrypted text (server sees only noise) → taps Block hash
1:00  Same number calls back → auto-reject PRE-RING, call log clean
1:15  Audit screen: relay dump = ciphertext + hashes. Kill Switch revokes everything.
```

*Demo video (public YouTube/Vimeo, <2 min) linked at submission — script in [`DEMO.md`](./DEMO.md). Prefer reading code? Start at [The 3 killer features](#-the-3-killer-features), then [How the E2E actually works](#-true-e2e-no-theater).*

---

## ⚡ The 3 killer features (acts, not chats)

### K1. 🔴 Live Attack Simulator — senior sitting, spam incoming
One tap in Scam Lab (or the web war-room) fires a Bank-OTP / Digital-Arrest / Power-APK lure through the **same production path** as a real SMS — `SmsHandler → RuleEngine → quarantine → E2E forward → dual siren`. No fake UI. End the round by asking the same number to call: the second call dies pre-ring via the learned block hash.
*Code: `android/.../sms/SmsHandler.kt`, `ui/ScamLabActivity.kt`, `POST /api/demo/attack`.*

### K2. 📥 Quarantine Vault — the inbox scams never reach
Scam SMS are suppressed from notifications, kept in an encrypted on-device vault with OTPs masked (`******`), E2E-forwarded to the manager **only on SCAM/SUSPICIOUS with consent**, and one-tap Block+Report teaches the whole household. Clean messages? Untouched, unbuzzed-about, unforwarded.
*Code: `ui/QuarantineActivity.kt`, `data/LocalStore.kt`, web vault in `FamilyBoard.tsx`.*

### K3. 🏠 Family War-Room + Safety Score — proof, not panic
Pulsing red banner on the latest threat, evidence-chained case file (every verdict cites its red flags), SVG Safety Score that climbs with check-ins and safe weeks, quarantine mirror with masked OTPs. The manager sees **minimum necessary**: verdict + sender-hash + timestamp always, full body only on scam-like with consent.
*Code: `simulator/web/src/components/FamilyBoard.tsx`, `GET /api/family-feed`.*

### Astra-grade depth behind them
* **Family Proof challenge** — verify the *enrolled device*, not the voice/number: `POST /api/family/challenge/create|respond`. Grandchild voice-clone dies here. Copy never claims `caller verified`.
* **Digital-Arrest Defuser** — offline pause cards in EN/HI/Hinglish (`GET /api/pause-card`) + curated 15-entry Official Directory (`GET /api/directory/lookup`, domain + verified date, never authenticates a caller).
* **Dignity check-ins** — `I'm okay / Call me / Need help now`, server-owned state machine, gentle escalation copy. No fear-mongering, no leaderboard shame.

---

## 🔐 True E2E, no theater

```
Senior phone                      Blind relay (FastAPI)              Manager phone
[Tink keypair, Keystore]          [hashes + noise ONLY]              [Tink keypair, Keystore]
  QR pair (code+pubHash) ────────▶ single-use code, 10-min expiry ──▶ fetch senior key
  safety numbers derived BOTH sides (SasFingerprint) — must match or abort
  scam SMS → encrypt(peer pub) ──push blob──▶ store opaque ──pull──▶ decrypt locally
  manager Block ─────────────────hash only ─▶ blocklist ──lookup──▶ pre-ring reject
  Kill Switch ──revoke───────────▶ epoch+1, queued powers wiped ────▶ peer key dropped
```

* Google Tink `ECIES_P256_HKDF_HMAC_SHA256_AES128_GCM` — audited primitives, never home-rolled (`crypto/ShieldCrypto.kt`).
* Server **rejects** plaintext (`otp/aadhaar/http` raw or decoded), short nonces, replayed nonces; blobs capped at 500/household with oldest-pruned; all relay mutations rate-limited (60/min, shared limiter — reads stay open for 8s command polls).
* Numbers travel as `SHA-256("kavach|household|number")` — raw numbers never leave the phone.
* Kill Switch = crypto revocation: epoch bump + peer wipe + queued commands voided. Future sharing stops (already-decrypted copies can't be un-read — the UI says exactly that).
* Prove it yourself: `ui/AuditActivity.kt` pulls the raw relay dump on-device — noise + leak-scanner included.

---

## 💰 Business, not demo-ware (Astra pricing, TEST MODE)

**Free for the Senior. Paid by the Adult Child who worries.**

| | Free Shield $0 | Pro Caregiver $4.99/mo | Family Fortress $9.99/mo · $79/yr |
|---|---|---|---|
| On-device rules, quarantine, Scam Lab | ✅ | ✅ | ✅ |
| Call screening auto-reject, remote cut, dual siren | manual | ✅ | ✅ priority |
| Cloud-brain quota | 20/mo | 200/mo | 2,000/mo |
| Seniors / caregivers | 1 / 1 | 1 / 2 | 2 parents / 6 |
| Check-in history | 7 days | 90 days | 365 days |

* 14-day Pro trial. Judges: promo `SHIPATON-JUDGE` (no card, TEST MODE badge on screen).
* RevenueCat done right: offerings → `purchase(package)` → entitlement `shield_protection`/`pro_caregiver`/`family_fortress` check → server reconcile; `restorePurchases()` always; **webhook is the server authority** (`POST /api/v1/billing/webhook`, Bearer + idempotent receipts + downgrade path). Client `CustomerInfo` is UI hint only. Urgent actions, consent screens, revoke, and export are **never paywalled**.
* Zero-marginal-cost engine: 95% of verdicts never leave the phone — paid tiers fund inference at high contribution margins. Honest math in [`docs/REVENUECAT.md`](./docs/REVENUECAT.md).
* Acquisition: test-mode quiz funnel (`simulator/web/public/funnel.html` → `/funnel.html`) ends at QR pairing. **No Stripe, no charges** — Funnel Vision is out of scope for Next Gen; noted as roadmap.

---

## 🧓 Senior-proof by design (and honest about limits)

* 24sp+ type, 64dp one-thumb buttons, Hindi toggle front-and-center, voice input + replay, `Ruko. Verify karo.` — not warning-wall red on launch.
* Zero-shame language everywhere: *"You did the right thing telling me."*
* What we **don't** claim: no call-audio analysis (screening sees metadata, not conversation), no guaranteed call-cut on arbitrary carriers (we ask seniors to hang up; remote cut is best-effort + siren cover), no SMS deletion without the default-SMS role (we suppress + quarantine + siren), no DND bypass promises, no `caller verified` badges (caller ID spoofs). The code says what it does; the video shows it.

---

## 🚀 Quickstart (local, 60 seconds, $0)

```bash
git clone https://github.com/krishivjoshi219-collab/Kavach.git
cd Kavach
pip install -r mcp_server/requirements.txt
uvicorn app:app --port 7860
# or: docker compose up --build   (1-click parity, no .env needed)
bash scripts/warm.sh http://localhost:7860   # healthz → readyz → SCAM proof
```

* Senior console: `simulator/web` → `npm install && npm run build` (or `npm run dev` → `http://localhost:5173`).
* API docs: `http://localhost:7860/docs` · MCP `/mcp` (spec 2025-11-25) · board `/apps/family-board.html` · funnel `/funnel.html`.
* Android APK: CI artifact `kavach-debug-apk` on every `main` push → `adb install app-debug.apk` (Android 10+). RevenueCat/OneSignal keys empty = full TEST MODE.
* Deploy relay free (no card): Render Free via Dockerfile (`$PORT`-aware) — runbook in [`docs/DEPLOY.md`](./docs/DEPLOY.md). HF Docker now needs PRO — skipped deliberately.

---

## 🧪 31 tests + live warm proof (judges: run this)

```bash
ruff check app.py mobile_api.py agent mcp_server tests
pytest -q
# 31 passed: debrief walks, 10-scam/5-legit eval, pairing+expiry, blind-relay
# plaintext/nonce/size rejects, consent kill-switch + epoch, quota tiers,
# pause/directory/challenge/webhook, relay stats + 500-cap prune, MCP handshake
```

Android `RuleEngineTest` (OTP-threat SCAM, safe-contact clear, salted-hash determinism) runs in CI alongside `assembleDebug`.

---

## 📁 Repository map

```
Kavach/
├── app.py                    # FastAPI: chat, feed, demo-attack, pause, directory,
│                             #   challenges, MCP at /mcp + /mcp/, metrics, funnel
├── mobile_api.py             # /api/v1/* blind relay: pair, blobs, blocklist, consent,
│                             #   commands, tier, webhook, checkin, radar (all limited)
├── agent/                    # ratelimit (shared) · mobile (relay+E2E gate+quotas)
│                             #   models (seniors, cases, alerts, challenges) · redflags
│                             #   (EN+HI, 8 weighted rules) · protocols (governed debrief)
│                             #   kavach_agent (LLM narrates, rules decide) · notifications
├── android/                  # Senior-first native app (Kotlin, SDK 34)
│   └── app/src/main/java/com/kavach/guardian/
│       ├── crypto/ShieldCrypto.kt + SasFingerprint.kt   # Tink ECIES + safety numbers
│       ├── screen/RuleEngine.kt + KavachScreeningService.kt
│       ├── sms/SmsReceiver.kt + SmsHandler.kt           # one path: real + demo
│       ├── siren/SirenActivity.kt                       # Hinglish lockscreen siren
│       └── ui/ Senior, Family war-room, Pairing (QR+SAS), Paywall (real
│           purchase/restore/promo), ScamLab (+live attack), Quarantine,
│           Audit (noise proof), Onboarding, KavachTheme
├── simulator/web/            # Senior shield + Family war-room + vault + score ring
├── data/official_directory.json  # curated verify-independently directory
├── scripts/warm.sh           # warm + proof chain (healthz→readyz→SCAM)
├── docs/                     # REVENUECAT · MOBILE_CONTRACT · ARCHITECTURE · DEPLOY · API
├── assets/                   # icon-1024.png · screenshot-1179x2556.png (Devpost-ready)
├── .github/workflows/ci.yml  # backend + frontend + android APK + docker, every push
└── LICENSE                   # MIT — visible in About
```

---

## 🔒 Safety, dignity & ethics

* Seniors are protectors' partners, not surveillance subjects — every manager power is **lent**, revocable in one tap, epoch-rotated.
* No medical, legal, or investment advice. Pause cards are general safety information with disclaimers, reviewed offline packs.
* Fictional demo household (`Asha`, redacted `+91-98XXX` numbers). Per-senior IDs isolate families. No address-book scraping, no invite spam.

---

## 👥 Built by

**Krishiv Joshi** ([@krishivjoshi219-collab](https://github.com/krishivjoshi219-collab)) — 13-year-old student. Full-stack architecture, cryptography, native Android, backend, and business design — for the **RevenueCat Shipaton 2026 · Next Gen Award**.

*Powered by [RevenueCat](https://www.revenuecat.com) (sandbox/test mode) · [Google Tink](https://github.com/google/tink) · [Android Telecom](https://developer.android.com/reference/android/telecom/CallScreeningService) · [OneSignal](https://onesignal.com) (journeys) · FastAPI · Vite.*

*Kavach is a family escalation aid and fraud companion — not professional, legal, medical, or emergency advice. In danger, contact local emergency services.*
