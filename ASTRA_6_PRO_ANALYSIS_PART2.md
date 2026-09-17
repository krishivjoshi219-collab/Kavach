# 2. KILLER ARCHITECTURAL & PRODUCT FEATURES  
## Must-Build Innovations

**Strategic thesis: Kavach should not compete as another caller-ID database. It should become the trusted, out-of-band verification layer families use when caller ID, familiar voices, and urgent stories can no longer be trusted.**

A convincing winning demo is not:

> “Our AI thinks this number is suspicious.”

It is:

> “An unfamiliar caller claimed to be your daughter. Kavach helped you pause, contacted your daughter’s enrolled device, and returned an authenticated response—without trusting the caller’s number or voice.”

That is differentiated, technically achievable, privacy-preserving, and naturally monetizable as a family product.

### Planning assumptions

The previous section and existing repository are not included here. The implementation paths below therefore assume:

- Android: Kotlin, Jetpack Compose, minimum SDK 29.
- Backend: FastAPI, PostgreSQL, Redis, an asynchronous worker.
- Website: Next.js App Router.
- Native subscriptions: RevenueCat with Google Play Billing.
- Notifications: OneSignal.
- Primary users: an older adult or other protected family member, plus an adult child acting as a guardian.

**Prize amounts and rules need verification.** The supplied HAMM and Samsung amounts are truncated, and no official 2026 rules are available in this conversation. Treat the named prize tracks as targets—not confirmed eligibility, award values, or integration requirements.

---

## 2.1 Feature One: Family Proof — Out-of-Band Challenge–Response Verification

### The headline

**“Verify the person’s enrolled device, not the incoming voice.”**

This is Kavach’s strongest differentiator.

Voice cloning makes “I recognize their voice” unreliable. Caller-ID spoofing makes “Their number appeared” unreliable. Kavach establishes a separate trust channel between enrolled family members.

### The actual user experience

A parent receives a call:

> “It’s me. I’m in trouble. Please send money immediately.”

The parent opens Kavach from a notification or the launcher and taps:

**“Check with my family.”**

They select:

- Who the caller claims to be.
- What the caller is asking:
  - “Did you call me?”
  - “Did you ask me to send money?”
  - “Are you actually in trouble?”
  - “I need help checking this story.”

The guardian receives:

> “Mum wants to verify a request claiming to be from you. Did you make this request?”

The guardian opens Kavach, sees the exact request, and responds:

- **I made this request.**
- **I did not make this request.**
- **I need help too.**

For the strongest assurance level, the guardian authenticates using a biometric-backed device key.

The parent sees one of four honest outcomes:

| State | Parent-facing wording |
|---|---|
| Authenticated denial | “Priya’s enrolled device says she did not make this request. End the call and contact her using your saved number.” |
| Authenticated confirmation | “Priya’s enrolled device confirmed this request. This does not authenticate the incoming caller. Call her back using your saved number before acting.” |
| No response | “Your family has not confirmed this. Do not treat silence as approval.” |
| Help response | “Your family member requested help. Contact another trusted person.” |

**Do not display “Caller verified” or “Safe to pay.”** The system authenticates a response from an enrolled device; it does not cryptographically authenticate the telephone caller.

### Why this is better than static safe words

A shared safe word is vulnerable to:

- Accidental disclosure.
- Social engineering.
- Reuse.
- A compromised family chat.
- A caller persuading someone to reveal the word.

Kavach’s challenge should instead be:

- Unique.
- Short-lived.
- Bound to the exact question.
- Bound to the requesting family member.
- Bound to the responding device.
- Unusable after completion.

There should be **no OTP or secret that the parent reads aloud to the caller**.

### Technical design

#### Enrollment

1. Users authenticate into their accounts.
2. A guardian creates a family group.
3. A protected member joins through a one-time invitation.
4. The relationship is confirmed through an existing trusted channel:
   - Preferably an in-person QR scan.
   - Otherwise a callback to an independently known number.
5. Each participating Android device generates a signing key in Android Keystore.
6. The backend registers the public key against the authenticated user and device.

An invitation link proves access to the invitation. It does **not** independently prove that the person accepting it is the intended relative. The confirmation step must be explicit.

#### Challenge object

```json
{
  "challenge_id": "uuid",
  "family_id": "uuid",
  "requester_user_id": "uuid",
  "intended_responder_user_id": "uuid",
  "question_type": "DID_YOU_REQUEST_MONEY",
  "context_digest": "sha256-of