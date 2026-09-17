# 3. MONETIZATION & HAMM AWARD ROADMAP

**Winning thesis:** Kavach monetizes coordination and reassurance—not access to an emergency button. The adult child pays for a calmer caregiving workflow; the parent retains autonomy, understands what is shared, and can revoke access.

**Implementation assumptions:** The earlier sections and repository are not available in this conversation. The paths below are a proposed implementation contract, not a claim about existing files. Your prompt also appears to have lost digits in the award amounts and tier prices. I use **$4.99/month for Pro Caregiver** and **$9.99/month or $79/year for Family Fortress** as working prices. Confirm these, the official award names, eligibility rules, and sponsor requirements before submission.

Do not present the listed prize amounts, SDK capabilities, or a 2026 submission requirement as verified until checked against official documentation.

## 3.1 Tier architecture

### Recommended tier matrix

| Capability | Free Shield | Pro Caregiver | Family Fortress |
|---|---|---|---|
| Parent’s local check-in reminders | Included | Included | Included |
| Manual “I’m okay” / “Please call me” | Included | Included | Included |
| Parent-controlled sharing and revocation | Included | Included | Included |
| Basic pairing | One parent + one caregiver | One parent + two caregivers | Two parents + up to six caregivers |
| Basic notifications to paired caregiver | Included | Included | Included |
| Check-in history | 7 days | 90 days | 365 days, configurable |
| Custom check-in schedules | One schedule | Multiple schedules | Per-parent schedules |
| Multi-stage caregiver escalation | — | Included | Included |
| Shared acknowledgment and handoff | — | Included | Included |
| Family coordination feed | — | Basic | Included |
| Multi-parent dashboard | — | — | Included |
| Export/delete own data | Included | Included | Included |

**Free Shield is the baseline**, assuming “bash” in the prompt meant “basic.”

### Product boundary that matters

Never paywall:

- Calling an emergency contact.
- Seeing an existing urgent request.
- Acknowledging an existing incident.
- Revoking caregiver access.
- Exporting or deleting personal data.
- The explanation of notification and delivery limitations.

On downgrade:

1. Preserve core free functionality.
2. Explain which future automation will stop.
3. Do not silently terminate an active escalation.
4. Give the family a way to choose which memberships remain active.
5. Apply an explicit retention policy rather than immediately deleting historical data.

### Who buys?

**The caregiver buys; the parent joins free.**

Model the subscription as a funding source for a care circle:

```text
Payer account
    └── Circle subscription allocation
          └── Care circle
                ├── Parent membership
                ├── Caregiver membership
                └── Caregiver membership
```

For the initial release, allow **one funded circle per subscription**. Family Fortress supports two parents within that circle.

Do not distribute subscription entitlements by sharing RevenueCat credentials or making every family member use the payer’s RevenueCat App User ID.

---

## 3.2 Paywall psychology: reassurance without coercion

The purchase decision comes from a worried adult child. That creates an ethical obligation as well as a conversion opportunity.

### Trigger hierarchy

| Trigger | Appropriate implementation | Avoid |
|---|---|---|
| Dignity-first | “Support their independence without constant check-in calls.” | “Track your parents at all times.” |
| Peace of mind | “Know when a check-in is acknowledged, and who is following up.” | “Guarantee your parent’s safety.” |
| Honest loss aversion | Preview the coordination features unavailable on Free | Fabricated warnings or withholding urgent information |
| Shared responsibility | “Let another sibling share the follow-up.” | Guilt-based sibling comparisons |
| Frictionless pairing | “Scan together. Choose what to share.” | Linking a parent without their informed approval |

### Best paywall moments

**Primary: after a successful parent-approved pairing and first check-in.**

The user has experienced the core value before being asked to pay.

```text
Create circle
→ Generate QR invite
→ Parent scans
→ Parent sees requested sharing permissions
→ Parent approves
→ First check-in arrives
→ Explain optional caregiver automation
→ Show paywall
```

**Secondary: when configuring a genuinely premium capability.**

Examples:

- Add a second parent.
- Add an additional caregiver beyond the free allocation.
- Configure multi-stage escalation.
- Extend historical reporting.

**Never interrupt an urgent request, incident acknowledgment, consent screen, or emergency-contact action with a paywall.**

### Suggested paywall copy

**Headline:**  
“Share the care. Reduce the checking.”

