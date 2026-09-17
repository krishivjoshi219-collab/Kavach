# Kavach: Remaining Killer Features, Monetization, Sponsor Strategy, and Build Plan

**Product thesis:** Kavach helps an older adult pause a suspicious interaction, verify it independently, and involve a trusted person—without surrendering autonomy or exposing private conversations.

**Winning demo narrative:**

> A caller impersonates law enforcement and pressures a senior to transfer money. The senior opens Kavach, activates a legal pause card, finds an independently sourced verification channel, and requests help. Their family sees a minimal, verified activity update—not a recording or transcript. On a Galaxy Fold, both roles are demonstrated side by side. The next day, a respectful check-in closes the loop.

This connects the features into one coherent product rather than four disconnected demos.

## Assumptions and competition-verification gates

- I do not have your previous Section 1 or Feature 2.1 implementation. I assume **Family Proof** already provides authenticated family pairing and out-of-band challenge-response.
- Your pricing and award figures contain formatting gaps: `0,000`, `bash`, `.99/mo`, and `9/yr`. Below, I use **Free**, **$2.99/month Pro**, and **$4.99/month or $39/year Family** as explicit working assumptions—not recovered facts.
- Treat all award names, amounts, SDK requirements, and eligibility conditions as **unverified until checked against the current Shipaton 2026 rules**. In particular, confirm whether an award requires a specific API, native SDK, published app, transaction volume, or entrant eligibility.
- Architecture below assumes **Android-first Kotlin + Jetpack Compose**, with a web acquisition funnel and a TypeScript backend. If Kavach already has another mobile stack, preserve it unless a native foldable module is genuinely necessary.

---

# 2.2 — Instant “Digital Arrest” & Legal Defuser

## A. Product promise

**“Pause the pressure. Verify independently. Bring in someone you trust.”**

Do not market this as automated legal advice, an official government service, or a guarantee that a caller is fraudulent.

Its purpose is to interrupt the high-pressure sequence commonly used in impersonation scams:

```text
Claim of authority
    → manufactured urgency
    → isolation from family
    → demand for secrecy
    → demand for money, credentials, or remote access
```

Kavach inserts a safe alternative:

```text
Pause
    → end the suspicious interaction
    → locate an independent verification channel
    → ask a trusted person for help
    → record only essential facts
```

## B. Senior interaction: three primary controls

Home screen:

1. **“Someone is pressuring me”**
2. **“Help me verify this”**
3. **“Ask my trusted person”**

Requirements:

- Minimum 64 dp primary touch targets; 72–88 dp where layout permits.
- At least 20 sp primary body text, scalable to system font settings.
- Icons accompanied by explicit text.
- No red warning wall on launch.
- No countdown implying the user must act quickly.
- Haptics and spoken guidance optional.
- No dependency on microphone, contacts, accessibility-service, or call-log permission.

**Android limitation:** Kavach cannot assume it can end an arbitrary cellular call or detect its content. Say **“Hang up using your phone’s call controls”**, not “Kavach has disconnected the scammer.”

### Entry flow

```text
Someone is pressuring me
    ↓
Who do they claim to represent?
    ├── Police / court / government
    ├── Bank / payment service
    ├── Delivery / customs
    └── Something else
    ↓
Pause card
    ├── Read aloud locally
    ├── Show verified contact options
    └── Ask trusted person
```

Do not require category selection if the user needs immediate help. The generic pause card must be one tap away.

---

## C. Pre-drafted legal pause card

### Default card

> **You can pause this conversation.**  
> Do not send money, share an OTP or PIN, install remote-access software, or screen-share financial information because someone is pressuring you.  
>  
> You can say:  
> **“I will verify this independently using an official contact channel. I will not make a payment or share credentials during this call.”**  
>  
> End the interaction if you feel unsafe doing so otherwise, and contact someone you trust. If there is immediate physical danger, use local emergency services.

A shorter large-type version:

> **Pause. Do not pay. Do not share codes.**  
> **Verify through a contact you find yourself.**

### India-specific digital-arrest module

Suggested copy, subject to legal/content review:

> Indian authorities have warned about scams described as “digital arrest.” A demand to remain on a video call, keep the interaction secret, or transfer money to a “safe account” is a serious warning sign. Verify any claimed official process independently.

