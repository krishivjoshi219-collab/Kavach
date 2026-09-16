# Kavach Mobile Contract & Zero-Knowledge Relay Specification

## 1. Zero-Knowledge Threat Model & Architecture

Traditional anti-spam solutions upload contact books and call metadata to central servers, breaking user privacy. **Kavach guarantees zero server-side plaintext access**:

```
Senior Device                         Kavach Blind Relay Server               Family Manager Device
┌───────────────────────┐             ┌─────────────────────────┐             ┌───────────────────────┐
│ Private Keyset (Tink) │             │ Ciphertext Blobs only   │             │ Private Keyset (Tink) │
│ Android Keystore      │             │ Salted Hashes only      │             │ Android Keystore      │
│                       │             │ No plaintexts or audio  │             │                       │
│ 1. Scan Manager QR    │────────────▶│ 2. ECDH Key Agreement   │◀────────────│ 1. Generate QR Code   │
│    (Public Key only)  │             │    Exchange Public Keys │             │    (Public Key only)  │
│                       │             │                         │             │                       │
│ 3. On-Device Screener │             │                         │             │                       │
│    Hash(salt, number) │────────────▶│ Check blocklist hash    │             │                       │
│                       │             │                         │             │                       │
│ 4. Encrypted Alert    │──push blob─▶│ Relay opaque ciphertext ├──pull blob─▶│ Decrypt with Manager  │
│    (Tink Hybrid ECIES)│             │                         │             │ Private Key           │
│                       │             │                         │             │                       │
│ 6. Receive Command    │◀──pull cmd──│ Queue Remote Command    │◀──send cmd──│ 5. "Cut Call" / Siren │
│    Execute via Telecom│             │ (Gated by Dad's Consent)│             │                       │
└───────────────────────┘             └─────────────────────────┘             └───────────────────────┘
```

---

## 2. Cryptographic Protocol (Google Tink)

* **Standard**: ECIES with `P256_HKDF_HMAC_SHA256_AES128_GCM` (`HybridKeyTemplates.ECIES_P256_HKDF_HMAC_SHA256_AES128_GCM`).
* **Storage**: Keysets stored in private app SharedPreferences protected by hardware-backed master key via `AndroidKeystore` (`android-keystore://kavach_master_*`).
* **Relay Payload**:
  * Every incident and message is encrypted on-device with the recipient's public key before network transmission.
  * The server only ever observes opaque Base64 ciphertext strings and arbitrary nonces.
  * Server database dumps show only random cryptographic noise.

---

## 3. Pairing Ceremony & "Fridge Code" Recovery

1. **Manager Display**:
   * Manager initiates pairing: generates ephemeral 6-character code (`/api/v1/pair/init`) and QR code embedding public key.
   * Both screens render a 5-emoji visual checksum (Signal-style SAS fingerprint: 🛡️ 🔑 🌟 🔔 🐘).
2. **Senior Scan/Input**:
   * Senior inputs 6-char code or scans QR; keys exchange via single-use endpoint `/api/v1/pair/complete`.
3. **Fridge Recovery Code**:
   * Generates human-readable recovery code (`KAVACH-FRIDGE-8492-SEAL`) for offline retention on the refrigerator.

---

## 4. Elder Autonomy & The Consent Kill Switch

Every capability granted to the family manager is **lent power**, strictly gated by the senior:

| Capability | Scope |
|---|---|
| `screen_calls` | Allows background call screening & number hash checking |
| `forward_sms` | Allows encrypted forwarding of quarantined scam SMS |
| `remote_cut` | Allows manager to trigger call termination via Telecom API |
| `cloud_brain` | Allows hard-case queries to be sent to Gemini Flash / Groq |
| `share_routines` | Allows routine status syncing to the family board |

**The One-Tap Kill Switch**:
A prominent button in `SeniorActivity` calls `/api/v1/consent/revoke`, immediately nullifying all remote commands and permissions.

---

## 5. Mobile API Endpoints

All endpoints reside under `/api/v1/*`:

* `POST /api/v1/households`: Creates an isolated household ID.
* `POST /api/v1/pair/init`: Registers manager public key and creates 6-char code.
* `POST /api/v1/pair/complete`: Consumes pairing code and exchanges public keys.
* `POST /api/v1/sync/push`: Submits encrypted ciphertext blob (`senior` or `manager`).
* `GET  /api/v1/sync/pull`: Retrieves pending ciphertext blobs by `since_id`.
* `POST /api/v1/screen/lookup`: Lookups salted number hash on blocklist.
* `POST /api/v1/screen/block`: Adds salted number hash to household blocklist.
* `POST /api/v1/consent/set`: Senior configures granted capabilities.
* `POST /api/v1/consent/revoke`: Instant revocation kill switch.
* `POST /api/v1/device/command`: Dispatches consent-gated remote action (`cut_call`, `sound_siren`).
* `GET  /api/v1/device/commands`: Senior device polls pending commands.
* `POST /api/v1/device/commands/{id}/ack`: Acknowledges execution of command.
* `POST /api/v1/brain/ask`: Consent & tier quota-gated cloud inference.
* `POST /api/v1/household/tier`: Updates subscription tier (`free`, `pro`, `ultra`).
