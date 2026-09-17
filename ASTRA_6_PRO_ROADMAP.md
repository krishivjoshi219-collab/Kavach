# 5. OPENCODE IMPLEMENTATION ROADMAP (Actionable File-by-File Blueprint)

**Build objective:** Ship one reliable, demonstrable loop:

> A suspicious demand triggers a pause → a family member verifies through a separate channel → the household receives a check-in → the guardian sees the outcome → RevenueCat manages access to premium coordination features.

**Implementation constraint:** Repository contents, installed SDK versions, and official Shipaton 2026 award rules have not been provided. The paths below are implementation targets—not claims about existing files. Before editing, OpenCode must inspect the repository, preserve its actual Android namespace and framework structure, and confirm SDK APIs against the pinned versions. Treat award snippets as proposed copy, not verified eligibility claims.

---

## 5.1 Execution Order and Repository Rules

### First action: inspect, do not scaffold over existing code

```bash
cd /home/k/Prototype

git status --short
find android -maxdepth 4 -type f \
  \( -name '*gradle*' -o -name 'AndroidManifest.xml' \)
find android -type f \
  \( -name '*.kt' -o -name '*.java' \) | head -100
find simulator/web -maxdepth 2 -type f
sed -n '1,240p' mobile_api.py
sed -n '1,240p' app.py
```

Resolve these placeholders once:

```text
ANDROID_MODULE = actual Android application module; examples below use app
PACKAGE_PATH   = existing namespace with dots replaced by slashes
JAVA_ROOT      = /home/k/Prototype/android/app/src/main/java/<PACKAGE_PATH>
RES_ROOT       = /home/k/Prototype/android/app/src/main/res
```

### Priority order

| Priority | Deliverable | Completion gate |
|---|---|---|
| P0 | Authentication, household authorization, database migrations | Users cannot read or mutate another household |
| P0 | Challenge creation and signed response | Two separate installations complete a challenge |
| P0 | Legal pause card and curated directory | Works without fabricated official results |
| P0 | Check-in scheduling and acknowledgement | Durable timer survives API restart |
| P1 | Guardian dual-pane cockpit | Fold/unfold preserves selection and state |
| P1 | RevenueCat purchase, restore, reconciliation | Sandbox purchase updates server entitlement |
| P1 | Web quiz, simulator, Stripe checkout | Signed webhook—not redirect—grants web entitlement |
| P2 | Demo fixtures, accessibility, submission package | Reproducible two-minute demonstration |

**Non-negotiable scope cuts:** No call interception, voice-clone detection, accessibility-service surveillance, emergency dispatch promises, or automatic contact with police.

---

## 5.2 Kotlin Android App

### A. Build and platform configuration

| File | Action |
|---|---|
| `android/gradle/libs.versions.toml` | Add compatible, pinned dependencies for RevenueCat Android + RevenueCat UI, OneSignal, Retrofit/OkHttp, Kotlin serialization, Room, WorkManager, Lifecycle Compose, and Material 3 adaptive components |
| `android/app/build.gradle.kts` | Enable Compose and serialization as needed; inject public SDK configuration; keep service secrets out of the APK |
| `android/app/src/main/AndroidManifest.xml` | Register activities, notification permission, OneSignal notification extension, and verified deep links where configured |
| `JAVA_ROOT/KavachApplication.kt` | Initialize RevenueCat and OneSignal once; bind them to the authenticated opaque Kavach user ID |
| `JAVA_ROOT/core/network/KavachApi.kt` | Define typed REST requests and responses |
| `JAVA_ROOT/core/network/AuthInterceptor.kt` | Attach short-lived bearer token; never log tokens or payloads |
| `JAVA_ROOT/core/security/DeviceIdentityStore.kt` | Generate non-exportable Android Keystore signing key; register public key with backend |
| `JAVA_ROOT/core/navigation/NotificationRouter.kt` | Validate notification type and UUID; navigate only after authentication |
| `JAVA_ROOT/core/config/DemoMode.kt` | Explicit, visibly labeled fixtures; prohibit fixtures in production API responses |

**SDK rules**

- RevenueCat SDK key is public configuration; RevenueCat secret API key stays server-side.
- Set RevenueCat `appUserID` and OneSignal external ID to the backend-issued opaque user ID.
- Configure OneSignal identity verification if supported by the chosen SDK/account setup.
- On logout, clear household caches, detach push identity, and reset purchase identity appropriately.
- Request notification permission in context, not at first launch.
- No foreground service is required for these features.