**Supporting copy:**  
“Coordinate check-ins, follow-ups, and family handoffs—while your parent stays in control.”

**Annual option:**  
“$79/year, billed annually. Equivalent to $6.58/month.”

**Footer:**  
“Cancel through your billing provider. Kavach is not an emergency-response or medical-monitoring service. Notifications depend on device settings and connectivity.”

Do not show a trial unless that product actually has an eligible introductory offer.

---

## 3.3 RevenueCat configuration

### Catalog

Create these identifiers as the application’s naming convention:

#### Entitlements

```text
pro_caregiver
family_fortress
```

Application capability resolution:

```kotlin
enum class Plan {
    FREE, PRO, FAMILY
}

fun resolvePlan(activeEntitlementIds: Set<String>): Plan = when {
    "family_fortress" in activeEntitlementIds -> Plan.FAMILY
    "pro_caregiver" in activeEntitlementIds -> Plan.PRO
    else -> Plan.FREE
}
```

Treat Family as a superset in your capability resolver. Avoid assuming that Family purchases automatically activate a separate Pro entitlement.

#### Proposed Google Play catalog

```text
Subscription: kavach_pro
    Base plan: monthly
    Price: $4.99/month

Subscription: kavach_family
    Base plan: monthly
    Price: $9.99/month

    Base plan: annual
    Price: $79/year
```

Configure equivalent web products and prices separately if Stripe is used.

#### Offerings

```text
caregiver_default
    pro_monthly       → Pro monthly product
    $rc_monthly       → Family monthly product
    $rc_annual        → Family annual product

caregiver_reassurance
    same products and prices

caregiver_coordination
    same products and prices
```

Use a custom package identifier such as `pro_monthly` when a single offering contains more than one monthly product. Verify the current dashboard’s product/base-plan mapping requirements.

### Paywalls v2 design

Use a currently available **multi-package comparison layout**, rather than relying on an unverified named template.

Components:

1. Calm hero illustration.
2. Dignity-first headline.
3. Three concrete benefits.
4. Plan/package selector.
5. Localized store price and billing period.
6. Purchase button bound to the selected package.
7. Restore purchases.
8. Privacy policy and terms.
9. Explicit close/free continuation path.
10. Introductory-offer text only when eligible.

Use product metadata returned by the billing SDK. Do not hardcode dollar prices into production purchase buttons.

### Identity and entitlement authority

- Configure RevenueCat with the Android **public SDK key**.
- Log in using a stable opaque backend user ID.
- Never use email, phone number, or a parent’s name as the App User ID.
- Keep RevenueCat secret API keys on the backend.
- Resolve cross-device and circle access on the backend.
- Use client `CustomerInfo` for responsive purchase UI, not as the sole authority for server-side premium actions.

Backend pipeline:

```text
RevenueCat event
→ Authenticate webhook
→ Durably record event
→ Queue reconciliation
→ Retrieve current subscription state
→ Update payer entitlement snapshot
→ Recompute funded circle capabilities
→ Notify clients to refresh
```

Webhook events can arrive more than once or out of order. **Do not implement access as “last webhook wins.”**

### Experiment strategy

Do not run a fear-inducing experiment against anxious caregivers. Replace “Fear vs Reassurance” with:

- **Reassurance:** “Less uncertainty, fewer check-in calls.”
- **Coordination:** “Make sure someone knows who is following up.”

Then test **monthly versus annual selected by default**, keeping both choices equally understandable.

| Experiment | Change | Primary metric | Guardrails |
|---|---|---|---|
| A | Reassurance vs coordination headline | Purchase within 7 days of eligible exposure | Refunds, cancellations, reported pressure |
| B | Monthly vs annual default | Net collected revenue per exposed payer | Refunds, annual-plan comprehension |
| C | Post-first-check-in vs premium-feature paywall | Activated paid circles | Pairing completion, parent revocations |

Rules:

- Randomize by payer account, not session.
- Keep assignment stable.
- Run one major variable at a time.
- Use RevenueCat Experiments if supported by the current account and configuration; otherwise use your own server-assigned variant and offering selection.
- Log assigned and actually rendered variants.
- Treat hackathon-sized samples as directional, not statistically proven.

**Do not claim a conversion uplift from five users.**

---

## 3.4 Sustainable unit economics

### Define the margin honestly

“Over 90% gross margin” needs a stated denominator and cost definition.

For a $9.99 monthly subscription with a **hypothetical 15% store fee**:

