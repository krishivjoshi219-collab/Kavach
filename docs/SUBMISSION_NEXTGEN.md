# Kavach — Next Gen Submission Pack (RevenueCat Shipaton 2026)

> **Track:** Next Gen Award only (student / minor-eligible). No store release required.
> Judged on **demo video + public open-source repo**. Live at `GET /api/nextgen/proof`.

## 1. What judges open (60 seconds)
1. **Video (<2 min, YouTube/Vimeo public):** `assets/kavach-demo-2min.mp4` is the filming source. Beats in `DEMO_2MIN_WINNABLE.md`: idle → live Bank-OTP attack (zero buzz + dual siren) → war-room Block → callback dies pre-ring → Audit (relay = noise) → signed rules vN → paywall promo `SHIPATON-JUDGE`.
2. **Repo:** public, MIT `LICENSE` at root (detectable in About). Instructions below.
3. **Proof endpoint:** `/api/nextgen/proof` returns RevenueCat integration proof, demo contract, and asset checklist in one JSON.

## 2. Run it (no keys, no card, $0)
```bash
git clone https://github.com/krishivjoshi219-collab/Kavach.git
cd Kavach
pip install -r mcp_server/requirements.txt
uvicorn app:app --port 7860
bash scripts/warm.sh http://localhost:7860   # healthz → readyz → SCAM proof
bash scripts/nextgen_verify.sh http://localhost:7860  # icons, screenshots, proof
```
- Senior console: `simulator/web` → `npm install && npm run build` (or `npm run dev`).
- API docs: `/docs` · board `/apps/family-board.html` · quiz `/funnel.html`.
- Android (two APKs, one codebase): CI builds `kavach-senior-apk` (`com.kavach.guardian.senior`, boots to sanctuary) + `kavach-manager-apk` (`com.kavach.guardian.manager`, boots to war-room). Flavors in `android/app/build.gradle.kts`; `RoleSelectionActivity` auto-routes per `BuildConfig.APP_ROLE`. Local: `gradle assembleSeniorDebug assembleManagerDebug`.

## 3. RevenueCat — thoughtful use (Next Gen criterion 3)
- **SDK:** `PaywallActivity.kt` — offerings → `purchase(package)` → entitlement check (`shield_protection` + aliases) → `POST /api/v1/household/tier` reconcile; `restorePurchases()`; judge promo `SHIPATON-JUDGE` unlocks Pro in TEST MODE (no card, no charge, badge on screen).
- **Server authority:** `POST /api/v1/billing/webhook` — Bearer-gated when `RC_WEBHOOK_AUTH` set, idempotent receipts (`webhook_receipts`), downgrade path. Client `CustomerInfo` is UI hint only.
- **Never paywalled:** urgent actions, consent screens, revoke/kill-switch, export.
- **Unit economics:** `docs/REVENUECAT.md` — 95% verdicts on-device ($0 marginal), Pro 200 / Ultra 2,000 cloud-brain quota.
- **Verify:** `/api/nextgen/proof` → `{revenuecat: {entitlements, promo, webhook, tiers}}`.

## 4. Why it wins (criterion 1, 2, 4)
- **Real problem:** $10B+/yr elder fraud; shame isolates seniors. Kavach **acts** (quarantine, pre-ring reject, dual siren, E2E evidence) instead of chatting.
- **Working, not slides:** 52+ backend tests, Android `RuleEngineTest` + `CommunityShieldTest`, 60-SMS flood + chaos harness (`scripts/robo/`), CI backend+frontend+android+docker.
- **Technical care:** deterministic rules decide / LLM only narrates; Tink ECIES-P256; signed rule packs (Ed25519, verify-then-apply); community shield = hashes only, 3-household gate, manager-sovereign; Hindi/Hinglish/English; dignity-first copy; honest limits in README.

## 5. Submission checklist (blocks disqualification)
- [ ] Devpost uses **student/academic email** (.edu or equivalent, JetBrains/swot-verified).
- [ ] **Parent/guardian consent form** completed before Sept 30: https://forms.gle/Gx2Cr4X8WPk9V1q77 (minor entrants).
- [ ] Repo **public** + `LICENSE` (MIT) visible at top.
- [ ] Video **<2 min**, public YouTube/Vimeo link, footage on real device, no third-party trademark/music without permission. All text/video in **English** (or with translation).
- [ ] `assets/icon-1024.png` is **1024×1024** · `assets/screenshot-1179x2556.png` is **1179×2556**, no device frame.
- [ ] Text description: features + functionality (README → sections K1–K3 + learns + E2E + business).
- [ ] No store URL needed for Next Gen. TEST MODE throughout; judges use promo, not cards.
- [ ] Minor entrant: enter **Next Gen only** (minors are ineligible for all other prize categories per §3/§8).

## 6. Repo map (judge speed-read)
`app.py` (chat/feed/demo/challenge/MCP) · `mobile_api.py` (`/api/v1/*` blind relay) · `agent/` (redflags source-of-truth, rulepack sign, mobile relay, protocols, agent) · `android/` (Senior sanctuary, Family war-room, `SmsHandler` one path, `KavachScreeningService` pre-ring, `ShieldCrypto` Tink, `PaywallActivity` RevenueCat) · `simulator/web/` (dual preview) · `mcp_server/` (MCP + board app) · `tests/` · `scripts/warm.sh` + `scripts/nextgen_verify.sh`.
