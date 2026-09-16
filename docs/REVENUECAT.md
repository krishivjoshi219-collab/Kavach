# Kavach Monetization & RevenueCat Integration Spec

> **Philosophy**: Free protection for seniors must cost nothing to run ($0 cloud cost via on-device rules). Adult children happily pay for their parents' safety, funding cloud AI inference and creating high-margin, sustainable unit economics.

---

## 1. Unit Economics & Business Model

* **The Buyer vs The User**: Seniors (users) are sensitive to friction and subscriptions. Adult children aged 35–55 (buyers) readily purchase peace of mind, elder care tools, and safety subscriptions ($30–50/mo medical alert market).
* **Zero Marginal Cost Free Tier**: The Free tier runs 100% on-device using the Kotlin/Python `RuleEngine`. No cloud API calls are required for clear scams and clear-safe calls.
* **Inference Margins**:
  * Cloud LLM inference (Gemini Flash / Groq) costs ~$0.0015 to $0.002 per analysis turn.
  * **Pro ($4.99/mo)** grants 200 cloud queries/mo = ~$0.40 max server cost (**>90% gross margin**).
  * **Ultra ($11.99/mo)** grants 2,000 queries/mo for multi-senior households (**>80% gross margin**).

---

## 2. Subscription Tiers Specification

| Feature | Free Shield ($0/mo) | Pro Shield ($4.99/mo) | Ultra Shield ($11.99/mo) |
|---|---|---|---|
| **Target** | Individual seniors | Caregiver / Single household | Multi-senior / Extended families |
| **On-Device Rule Engine** | ✅ Yes | ✅ Yes | ✅ Yes |
| **SMS Phishing Quarantine** | ✅ Yes | ✅ Yes | ✅ Yes |
| **Active Telecom Call Screening** | ❌ None | ✅ Auto-Reject & Block | ✅ Priority Auto-Reject |
| **Remote Call Cut by Family** | ❌ None | ✅ One-tap Remote Cut | ✅ One-tap Remote Cut |
| **Emergency Dual Siren Alert** | ❌ None | ✅ Instant Dual Alert | ✅ Instant Dual Alert |
| **Cloud AI Brain Quota** | 20 checks/mo | 200 checks/mo | 2,000 checks/mo |
| **Household Seniors Supported** | 1 senior | 1 senior | Unlimited seniors |
| **Zero-Knowledge Relay Sync** | Manual pull | ✅ Instant push/pull | ✅ Priority push/pull |

---

## 3. RevenueCat Project Configuration

### 3.1 Entitlements & Offerings
* **Entitlement ID**: `shield_protection`
  * Associated Packages:
    * `$rc_monthly` (Pro Monthly)
    * `ultra_monthly` (Ultra Monthly)
* **Products**:
  * `kavach_pro_monthly` → Google Play Product ID `kavach_pro_monthly` ($4.99)
  * `kavach_ultra_monthly` → Google Play Product ID `kavach_ultra_monthly` ($11.99)
* **Offering ID**: `default`

### 3.2 Mobile SDK Setup (`android/app`)
* **Dependency**:
  ```kotlin
  implementation("com.revenuecat.purchases:purchases:10.21.1")
  implementation("com.revenuecat.purchases:purchases-ui:10.21.1")
  ```
* **Initialization** (`KavachApp.kt`):
  ```kotlin
  if (BuildConfig.REVENUECAT_KEY != "test_REPLACE_ME") {
      Purchases.configure(PurchasesConfiguration.Builder(this, BuildConfig.REVENUECAT_KEY).build())
  }
  ```
* **Paywall View** (`PaywallActivity.kt`):
  Renders the 3-tier card selection, calls `Purchases.sharedInstance.purchase()`, and synchronizes the tier entitlement with the backend via `POST /api/v1/household/tier`.

---

## 4. Backend Webhook Verification (`mobile_api.py`)

RevenueCat webhooks post subscription events to the server endpoint to keep household entitlements synchronized:

```
POST /api/v1/household/tier
Body: { "household_id": "hh_abc123", "tier": "pro" }
```

In production, webhook validation:
1. Verifies the `Authorization: Bearer <RC_WEBHOOK_AUTH_TOKEN>` header.
2. Unpacks `event.type`:
   * `INITIAL_PURCHASE` or `RENEWAL` → `set_tier(household_id, event.entitlement_id)`
   * `CANCELLATION` or `EXPIRATION` → `set_tier(household_id, "free")`
3. Audits tier changes into the database.