Do not assert that every genuine investigation follows a single procedure. Do not declare a notice invalid solely because it arrived electronically.

### Legal-content architecture

Use reviewed deterministic content, not an LLM generating legal claims during an emergency.

```kotlin
data class PauseCard(
    val id: String,
    val jurisdiction: String,
    val language: String,
    val version: Int,
    val title: String,
    val immediateActions: List<String>,
    val script: String,
    val limitations: String,
    val sourceIds: List<String>,
    val reviewedAt: Instant,
    val reviewDueAt: Instant
)
```

Include:

- Jurisdiction.
- Language.
- Source references.
- Review date.
- Content version.
- Clear disclaimer that the card is general safety information.

**Offline requirement:** Ship a reviewed baseline pack inside the app. Remote updates can replace it only after signature verification.

---

## D. Official registry lookup: implement an honest directory

Do not imply Kavach has access to a universal police-officer database or can authenticate an officer by badge number. Such access may not exist.

Instead build an **Official Contact Directory**:

- Official institution website.
- Official customer-care or fraud-reporting page.
- Jurisdiction-specific reporting portal.
- Institution name and region.
- Source URL.
- Date verified.
- Explicit limits of what the entry establishes.

### Three separate labels

| Label | Meaning |
|---|---|
| Official source | The entry points to a reviewed official institution source |
| Contact listed | A contact method appears on that source |
| Caller not authenticated | The directory does not establish who placed the incoming call |

Never turn a phone-number match into “Caller verified.” Caller ID can be spoofed.

### Recommended verification flow

1. Select institution.
2. Show official domain prominently.
3. Explain: **“Use this independently sourced channel—not a number or link the caller sent.”**
4. Open the official contact page or initiate a user-confirmed call.
5. Ask: **“Would you like your trusted person to help?”**

For banks, also recommend using the contact channel inside the bank’s official app or on the physical card.

### Directory schema

```sql
official_directory_entries (
  id uuid primary key,
  jurisdiction text not null,
  category text not null,
  institution_name text not null,
  official_domain text not null,
  contact_page_url text not null,
  display_phone text,
  source_url text not null,
  verified_at timestamptz not null,
  review_due_at timestamptz not null,
  status text not null,
  content_version integer not null
);
```

### Security controls

- No arbitrary server-side URL fetching from user input.
- Admin-only directory writes.
- Reviewer identity and change history.
- Domain allowlist with careful redirect handling.
- Link text must show the destination domain.
- Cached entries visibly marked with verification date.
- Expired entries remain usable as reference where appropriate, but lose any freshness claim.

**MVP scope:** Curate 15–25 high-value institution and reporting entries for one jurisdiction. Coverage quality beats a fake global registry.

---

## E. Incident packet without surveillance

When the senior selects “Ask my trusted person,” create an incident:

```json
{
  "incidentId": "uuid",
  "category": "government_impersonation",
  "status": "assistance_requested",
  "createdAt": "server_timestamp",
  "sharedFields": [
    "category",
    "requested_help_at",
    "selected_institution"
  ]
}
```

Default exclusions:

- Call audio.
- Message contents.
- Screen captures.
- Location.
- Banking details.
- OTPs.
- Other installed-app activity.

Optional notes are encrypted and deliberately entered by the user.

### Measurable success

- Time to pause card: **under 2 seconds from home**, excluding app cold start.
- Offline pause-card availability: **100% of supported baseline content**.
- Percentage reaching an independent contact channel.
- Percentage requesting trusted help.
- User-reported confidence after resolution.

Avoid “money saved” claims unless backed by a credible measurement method.

---

# 2.3 — Samsung Galaxy Z Fold “Guardian Cockpit”

## A. Product promise

**A fold-aware family safety console—not a stretched phone screen.**

On an unfolded Galaxy Z Fold, the large inner display can show **two panes**. That is different from promising simultaneous independent rendering on the inner and cover displays.

Build around actual window size, posture, and folding features—not Samsung model-name detection.

## B. Layout model

### Expanded, authenticated joint session