```text
Consumer payment:                     $9.990
Store fee assumption:                -$1.499
Receipts after store fee:              $8.492

Allocated variable service cost:      -$0.650
Contribution after those costs:        $7.842
```

That is:

- **92.3% service margin on post-store receipts**.
- **78.5% contribution relative to the consumer payment**.

It is **not** a demonstrated 90% all-in margin on the consumer’s payment. Accounting presentation, taxes, actual billing fees, refunds, and support costs must be accounted for.

At $79/year, using the same illustrative store fee:

```text
Monthly-equivalent post-store receipts: $5.596
Maximum service COGS for >90% margin:     less than $0.560/month
```

### Architecture required for the target

- Push-first notifications.
- No continuous GPS ingestion.
- No mandatory LLM inference.
- Local reminder scheduling.
- Indexed due-time queries, not polling every user.
- Short-lived high-volume delivery telemetry.
- Aggregated long-term analytics.
- Measured sponsor/vendor costs beyond promotional credits.
- No unlimited SMS/calling bundled into low-cost tiers.

Track cost per **active care circle**, including the subsidy for free circles.

```text
Paid-circle service COGS =
    infrastructure allocation
  + vendor allocation
  + variable support allocation
  + free-tier subsidy allocation
```

The Pro tier has substantially less margin headroom. Instrument its economics independently.

---

## 3.5 Organic caregiver referral loop

```text
First useful check-in
→ Caregiver sees “Share the follow-up”
→ Invites a sibling
→ Sibling accepts
→ Parent approves expanded visibility
→ Sibling acknowledges a real check-in
→ Circle gains shared coordination value
```

Keep **invitation acceptance separate from permission activation**. The person inviting another caregiver should not automatically grant access to a parent’s data.

Measure:

- Invites per activated circle.
- Invite acceptance rate.
- Parent approval rate.
- Seven-day meaningful activity by invited caregivers.
- Paid conversion after collaboration.
- Revocation and notification opt-out rates.

Avoid address-book scraping and automatic invitations.

---

# 4. SPONSOR PRIZE MAXIMIZATION MATRIX

Treat every prize as a **proof package**, not merely an SDK logo.

| Track named in prompt | Product integration | Evidence to submit | Critical caveat |
|---|---|---|---|
| OneSignal | Check-in and escalation delivery | Journey diagram, delivery telemetry, live acknowledgment cancellation | Push cannot guarantee urgent delivery |
| Stripe Funnel Vision | Web quiz → Checkout → app handoff | Funnel events, verified payment webhook, completed pairing | Confirm category and app-store billing rules |
| Layers Growth Loop | Invite → consent → activation loop | Event trace, cohort chart, growth hypothesis | Verify actual SDK/API and judging requirements |
| Next Gen | Accessible, consent-centered mobile implementation | Accessibility walkthrough, technical architecture | Confirm eligibility |
| Peace Prize | Reduced coordination burden without surveillance | Consent demo, ethical controls, real user feedback | Do not claim unmeasured clinical/social outcomes |

## 4.1 OneSignal: multi-step Journey

### Reliability architecture

**The backend incident state machine owns escalation. OneSignal transports notifications and can orchestrate supported engagement messaging.**

Do not make a marketing Journey the only source of truth for time-sensitive follow-up.

```text
SCHEDULED
  → AWAITING_CHECKIN
      → RESOLVED
      → MISSED
          → CAREGIVER_NOTIFIED
              → ACKNOWLEDGED
              → SECONDARY_NOTIFIED
              → RESOLVED
              → EXPIRED
```

### Step 1: Morning Check-in

At the parent’s chosen local time:

- Attempt a local device reminder.
- Optionally send a OneSignal push as a complementary channel.
- Deep-link to a short-lived, authenticated check-in screen.
- Offer “I’m okay” and “Please call me.”
- Deduplicate presentation where feasible.

Default lock-screen text:

> “Your Kavach check-in is ready.”

Do not expose health or incident details on the lock screen.

### Step 2: Escalation Nudge

After a **parent-approved grace period**, if no valid response exists:

> “A scheduled check-in hasn’t been completed. You can try contacting your family member.”

Actions:

- Open incident.
- Call using the device dialer.
- “I’m following up.”

Before dispatch, the worker must re-read incident state. A late parent response should cancel pending escalation.

### Step 3: “Breakthrough” urgent alert