---

### B. `FamilyProofService.kt` — out-of-band challenge-response

Create:

```text
JAVA_ROOT/feature/familyproof/
├── FamilyProofService.kt
├── FamilyProofRepository.kt
├── FamilyProofModels.kt
├── FamilyProofViewModel.kt
├── FamilyProofScreen.kt
└── FamilyProofActivity.kt
```

#### Exact classes and models

```kotlin
enum class ChallengeState {
    PENDING, APPROVED, DENIED, EXPIRED, CANCELLED
}

enum class ProofDecision { APPROVE, DENY }

data class CreateChallengeRequest(
    val householdId: String,
    val responderMemberId: String,
    val purposeCode: String
)

data class FamilyChallenge(
    val id: String,
    val householdId: String,
    val initiatorMemberId: String,
    val responderMemberId: String,
    val nonce: String,
    val expiresAt: String,
    val state: ChallengeState
)

data class RespondChallengeRequest(
    val challengeId: String,
    val decision: ProofDecision,
    val deviceKeyId: String,
    val signature: String
)
```

`FamilyProofService` is an injectable application service, **not** an Android background `Service`.

Methods:

```kotlin
suspend fun create(request: CreateChallengeRequest): FamilyChallenge
suspend fun fetch(challengeId: String): FamilyChallenge
suspend fun respond(
    challenge: FamilyChallenge,
    decision: ProofDecision
): FamilyChallenge
```

#### Protocol

1. Backend generates a cryptographically random 32-byte nonce and a five-minute expiration.
2. Challenge names one enrolled responder.
3. Push contains only a challenge ID and generic notification text.
4. Responder opens Kavach, authenticates, and retrieves the challenge.
5. Responder explicitly approves or denies.
6. Device signs this exact UTF-8 message:

```text
kavach.family-proof.v1\n{challenge_id}\n{nonce_base64url}\n{household_id}\n{initiator_member_id}\n{responder_member_id}\n{decision}\n{expires_at_epoch_seconds}
```

Use UUID identifiers, uppercase decision values, Base64URL without padding, and no trailing newline. Use Android Keystore EC P-256 with `SHA256withECDSA`; transport the DER signature as Base64URL.

7. Backend verifies key ownership, signature, membership, expiration, and pending state in one transactional transition.
8. Foreground UI polls status with bounded backoff. Push is a hint, not the source of truth.

#### Composables

- `FamilyProofScreen`
- `TrustedResponderPicker`
- `ChallengePendingCard`
- `IncomingChallengeCard`
- `ProofDecisionButtons`
- `ChallengeResultCard`
- `ChannelIndependenceNotice`

**Required copy:**

> “This confirms a response from an enrolled family device. It does not prove that a caller is genuine. If unsure, end the call and contact your family using a saved number.”

Do not describe a push on the same compromised device as an independent verification channel. Household enrollment must require an authenticated invitation and approval by an existing authorized member.

---

### C. `LegalDefuserActivity.kt` — pause card and directory lookup

Create:

```text
JAVA_ROOT/feature/legal/
├── LegalDefuserActivity.kt
├── LegalDefuserViewModel.kt
├── OfficialDirectoryRepository.kt
├── OfficialDirectoryModels.kt
└── LegalDefuserScreen.kt
```

#### Models

```text
OfficialDirectoryEntry
  id, jurisdiction, agencyName, officeName
  officialWebsite, publishedPhone
  sourceUrl, verifiedAt

DirectoryLookupResult
  entries[], freshnessStatus

LegalDefuserUiState
  jurisdiction, query, loading, results, error
```

#### Composables

- `DigitalArrestPauseCard`
- `ImmediateSafetyActions`
- `JurisdictionSelector`
- `OfficialDirectorySearch`
- `OfficialDirectoryResultCard`
- `SourceAndFreshnessLabel`
- `CallTrustedPersonButton`

#### Behavior

- Pause card renders offline.
- Directory returns curated records only.
- Display source URL and verification date with each result.
- Use `ACTION_DIAL`, not `ACTION_CALL`.
- Open official URLs through a browser/custom tab.
- Never accept a caller-provided URL as an official source.
- A matching agency entry must **not** produce a “caller verified” badge.

**Required copy:**

> “Pause before sending money, sharing codes, or installing software. End the call and independently contact the relevant agency using its published contact details.”

> “Kavach is not legal advice or an emergency service.”

---

