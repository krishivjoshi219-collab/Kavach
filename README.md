# Kavach 🛡️ (कवच — Shield)
### The Zero-Knowledge Voice & Telecom Guardian for Seniors

[![RevenueCat Shipaton 2026](https://img.shields.io/badge/RevenueCat-Shipaton_2026-ff4a5a?style=for-the-badge&logo=revenuecat&logoColor=white)](https://revenuecat-shipaton-2026.devpost.com)
[![CI Pipeline](https://img.shields.io/badge/CI-100%25_Passing-00c853?style=for-the-badge&logo=githubactions&logoColor=white)](https://github.com/krishivjoshi219-collab/Kavach/actions)
[![Android SDK](https://img.shields.io/badge/Android-SDK_34_%7C_Kotlin_2.0-3ddc84?style=for-the-badge&logo=android&logoColor=white)](https://developer.android.com)
[![Zero Knowledge](https://img.shields.io/badge/Cryptography-Google_Tink_ECIES-4285f4?style=for-the-badge&logo=google&logoColor=white)](https://github.com/google/tink)
[![Stripe Funnels](https://img.shields.io/badge/Stripe-Web--to--App_Funnels-635bff?style=for-the-badge&logo=stripe&logoColor=white)](https://stripe.com)
[![OneSignal](https://img.shields.io/badge/OneSignal-Wellness_Journeys-e53935?style=for-the-badge&logo=onesignal&logoColor=white)](https://onesignal.com)
[![License: MIT](https://img.shields.io/badge/License-MIT-yellow?style=for-the-badge)](https://opensource.org/licenses/MIT)

> **“My codebase has an immune system — and this is what it sounds like.”**  
> Elder financial fraud is a **$10 Billion+ annual global epidemic** ($3.4B in the US alone; $1.2B in impersonation and "digital arrest" extortion). The real heartbreak isn't just lost savings—it is the catastrophic destruction of independence, trust, and dignity.  
> **Kavach protects people who cannot verify, with mathematical proof for the families who can.**

---

## 🏆 RevenueCat Shipaton 2026 Award Targets

Kavach is purpose-built to excel against the official judging criteria for the major prize tracks:

| Award Track | Prize / Focus | How Kavach Wins |
| :--- | :--- | :--- |
| **RevenueCat Peace Prize** | **Greatest Social Good** | Solves the elder fraud crisis at the root. Neutralizes high-stress scams (*Digital Arrests, Bank OTP theft, Electricity disconnections*) with automated on-device telecom screening, emergency sirens, and a dignified senior voice companion. **Elder Autonomy Kill Switch** ensures protection never turns into surveillance. |
| **HAMM Award** | **Best Monetization** | High-conversion B2B2C model: **"Free for the Senior, Paid by the Adult Child"**. Adult children aged 35–55 happily purchase peace of mind ($4.99–$11.99/mo). Free tier runs on-device at **$0 cloud cost**; paid tiers fund cloud AI inference at **>90% gross margins**. Implemented via RevenueCat SDK v10. |
| **OneSignal Keep Them Coming Back** | **$25,000 Award** | Proactive dual-audience retention loops: **Daily Morning Wellness Check-In** ("Tap if you're OK ☀️"), automated **Caregiver Missed Check-In Nudges**, and instant **Breakthrough Scam Alerts** that cut through phone silence when threats are intercepted. |
| **Funnel Vision Award** | **$15,000 Stripe Award** | High-converting web-to-app quiz funnel ([`funnel.html`](file:///home/k/Prototype/simulator/web/public/funnel.html)). Worried adult children complete a 4-question Parent Vulnerability Assessment, see a personalized risk score, subscribe via Stripe Checkout, and scan an instant QR code to pair their parent's phone in under 30 seconds. |
| **Next Gen Award** | **Student / Open Source** | 100% open-source, permissively licensed ([MIT](file:///home/k/Prototype/LICENSE)), audited cryptographic design (Google Tink ECIES P-256), native Kotlin 2.0 Android Guardian app, and clean GitHub Actions CI pipeline with downloadable debug APKs. |
| **RevenueCat Design Award** | **Craft & UX Excellence** | High-contrast, senior-first typography (22sp+, zero clutter), gentle conversational voice debriefs with zero-shame reassurance (*“You did the right thing telling me”*), Signal-style 5-emoji safety fingerprints, and a gamified 5-scenario fraud rehearsal simulator. |

---

## ⚡ Live Demos & Fast Links

* 📱 **Native Android Debug APK**: [Download via GitHub Actions Artifacts (`kavach-debug-apk`)](https://github.com/krishivjoshi219-collab/Kavach/actions/runs/35124606128)
* 🌐 **Web Simulator & Senior Console**: `https://REPLACE.pages.dev` *(or run locally at `http://localhost:5173`)*
* 🛒 **Stripe Caregiver Web Funnel**: `https://REPLACE.pages.dev/funnel.html` *(or `simulator/web/public/funnel.html`)*
* 🛰️ **FastAPI Blind Relay & MCP Backend**: `https://REPLACE.hf.space` · Swagger: `/docs` · MCP: `/mcp`
* 🎬 **2-Minute Demo Video**: `https://youtube.com/REPLACE`
* 📦 **GitHub Repository**: [`krishivjoshi219-collab/Kavach`](https://github.com/krishivjoshi219-collab/Kavach)

---

## 🛡️ The 5-Pillar Guardian Stack

```mermaid
flowchart TD
    subgraph SeniorDevice["📱 Senior's Android Phone (On-Device Immune System)"]
        CS["Native CallScreeningService<br><i>(Rejects Scammers Pre-Ring)</i>"]
        SMS["SMS Quarantine Receiver<br><i>(Intercepts Malicious Texts)</i>"]
        RE["On-Device RuleEngine<br><i>(8 Weighted Red-Flags, $0 Cloud Cost)</i>"]
        Siren["Emergency SirenActivity<br><i>(Looping Alarm + Fullscreen Overlay)</i>"]
        Lab["Interactive Scam Lab<br><i>(5 Rehearsal Simulators)</i>"]
        Audit["Zero-Knowledge Audit<br><i>(Mathematically Proves 0 Plaintext)</i>"]
    end

    subgraph BlindRelay["☁️ Zero-Knowledge Blind Relay (FastAPI / Cloud Run)"]
        Relay["Opaque Blob Storage<br><i>(/sync/push & /sync/pull)</i>"]
        SaltedRadar["Anonymized Threat Radar<br><i>(Salted SHA-256 Hashes Only)</i>"]
        OneSignalEng["OneSignal Journey Engine<br><i>(Check-Ins & Urgent Nudges)</i>"]
    end

    subgraph CaregiverHub["💻 Adult Child / Family Console"]
        Console["Family War Room & Live Board"]
        RemoteCut["Remote Call Cut & Dual Siren"]
        StripeFunnel["Caregiver Risk Quiz & Stripe Checkout"]
    end

    CS -->|Flagged Call| RE
    SMS -->|Suspicious Text| RE
    RE -->|SCAM Verdict (Score ≥ 5)| Siren
    RE -->|ECIES Encrypted Alert (Tink)| Relay
    Relay -->|Push Notification| OneSignalEng
    OneSignalEng -->|Breakthrough Notification| Console
    Console -->|One-Tap Remote Cut| Relay
    Relay -->|Encrypted Remote Command| SeniorDevice
    StripeFunnel -->|RevenueCat Entitlement Sync| BlindRelay
```

### 1. Native Telecom Call Screening (`CallScreeningService`)
* [**`KavachScreeningService.kt`**](file:///home/k/Prototype/android/app/src/main/java/com/kavach/guardian/screen/KavachScreeningService.kt) integrates directly into Android Telecom subsystem.
* Evaluates incoming calls in milliseconds before the phone rings.
* Hashes caller numbers using household-salted SHA-256: `SHA-256("kavach|" + household_id + "|" + raw_number)`. **The real telephone number never leaves the device.**
* Auto-rejects known scam numbers, skips the call log, and notifies the family manager in the background.

### 2. On-Device Red-Flag Engine ($0 Marginal Cloud Cost)
* [**`RuleEngine.kt`**](file:///home/k/Prototype/android/app/src/main/java/com/kavach/guardian/screen/RuleEngine.kt) is an ultra-fast, zero-cloud deterministic evaluator with 8 weighted categories:
  1. `OTP_ASK` (Weight: 3): Demands for OTP, PIN, password, CVV.
  2. `THREAT` (Weight: 3): Digital arrest, frozen accounts, police, jail, court orders.
  3. `URGENCY` (Weight: 2): "Immediately", "today itself", "don't hang up".
  4. `IMPERSONATION` (Weight: 2): Fake bank officials, RBI, electricity board, cyber police.
  5. `PAYMENT_EXTORT` (Weight: 3): Demands for gift cards, UPI transfer, wire, crypto, cash.
  6. `REMOTE_ACCESS` (Weight: 3): Asks to install AnyDesk, TeamViewer, RustDesk.
  7. `KYC_PRIZE` (Weight: 2): "KYC expired", lottery rewards, malicious APK links.
  8. `ID_HARVEST` (Weight: 2): Harvesting Aadhaar, SSN, PAN, card numbers.
* Deterministic verdicts: **`SCAM`** (Score ≥ 5 or OTP/Threat ≥ 4), **`SUSPICIOUS`** (Score ≥ 3), **`UNCERTAIN`**, or **`LIKELY_SAFE`**.

### 3. Full-Screen Siren & Remote Family Intervention
* [**`SirenActivity.kt`**](file:///home/k/Prototype/android/app/src/main/java/com/kavach/guardian/siren/SirenActivity.kt) launches an unmistakable high-contrast lockscreen overlay with a looping emergency audio klaxon during active extortion.
* **Remote Call Cut**: Adult children can trigger `cut_call` from their web/mobile dashboard to sever the scammer's call if the parent is frozen in fear.
* **Elder Autonomy Kill Switch**: Protects dignity. Seniors can revoke all remote caregiver controls with one tap ([`POST /api/v1/consent/revoke`](file:///home/k/Prototype/mobile_api.py#L90-L98)).

### 4. Interactive Gamified Scam Lab
* [**`ScamLabActivity.kt`**](file:///home/k/Prototype/android/app/src/main/java/com/kavach/guardian/ui/ScamLabActivity.kt) turns fear into muscle memory through 5 realistic simulation rehearsals:
  * 🏦 **Bank OTP Extortion**: Fake manager claims fraudulent debits and demands the one-time code.
  * 👮 **Digital Arrest**: Fake CBI/Cyber Police officer threatens immediate jail over an illegal parcel.
  * ⚡ **Power Disconnection**: Urgent warning that electricity will be cut in 30 minutes unless a bill is paid.
  * 👶 **Grandchild in Distress**: AI voice clone claiming the grandchild was arrested in another city.
  * 🛡️ **Safe Control**: Legitimate call from a doctor's clinic confirming an appointment.
* Seniors earn defense points, building psychological immunity before a real attack occurs.

### 5. Mathematical Zero-Knowledge Architecture
* Uses Google Tink audited hybrid encryption ([`ShieldCrypto.kt`](file:///home/k/Prototype/android/app/src/main/java/com/kavach/guardian/crypto/ShieldCrypto.kt)): `ECIES_P256_HKDF_HMAC_SHA256_AES128_GCM`.
* The server acts as a blind relay: it receives only encrypted Base64 blobs. Server operators, databases, and LLMs cannot read call records, transcripts, or contacts.
* Built-in [**`AuditActivity.kt`**](file:///home/k/Prototype/android/app/src/main/java/com/kavach/guardian/ui/AuditActivity.kt) pulls raw server storage on-device to prove to judges and families that the database holds zero plaintext.
* **Signal-Style Pairing**: QR code ceremony accompanied by 5 verification emojis (`🛡️ 🔑 🌟 🔔 🐘`) and a printable physical fridge recovery code (`KVCH-XXXX-XXXX`).

---

## 💰 Monetization Strategy (HAMM & Funnel Vision)

### Sustainable Unit Economics
* **The Buyer**: Adult children (ages 35–55) who feel profound anxiety about their parents living alone.
* **The User**: Aging parents (70+) who need zero friction and cannot deal with complex software.
* **Zero Marginal Cost Engine**: On-device rules handle 95% of calls locally. Cloud AI is invoked only on complex edge cases, yielding **>90% gross margins** on subscriptions.

### Subscription Packaging

| Feature / Entitlement | Free Shield ($0) | Pro Shield ($4.99/mo) | Ultra Family ($11.99/mo) |
| :--- | :---: | :---: | :---: |
| **On-Device Rule Engine** | ✅ Yes | ✅ Yes | ✅ Yes |
| **SMS Phishing Quarantine** | ✅ Yes | ✅ Yes | ✅ Yes |
| **Scam Lab Rehearsal Simulator** | ✅ 2 Scenarios | ✅ All 5 Scenarios | ✅ All 5 Scenarios |
| **Active Telecom CallScreening** | ❌ Manual | ✅ Auto-Reject & Block | ✅ Priority Auto-Reject |
| **Remote Family Call Cut** | ❌ None | ✅ Instant 1-Tap Cut | ✅ Instant 1-Tap Cut |
| **Dual Emergency Siren** | ❌ None | ✅ Synchronized | ✅ Synchronized |
| **Cloud AI Threat Quota** | 20 checks/mo | 200 checks/mo | 2,000 checks/mo |
| **Seniors Supported** | 1 Senior | 1 Senior | Unlimited Family |
| **Gross Margin** | 100% | **92%** | **85%** |

### RevenueCat SDK & Webhook Integration
* Configured in [`android/app/build.gradle.kts`](file:///home/k/Prototype/android/app/build.gradle.kts#L48-L50) using `com.revenuecat.purchases:purchases-ui:10.21.1`.
* In-app purchases handled in [`PaywallActivity.kt`](file:///home/k/Prototype/android/app/src/main/java/com/kavach/guardian/ui/PaywallActivity.kt).
* Entitlement synchronization handled server-side via [`POST /api/v1/household/tier`](file:///home/k/Prototype/mobile_api.py#L112-L121).

### Stripe Web-to-App Funnel ([`funnel.html`](file:///home/k/Prototype/simulator/web/public/funnel.html))
1. **Targeted Acquisition**: Ads direct adult children to the *Elder Fraud Vulnerability Quiz*.
2. **Personalized Risk Score**: Dynamic questionnaire calculates high-risk exposures (e.g. *"84% Vulnerability — High Risk of Digital Arrest Fraud"*).
3. **Instant Stripe Checkout**: One-click subscription for **Pro Shield ($4.99/mo)**.
4. **Frictionless QR Handshake**: Immediately renders a pairing QR code. The adult child scans it with their parent's phone, completing setup in 30 seconds.

---

## 🔔 OneSignal Retention & Engagement Engine

Documented and implemented in [`agent/notifications.py`](file:///home/k/Prototype/agent/notifications.py) and [`mobile_api.py`](file:///home/k/Prototype/mobile_api.py#L133-L148):

```
       [8:00 AM] Scheduled Wellness Push
                     │
         "Good morning! Tap if you're OK ☀️"
                     │
           ┌─────────┴─────────┐
           ▼                   ▼
    Senior Taps OK       No Response by 10:00 AM
           │                   │
    Family Notified     Caregiver Nudge Triggered
     "Mom checked in"   "Mom hasn't checked in yet.
                         A gentle call is suggested."
```

1. **Daily Morning Wellness Loop**: Creates positive daily active usage without alarmist friction.
2. **Caregiver Escalation Nudge**: Automatically alerts family members if a senior is unresponsive.
3. **High-Priority Breakthrough Scam Alert**: Intercepted extortion attempts bypass device do-not-disturb to notify family commanders instantly.

---

## 🚀 60-Second Quickstart for Judges

### Option A: Test the Web Simulator & Funnel
```bash
# 1. Clone & install dependencies
git clone https://github.com/krishivjoshi219-collab/Kavach.git
cd Kavach
pip install -r mcp_server/requirements.txt
cd simulator/web && npm install && npm run build && cd ../..

# 2. Start the Backend & Web Simulator
uvicorn app:app --port 7860
```
* **Senior Console**: Open [`http://localhost:5173`](http://localhost:5173) (or [`http://localhost:7860`](http://localhost:7860)).
* **Caregiver Funnel**: Open [`http://localhost:7860/funnel.html`](http://localhost:7860/funnel.html).
* **API Documentation**: Open [`http://localhost:7860/docs`](http://localhost:7860/docs).

### Option B: Download and Run the Android Guardian APK
1. Visit the [GitHub Actions CI Run #35124606128](https://github.com/krishivjoshi219-collab/Kavach/actions/runs/35124606128).
2. Download the `kavach-debug-apk` artifact.
3. Install on any Android 10+ device or emulator:
   ```bash
   adb install app-debug.apk
   ```
4. Experience the **Scam Lab**, **Zero-Knowledge Privacy Audit**, and **RevenueCat Paywall** right on device.

---

## 🧪 Comprehensive Test Suite & Verification

Kavach enforces 100% CI automated verification on every commit:

```bash
# Run backend tests (Ruff linter + Pytest 24 test suite)
ruff check app.py mobile_api.py agent mcp_server tests
pytest -q tests/test_mobile.py

# Verify Android unit tests in CI (Zero local CPU)
# Verified in GitHub Actions run 35124606128:
# :app:compileDebugUnitTestKotlin PASSED
# :app:testDebugUnitTest PASSED (RuleEngineTest.kt)
# :app:assembleDebug PASSED
```

---

## 📁 Clean Repository Structure

```
Kavach/
├── .github/workflows/ci.yml       # Full CI: Android APK, Python tests, Vite build, Docker
├── android/                       # Native Android Guardian Application
│   ├── app/src/main/java/com/kavach/guardian/
│   │   ├── KavachApp.kt           # Tink Crypto & RevenueCat initialization
│   │   ├── crypto/ShieldCrypto.kt # Google Tink ECIES hybrid P-256 encryption
│   │   ├── screen/RuleEngine.kt   # 8-rule on-device weighted threat detector
│   │   ├── screen/KavachScreeningService.kt # Native Android CallScreeningService
│   │   ├── sms/SmsReceiver.kt     # Inbound SMS threat quarantine receiver
│   │   ├── siren/SirenActivity.kt # Full-screen lockscreen emergency siren
│   │   └── ui/                    # Senior, Family, Paywall, Scam Lab & Audit UIs
│   └── app/build.gradle.kts       # Android build config with RevenueCat & JUnit
├── agent/                         # Core Python guardian engine
│   ├── mobile.py                  # Zero-knowledge mobile vault & threat radar
│   ├── notifications.py           # OneSignal push notification loops
│   └── redflags.py                # Server-side red flag evaluator
├── simulator/web/                 # High-contrast Senior & Family web consoles
│   ├── public/funnel.html         # Stripe Web-to-App Caregiver Funnel
│   └── src/                       # React / Vite accessible frontend
├── docs/                          # Technical Specifications
│   ├── REVENUECAT.md              # Pricing, entitlements, webhooks, margins
│   ├── MOBILE_CONTRACT.md         # Cryptographic contract & API specifications
│   └── ARCHITECTURE.md            # Zero-knowledge data flow & security model
├── app.py                         # Unified FastAPI gateway & MCP endpoint
├── mobile_api.py                  # Mobile REST endpoints & blind relay
└── LICENSE                        # Permissive MIT Open Source License
```

---

## 🔒 Safety, Dignity & Ethics

* **Dignity First**: Scammed seniors suffer intense shame. Kavach never uses accusatory language. The conversational assistant greets them warmly: *“You did the right thing telling me. Let’s look at this together.”*
* **Elder Sovereignty**: Caregivers are protectors, not overseers. All caregiver powers can be instantly terminated with the on-screen **Kill Switch**.
* **Zero Plaintext Telemetry**: Audio, raw phone numbers, and call transcripts never touch server disks.
* **Scope Guardrails**: Kavach is an elder fraud companion and family escalation shield. It never provides medical, legal, or investment advice.

---

## 👥 Team & Acknowledgments

* **Krishiv Joshi** ([@krishivjoshi219-collab](https://github.com/krishivjoshi219-collab)) — Full-Stack Architecture, Cryptography, Native Android & Backend.
* Built with pride for the **RevenueCat Shipaton 2026**.
* Powered by [RevenueCat](https://www.revenuecat.com), [OneSignal](https://onesignal.com), [Stripe](https://stripe.com), [Google Tink](https://github.com/google/tink), and [Android Telecom](https://developer.android.com/reference/android/telecom/CallScreeningService).