```text
┌──────────────────────────────┬──────────────────────────────────┐
│ SENIOR CONTROLS               │ GUARDIAN COCKPIT                 │
│                              │                                  │
│ “You are in control.”         │ Family Proof status              │
│                              │ ✓ Paired device confirmed        │
│ [ Someone is pressuring me ]  │                                  │
│                              │ Current assistance request       │
│ [ Help me verify this ]       │ Government impersonation concern │
│                              │                                  │
│ [ Ask my trusted person ]     │ Minimal activity timeline        │
│                              │ 10:42 Pause card opened           │
│ [ I’m okay for now ]          │ 10:43 Help requested              │
│                              │ 10:44 Trusted person acknowledged │
└──────────────────────────────┴──────────────────────────────────┘
```

### Compact window / cover screen

Use a single pane with simple navigation:

- Help.
- Check-in.
- Family.

Senior controls remain the default for the senior role.

### Tabletop posture

Where the device reports a suitable horizontal fold:

- Upper region: guidance and assistance status.
- Lower region: large actions.
- Avoid placing important content across the fold/occlusion area.

### Multi-window

The app must remain usable in narrow split-screen windows. Folding-device ownership does not imply an expanded app window.

---

## C. Critical authorization boundary

**Screen width must never grant access.**

The right pane contains only information the current session is authorized to view.

Support three modes:

| Session | Right-pane content |
|---|---|
| Senior only | Their own shared activity and consent controls |
| Caregiver | Activity shared with that caregiver |
| Joint demonstration / co-present session | Additional family view after explicit authentication and consent |

Do not show private caregiver notes merely because a senior unfolds the device.

### Joint session flow

```text
Open cockpit
    → “Show family view?”
    → authenticate authorized caregiver or approve scoped session
    → display exactly what will be visible
    → start short-lived joint session
    → auto-expire / manually close
```

A biometric prompt alone proves access to the device, not that the person is a separately authorized family member. Bind elevated family access to the correct account or approved session.

---

## D. Android implementation

Use:

- Jetpack Compose.
- Material 3 adaptive components appropriate to the pinned library version.
- Jetpack WindowManager.
- Window size classes.
- `FoldingFeature` posture and occlusion information.
- `ViewModel` + `SavedStateHandle`.
- Kotlin `StateFlow`.
- Room for local incident state and encrypted payload storage.
- Navigation that preserves selected incident across size changes.

Conceptual state:

```kotlin
data class CockpitUiState(
    val seniorPanel: SeniorPanelState,
    val guardianPanel: GuardianPanelState?,
    val layout: CockpitLayout,
    val access: CockpitAccess,
    val selectedIncidentId: String?,
    val connectionStatus: ConnectionStatus
)

enum class CockpitLayout {
    SINGLE_PANE,
    SIDE_BY_SIDE,
    TABLETOP
}
```

Important details:

- Fold/unfold must not issue duplicate assistance requests.
- Hoist state above layout-specific composables.
- Use server-generated request IDs and client idempotency keys.
- Respect font scaling and TalkBack traversal order.
- Separate semantics for each pane.
- No drag-only interaction.
- No reliance on color to distinguish verified, pending, or failed states.
- Redact sensitive content from task-switcher previews where supported; assess screenshot restrictions against accessibility and support needs.

---

## E. Encrypted, tamper-evident audit log

Separate **workflow metadata** from **private content**.

### Server-readable metadata

Necessary for scheduling and authorization:

- Household ID.
- Event type.
- Incident ID.
- Timestamp.
- Acknowledgment state.
- Authorized recipients.

### End-to-end encrypted content

- User-written incident notes.
- Sensitive family annotations.
- Optional attachments, if implemented.

Use vetted cryptographic libraries and established primitives. Do not invent encryption algorithms.

A workable MVP design:

1. Each device generates an encryption keypair.
2. Public keys are bound to authenticated device identities.
3. Family Proof authenticates the pairing and key-binding step.
4. Each private event receives a random content-encryption key.
5. Encrypt content using a vetted AEAD implementation.
6. Wrap the content key for each authorized recipient device.
7. Sign the canonical event envelope with the author device key.
8. Include a per-author sequence number and previous-event hash.