### D. `GuardianCockpitActivity.kt` — Galaxy Z Fold adaptive cockpit

Create:

```text
JAVA_ROOT/feature/guardian/
├── GuardianCockpitActivity.kt
├── GuardianCockpitViewModel.kt
├── GuardianRepository.kt
├── GuardianModels.kt
└── GuardianCockpitScreen.kt
```

#### Models

```text
HouseholdOverview
  householdId, members[], pendingChallenges[], activeCheckins[]

GuardianSelection
  Member(memberId) | Challenge(challengeId) | Checkin(checkinId)

GuardianUiState
  overview, selection, loading, error, lastRefreshedAt
```

#### Composables

- `GuardianCockpitScreen`
- `HouseholdListPane`
- `GuardianDetailPane`
- `MemberStatusCard`
- `PendingChallengeCard`
- `CheckinStatusCard`
- `HouseholdTimeline`
- `EntitlementStatusChip`

#### Adaptive implementation

Use Material 3 adaptive `ListDetailPaneScaffold` and its navigator, matching the pinned library’s API.

- Compact width: list → detail navigation.
- Expanded width: list and detail visible together.
- Use posture-aware adaptive information; respect separating hinges.
- Do not hardcode Samsung model detection.
- Persist selected entity ID in `SavedStateHandle`.
- Collect state lifecycle-aware.
- Preserve behavior under multi-window, rotation, font scaling, and fold/unfold.

**Acceptance test:** Select a pending challenge on the cover display, unfold, and confirm that the same challenge remains selected in the detail pane.

---

### E. `PaywallActivity.kt` — RevenueCat Paywalls

Create:

```text
JAVA_ROOT/feature/billing/
├── PaywallActivity.kt
├── BillingRepository.kt
├── BillingModels.kt
├── PaywallViewModel.kt
└── SubscriptionManagementScreen.kt
```

#### RevenueCat configuration contract

```text
Entitlement: household_plus
Offering:    default
Packages:    monthly, annual
Products:    actual Google Play subscription/base-plan mappings
```

Configure the requested Paywalls v2 experience in the RevenueCat dashboard and use a compatible pinned RevenueCat UI SDK. Do not invent a `PaywallsV2` Kotlin API or substitute a hand-coded screen while claiming it is a dashboard-rendered paywall.

#### Classes and composables

- `BillingRepository`
  - `loadOffering()`
  - `refreshCustomerInfo()`
  - `restorePurchases()`
  - `reconcileHouseholdSubscription(householdId)`
- `BillingUiState`
- `HouseholdEntitlement`
- `PaywallHost`
- `SubscriptionManagementScreen`
- `RestorePurchasesAction`

#### Flow

1. Household owner opens the dashboard-configured paywall.
2. RevenueCat handles Google Play purchase.
3. Client refreshes `CustomerInfo`.
4. Client calls backend reconciliation.
5. Backend independently verifies RevenueCat entitlement.
6. Backend maps that entitlement to the authorized household.
7. Webhooks maintain the grant over renewals, expiration, and refunds.

**Free safety baseline:** Pause card, directory lookup, basic challenge response, and check-in acknowledgement stay available without purchase. Premium can unlock additional coordination capacity and household history.

Use Play billing in the Android app. Keep Stripe checkout on the standalone web funnel unless the applicable store policy explicitly permits another arrangement.

---

### F. `CheckinActivity.kt` and OneSignal receiver

Create:

```text
JAVA_ROOT/feature/checkin/
├── CheckinActivity.kt
├── CheckinViewModel.kt
├── CheckinRepository.kt
├── CheckinModels.kt
└── CheckinScreen.kt

JAVA_ROOT/core/notifications/
├── KavachNotificationServiceExtension.kt
└── KavachNotificationClickListener.kt
```

#### Models

```text
Checkin
  id, householdId, subjectMemberId, dueAt
  graceSeconds, state, acknowledgedAt, escalationQueuedAt

CheckinState
  SCHEDULED | ACKNOWLEDGED | OVERDUE | CANCELLED

ScheduleCheckinRequest
  householdId, subjectMemberId, dueAt, graceSeconds

AcknowledgeCheckinRequest
  checkinId
```

#### Composables

- `CheckinScheduleForm`
- `PendingCheckinCard`
- `AcknowledgeCheckinButton`
- `CheckinAcknowledgedCard`
- `NotificationPermissionRationale`

Use the OneSignal notification service extension and click listener supported by the pinned SDK—not a fabricated generic broadcast receiver.