For an explicit “Please call me” or an unresolved escalation:

1. Notify the primary caregiver.
2. If still unacknowledged after the configured interval, notify an approved secondary caregiver.
3. Show acknowledgment ownership to avoid duplicate calls.

“Breakthrough” is a product label—not permission to bypass Do Not Disturb.

On Android:

- Create a user-controllable high-importance channel.
- Request notification permission where required.
- Explain that channel settings can limit sound and visibility.
- Do not misuse full-screen intents.
- Do not claim emergency dispatch, guaranteed delivery, or automatic DND bypass.

### OneSignal configuration

```text
External ID: opaque Kavach user UUID

Channels:
    kavach_checkins
    kavach_caregiver_updates
    kavach_urgent_requests

Low-sensitivity segmentation attributes:
    role
    locale
    onboarding_stage
    marketing_opt_in
```

Do not put diagnosis, vulnerability, or detailed parent activity into provider tags.

Use current OneSignal Journey capabilities only after verifying them. Any unsupported delay, custom event, or condition belongs in the backend orchestration layer.

Measure separately:

```text
dispatch attempted
provider accepted
delivery observed, where available
notification opened
incident acknowledged
incident resolved
```

**Provider acceptance is not proof of device delivery.**

---

## 4.2 Stripe: web-to-app conversion funnel

### Funnel

```text
funnel.html
→ 3-question coordination quiz
→ Recommendation
→ Account creation / authenticated session
→ Stripe Checkout
→ Webhook-confirmed entitlement
→ App installation/opening handoff
→ Generate parent-pairing QR in the app
→ Parent consent
→ First completed check-in
```

**Distinguish app handoff from parent pairing.** Payment should not create a preapproved parent relationship.

### Quiz questions

Use nonclinical coordination questions:

1. “How many family members help with check-ins?”
2. “Are you coordinating support for one parent or two?”
3. “What is hardest today: remembering, following up, or sharing responsibility?”

Do not ask about diagnoses merely to personalize a paywall.

### Checkout controls

- Create Checkout Sessions server-side.
- Select prices through a server allowlist.
- Bind Checkout to an authenticated account.
- Store opaque account/circle references in metadata.
- Verify webhook signatures against the raw body.
- Handle delayed payments, subscription updates, failed renewals, cancellation, and refunds.
- Never grant access from `success_url` alone.
- Use idempotency keys when creating sessions.

Choose one web entitlement reconciliation path:

1. A currently supported RevenueCat–Stripe integration, if confirmed; or
2. A backend-normalized Stripe subscription provider.

Do not run two independent writers that fight over the same entitlement state.

Native Android digital-subscription purchase flows must follow applicable Google Play billing rules. External checkout links inside the app depend on current program, jurisdiction, and eligibility rules.

### Funnel events

```text
quiz_started
quiz_completed
recommendation_viewed
checkout_started
payment_confirmed
app_handoff_created
app_handoff_redeemed
parent_pairing_approved
first_checkin_completed
```

The winning metric is **paid, activated care circles**, not Checkout conversion alone.

---

## 4.3 Layers: measurable growth loop

### Hypothesis

> Circles that add a second approved caregiver within 48 hours of their first completed check-in will show higher seven-day coordination activity than single-caregiver circles.

This is an association until tested with a randomized invitation prompt. Motivated families may both invite more people and retain better.

### SDK boundary

Do not invent Layers method names. Define an internal interface:

```kotlin
interface GrowthAnalytics {
    fun identify(userId: String)
    fun track(name: String, properties: Map<String, Any?> = emptyMap())
    fun reset()
}
```

Implement `LayersGrowthAnalytics` using the **verified SDK or documented ingestion API**.

If no qualifying SDK/API exists, confirm whether dashboard ingestion is acceptable before spending implementation time.

### Event contract

```json
{
  "event_id": "uuid",
  "name": "caregiver_invite_accepted",
  "occurred_at": "2026-08-01T10:15:00Z",
  "actor_id": "opaque-user-id",
  "circle_id": "opaque-circle-id",
  "properties": {
    "invite_source": "first_checkin_success",
    "plan": "family",
    "variant": "shared_responsibility"
  }
}
```

Exclude names, contact details, raw invite tokens, check-in content, and precise location.

### Cohort dashboard

Compare:

- First-check-in week.
- One versus multiple approved caregivers.
- Invitation-prompt assignment.
- Free versus paid at cohort entry