```json
{
  "eventId": "uuid",
  "householdId": "uuid",
  "incidentId": "uuid",
  "authorDeviceId": "uuid",
  "authorSequence": 12,
  "previousAuthorEventHash": "base64",
  "ciphertext": "base64",
  "nonce": "base64",
  "recipientKeyEnvelopes": [],
  "signature": "base64",
  "schemaVersion": 1
}
```

Be precise about guarantees:

- Encryption protects payload confidentiality.
- Signatures authenticate events relative to trusted device keys.
- Hash chains help detect modification, ordering problems, and certain missing events.
- They do **not** automatically prove complete history or prevent a malicious server from hiding an entire tail of events.
- Trusted checkpoints or cross-device reconciliation are needed for stronger completeness guarantees.

### Key lifecycle

For the hackathon:

- Support two-device pairing first.
- Require an existing trusted device to authorize a new recipient device.
- Explain that device loss without recovery may make old private notes unavailable.
- Rotate keys on member removal for future data.
- Do not promise revocation of information already decrypted or copied.

**Scope discipline:** Avoid group-key complexity and encrypted attachments until the two-device path is reliable.

---

## F. Galaxy judging proof

Show—not merely claim:

1. Start on the cover display.
2. Open a pause card.
3. Unfold.
4. Controls reorganize into the cockpit without losing the incident.
5. Increase system font size.
6. Rotate or enter multi-window.
7. Show role-gated family content.
8. Refold while an acknowledgment arrives.
9. Confirm the assistance request was created exactly once.

Target **a 45–60 second uninterrupted device recording**.

---

# 2.4 — Dignity-Preserving Daily Check-in & Caregiver Escalation

## A. Product promise

**“A small daily connection, on your terms.”**

Avoid “elder monitoring,” “compliance,” and “failure to respond.”

The senior chooses:

- Whether to participate.
- Preferred time and time zone.
- Reminder frequency.
- Grace period.
- Who can be notified.
- Quiet days.
- Temporary pause.
- Whether a gentle streak is shown.

## B. Daily interaction

Notification:

> **A quick hello from Kavach**  
> Would you like to let your circle know how today is going?

App controls:

- **“I’m okay today”**
- **“Please call when you can”**
- **“I need help now”**

Secondary action:

- **“Not today—pause reminders”**

No public leaderboard. No punitive broken streak. No guilt-inducing messages to family.

### Positive reinforcement

> “Thanks. Your check-in has been shared with the people you selected.”

If the user has opted out of sharing:

> “Done. Your check-in is saved privately.”

---

## C. Authoritative state machine

```text
SCHEDULED
    ↓ due
OPEN
    ├── user confirms okay → COMPLETED
    ├── user requests call → CONTACT_REQUESTED
    ├── user requests help → HELP_REQUESTED
    ├── user pauses        → PAUSED
    └── grace expires      → REMINDER_DUE
                                  ↓
                             REMINDER_SENT
                                  ├── response → resolved
                                  └── grace expires
                                         ↓
                                  ESCALATION_DUE
                                         ↓
                               CAREGIVER_NOTIFIED
                                         ├── acknowledgment
                                         ├── senior response
                                         └── optional backup escalation
```

**No-response is not an emergency diagnosis.**

Caregiver copy:

> “Asha hasn’t checked in during the agreed window. Their phone may be unavailable. Would you like to check in with them?”

Never:

> “Asha may be in danger. Upgrade now.”

### Default escalation policy

Example—not universal:

- Due time: user-selected.
- First grace period: 60 minutes.
- One gentle senior reminder.
- Second grace period: 60 minutes.
- Notify primary caregiver if permission remains active.
- Optional backup caregiver after another user-agreed interval.
- Maximum escalation count per instance.
- Immediate suppression once resolved, paused, or consent revoked.

Do not automatically contact police or emergency services because a check-in was missed.

---

## D. Reliable scheduling architecture

Push is a delivery channel, not the system of record.

Use:

- Server-managed check-in instances.
- Durable scheduled jobs.
- Transactional outbox.
- Idempotent sends.
- Push through OneSignal.
- Optional local reminder for the senior, with best-effort scheduling.
- In-app reconciliation on every foreground.
- Explicit time-zone and daylight-saving handling.

Android background execution and push delivery are not guaranteed. Do