**Rules**

- Server owns scheduling and escalation.
- OneSignal notification delivery is best-effort.
- Opening a notification does not acknowledge a check-in.
- An explicit authenticated button press acknowledges it.
- Late acknowledgement remains possible and records that it occurred after the deadline.
- Notification text omits sensitive household details.

---

## 5.3 FastAPI Backend and Blind Relay

### A. File map

Under `/home/k/Prototype/`:

```text
mobile_api.py                         UPDATE: mount /api/v1 routers once
app.py                                UPDATE: integrate existing web entrypoint
kavach_api/
├── auth.py                           CREATE
├── database.py                       CREATE
├── models.py                         CREATE
├── schemas.py                        CREATE
├── settings.py                       CREATE
├── routers/
│   ├── family.py
│   ├── official_directory.py
│   ├── household.py
│   ├── checkin.py
│   ├── layers.py
│   └── billing_webhooks.py
├── services/
│   ├── device_signatures.py
│   ├── directory.py
│   ├── revenuecat.py
│   ├── stripe_billing.py
│   ├── entitlement_reconciler.py
│   ├── push_relay.py
│   └── event_outbox.py
└── workers/
    └── scheduler.py
data/official_directory.json
migrations/versions/<revision>_household_coordination.py
tests/
├── test_family_challenges.py
├── test_household_authorization.py
├── test_checkins.py
├── test_billing_webhooks.py
└── test_directory.py
```

Reuse existing database, authentication, migration, and router conventions. Do not replace a working framework with a second application instance.

### B. Required endpoint contracts

All user endpoints require bearer authentication and object-level authorization. All mutations accept `Idempotency-Key`.

| Endpoint | Request | Success |
|---|---|---|
| `POST /api/v1/family/challenge/create` | `household_id, responder_member_id, purpose_code` | `201` challenge, nonce, expiry |
| `POST /api/v1/family/challenge/respond` | `challenge_id, decision, device_key_id, signature` | `200` authoritative state |
| `GET /api/v1/family/challenge/{id}` | — | `200` authorized challenge |
| `GET /api/v1/official-directory/lookup` | Query: `jurisdiction, q` | `200` curated entries and freshness |
| `POST /api/v1/household/subscribe` | `household_id` | `200` server-verified entitlement |
| `POST /api/v1/checkin/schedule` | `household_id, subject_member_id, due_at, grace_seconds` | `201` check-in |
| `POST /api/v1/checkin/acknowledge` | `checkin_id` | `200` updated check-in |
| `POST /api/v1/layers/event` | `event_id, layer, event_type, entity_id?` | `202` accepted |
| `GET /api/v1/household/{id}/overview` | — | `200` cockpit projection |
| `POST /api/v1/devices/register` | `public_key, algorithm, installation_id` | `201` registered key ID |
| `POST /api/v1/webhooks/revenuecat` | RevenueCat event | `200` durably received |
| `POST /api/v1/webhooks/stripe` | Raw Stripe event | `200` durably received |
| `POST /api/v1/billing/stripe/checkout-session` | `household_id, plan_code` | `201` hosted checkout URL |

If household enrollment does not exist, add authenticated invitation creation and acceptance endpoints before challenge creation. Enrollment, role changes, and device replacement must not be inferred from push identifiers.

### C. Database entities

```text
Household
HouseholdMembership
HouseholdInvitation
DeviceKey
FamilyChallenge
Checkin
SubscriptionGrant
WebhookReceipt
LayerEvent
OutboxMessage
IdempotencyRecord
```

Important constraints:

- Unique membership per `(household_id, user_id)`.
- Unique webhook per `(provider, event_id)`.
- Unique subscription grant per provider subscription binding.
- Unique layer event per authenticated actor and event ID.
- Conditional challenge update only while pending and unexpired.
- Store UTC timestamps throughout.
- Bind idempotency keys to actor, route, and request hash.
- Reusing a key with different input returns `409`.

### D. Durable check-in worker

Do **not** implement reminders with FastAPI `BackgroundTasks`, process-local timers, or Android alarms alone.

`workers/scheduler.py`:

1. Claim due check-ins transactionally.
2. Transition overdue state and create an outbox event atomically.
3. Outbox worker resolves current authorized guardian recipients.
4. Recheck acknowledgement before dispatch.
5. Send OneSignal notifications with stable deduplication identifiers where supported.
6. Retry transient errors with bounded backoff.
7. Record