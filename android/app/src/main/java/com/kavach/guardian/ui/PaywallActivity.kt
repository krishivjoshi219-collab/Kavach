package com.kavach.guardian.ui

import android.graphics.Color
import android.graphics.drawable.GradientDrawable
import android.os.Bundle
import android.view.Gravity
import android.widget.Button
import android.widget.EditText
import android.widget.LinearLayout
import android.widget.ScrollView
import android.widget.TextView
import android.widget.Toast
import androidx.appcompat.app.AppCompatActivity
import com.kavach.guardian.BuildConfig
import com.kavach.guardian.KavachApp
import com.kavach.guardian.net.RelayClient
import com.revenuecat.purchases.CustomerInfo
import com.revenuecat.purchases.Offerings
import com.revenuecat.purchases.Package
import com.revenuecat.purchases.PurchaseParams
import com.revenuecat.purchases.Purchases
import com.revenuecat.purchases.PurchasesError
import com.revenuecat.purchases.interfaces.PurchaseCallback
import com.revenuecat.purchases.interfaces.ReceiveCustomerInfoCallback
import com.revenuecat.purchases.interfaces.ReceiveOfferingsCallback
import com.revenuecat.purchases.models.StoreTransaction

/**
 * Modern High-Craft RevenueCat Paywall for Family Guardians (Adult Children):
 * Multi-device household protection tiers, seat-based entitlements,
 * live RevenueCat SDK purchase/restore callbacks, and 1-tap Judge evaluation unlock.
 */
class PaywallActivity : AppCompatActivity() {

    private lateinit var client: RelayClient
    private var proPackage: Package? = null
    private var familyPackage: Package? = null
    private var selectedTier: String = "annual" // "annual" or "monthly"
    private lateinit var statusBadge: TextView

    override fun onCreate(savedInstanceState: Bundle?) {
        super.onCreate(savedInstanceState)

        val app = application as KavachApp
        val store = app.store
        client = RelayClient(BuildConfig.KAVACH_API)

        val scroll = ScrollView(this).apply {
            isFillViewport = true
            setBackgroundColor(Color.parseColor("#121212")) // Premium dark mode for adult child
        }

        val root = LinearLayout(this).apply {
            orientation = LinearLayout.VERTICAL
            setPadding(40, 48, 40, 48)
        }
        scroll.addView(root)

        fun createCardDrawable(bgColor: Int, cornerRadiusDp: Float = 16f, strokeColor: Int = Color.TRANSPARENT, strokeWidthDp: Float = 0f): GradientDrawable {
            return GradientDrawable().apply {
                shape = GradientDrawable.RECTANGLE
                cornerRadius = cornerRadiusDp * resources.displayMetrics.density
                setColor(bgColor)
                if (strokeWidthDp > 0) {
                    setStroke((strokeWidthDp * resources.displayMetrics.density).toInt(), strokeColor)
                }
            }
        }

        // 1. Header Shield & Title
        val headerIcon = TextView(this).apply {
            text = "🛡️"
            textSize = 36f
            gravity = Gravity.CENTER
        }
        root.addView(headerIcon)

        val title = TextView(this).apply {
            text = "Protect the People Who Raised You"
            textSize = 24f
            setTextColor(Color.WHITE)
            typeface = android.graphics.Typeface.DEFAULT_BOLD
            gravity = Gravity.CENTER
            setPadding(0, 12, 0, 8)
        }
        root.addView(title)

        val subtitle = TextView(this).apply {
            text = "Elder fraud steals $10B+ every year. Shield your parents' phones with on-device AI, pre-ring call rejection, and instant family war-room alerts."
            textSize = 14f
            setTextColor(Color.parseColor("#B0BEC5"))
            gravity = Gravity.CENTER
            setLineSpacing(4f, 1.15f)
            setPadding(0, 0, 0, 24)
        }
        root.addView(subtitle)

        // 2. Active Entitlement Status Pill
        statusBadge = TextView(this).apply {
            val currentTier = store.getString("tier") ?: "free"
            text = if (currentTier == "pro" || currentTier == "ultra") "✨ PRO FAMILY SHIELD ACTIVE (3 Parent Seats)"
                   else "STANDARD TIER (1 Parent Seat)"
            textSize = 13f
            typeface = android.graphics.Typeface.DEFAULT_BOLD
            setTextColor(if (currentTier == "pro" || currentTier == "ultra") Color.parseColor("#FFD54F") else Color.parseColor("#90A4AE"))
            background = createCardDrawable(Color.parseColor("#1E1E1E"), 24f, Color.parseColor("#37474F"), 1f)
            setPadding(32, 12, 32, 12)
            gravity = Gravity.CENTER
        }
        val statusLp = LinearLayout.LayoutParams(
            LinearLayout.LayoutParams.WRAP_CONTENT,
            LinearLayout.LayoutParams.WRAP_CONTENT
        ).apply {
            gravity = Gravity.CENTER_HORIZONTAL
            setMargins(0, 0, 0, 28)
        }
        root.addView(statusBadge, statusLp)

        // 3. Plan Option: Annual (Best Value)
        val annualCard = LinearLayout(this).apply {
            orientation = LinearLayout.VERTICAL
            background = createCardDrawable(Color.parseColor("#1E2A1E"), 16f, Color.parseColor("#4CAF50"), 2f)
            setPadding(28, 24, 28, 24)
            isClickable = true
            isFocusable = true
            setOnClickListener {
                selectedTier = "annual"
                Toast.makeText(this@PaywallActivity, "Selected: Annual Family Protection Plan", Toast.LENGTH_SHORT).show()
            }
        }
        val bestValueBadge = TextView(this).apply {
            text = "★ MOST POPULAR • SAVE 35%"
            textSize = 11f
            setTextColor(Color.parseColor("#81C784"))
            typeface = android.graphics.Typeface.DEFAULT_BOLD
            setPadding(0, 0, 0, 6)
        }
        val annualHeader = TextView(this).apply {
            text = "Family Fortress Annual — $79.99 / yr"
            textSize = 17f
            setTextColor(Color.WHITE)
            typeface = android.graphics.Typeface.DEFAULT_BOLD
        }
        val annualSub = TextView(this).apply {
            text = "Just $6.67/mo • 7-day free trial • 2 parents + 6 caregivers • save 44% vs $11.99/mo"
            textSize = 13f
            setTextColor(Color.parseColor("#A5D6A7"))
            setPadding(0, 4, 0, 0)
        }
        annualCard.addView(bestValueBadge)
        annualCard.addView(annualHeader)
        annualCard.addView(annualSub)

        val planCardLp = LinearLayout.LayoutParams(
            LinearLayout.LayoutParams.MATCH_PARENT,
            LinearLayout.LayoutParams.WRAP_CONTENT
        ).apply { setMargins(0, 0, 0, 16) }
        root.addView(annualCard, planCardLp)

        // 4. Plan Option: Monthly
        val monthlyCard = LinearLayout(this).apply {
            orientation = LinearLayout.VERTICAL
            background = createCardDrawable(Color.parseColor("#262626"), 16f, Color.parseColor("#424242"), 1f)
            setPadding(28, 24, 28, 24)
            isClickable = true
            isFocusable = true
            setOnClickListener {
                selectedTier = "monthly"
                Toast.makeText(this@PaywallActivity, "Selected: Monthly Family Protection Plan", Toast.LENGTH_SHORT).show()
            }
        }
        val monthlyHeader = TextView(this).apply {
            text = "Pro Caregiver Monthly — $4.99 / mo"
            textSize = 17f
            setTextColor(Color.WHITE)
            typeface = android.graphics.Typeface.DEFAULT_BOLD
        }
        val monthlySub = TextView(this).apply {
            text = "1 senior + 2 caregivers • Family Fortress $11.99/mo in store • Cancel anytime"
            textSize = 13f
            setTextColor(Color.parseColor("#9E9E9E"))
            setPadding(0, 4, 0, 0)
        }
        monthlyCard.addView(monthlyHeader)
        monthlyCard.addView(monthlySub)
        root.addView(monthlyCard, planCardLp)

        // 5. Feature Breakdown Checklist
        val featureBox = LinearLayout(this).apply {
            orientation = LinearLayout.VERTICAL
            background = createCardDrawable(Color.parseColor("#1A1A1A"), 14f)
            setPadding(24, 20, 24, 20)
        }
        val features = listOf(
            "✓ Multi-Device Seat: Protect 3 parents/grandparents with 1 subscription",
            "✓ Silent SMS Quarantine: Bank scams & malicious APKs intercepted without buzzing",
            "✓ Pre-Ring Call Defense: Known scam numbers terminated before the first ring",
            "✓ Instant E2E Family Siren: Emergency alert sounds on both senior and child phones",
            "✓ Daily Signed Threat Intelligence: Fresh community fraud rules verified on-device",
            "✓ Zero Cloud Spying: Audio & personal SMS never uploaded; server sees only hashes"
        )
        for (feat in features) {
            featureBox.addView(TextView(this).apply {
                text = feat
                textSize = 13f
                setTextColor(Color.parseColor("#CFD8DC"))
                setPadding(0, 6, 0, 6)
            })
        }
        root.addView(featureBox, planCardLp)

        // 6. Primary Action: Subscribe via RevenueCat
        val subscribeBtn = Button(this).apply {
            text = "Start 7-Day Free Trial via RevenueCat →"
            textSize = 16f
            typeface = android.graphics.Typeface.DEFAULT_BOLD
            setTextColor(Color.BLACK)
            background = createCardDrawable(Color.parseColor("#4CAF50"), 12f)
            setPadding(24, 36, 24, 36)
            isAllCaps = false
            setOnClickListener {
                activateTier(if (selectedTier == "annual") "ultra" else "pro")
            }
        }
        root.addView(subscribeBtn, planCardLp)

        // 7. Judge Evaluation Access (Shipaton 2026 Special)
        val judgeCard = LinearLayout(this).apply {
            orientation = LinearLayout.VERTICAL
            background = createCardDrawable(Color.parseColor("#2C2416"), 16f, Color.parseColor("#FFA000"), 1f)
            setPadding(24, 20, 24, 20)
        }
        val judgeTitle = TextView(this).apply {
            text = "⚖️ RevenueCat Shipaton Judge Evaluation"
            textSize = 14f
            typeface = android.graphics.Typeface.DEFAULT_BOLD
            setTextColor(Color.parseColor("#FFD54F"))
            setPadding(0, 0, 0, 6)
        }
        val judgeDesc = TextView(this).apply {
            text = "Next Gen judges (TEST MODE, no card, no charge): enter promo to unlock Pro Family Shield."
            textSize = 12f
            setTextColor(Color.parseColor("#FFE082"))
            setPadding(0, 0, 0, 12)
        }
        val promoRow = LinearLayout(this).apply {
            orientation = LinearLayout.HORIZONTAL
            gravity = Gravity.CENTER_VERTICAL
        }
        val promoInput = EditText(this).apply {
            setText("SHIPATON-JUDGE")
            textSize = 13f
            setTextColor(Color.WHITE)
            background = createCardDrawable(Color.parseColor("#1E1E1E"), 8f, Color.parseColor("#424242"), 1f)
            setPadding(20, 16, 20, 16)
            layoutParams = LinearLayout.LayoutParams(0, LinearLayout.LayoutParams.WRAP_CONTENT, 1f)
        }
        val unlockBtn = Button(this).apply {
            text = "Unlock Pro"
            textSize = 13f
            typeface = android.graphics.Typeface.DEFAULT_BOLD
            setTextColor(Color.BLACK)
            background = createCardDrawable(Color.parseColor("#FFD54F"), 8f)
            setPadding(24, 16, 24, 16)
            isAllCaps = false
            setOnClickListener {
                val code = promoInput.text.toString().trim()
                if (!code.equals("SHIPATON-JUDGE", ignoreCase = true)) {
                    Toast.makeText(this@PaywallActivity, "Unknown promo code. Judges: use SHIPATON-JUDGE.", Toast.LENGTH_LONG).show()
                    return@setOnClickListener
                }
                val hid = (application as KavachApp).store.getString("household_id") ?: "demo_family_household"
                syncTierToBackend(hid, "pro")
                statusBadge.text = "✨ PRO FAMILY SHIELD ACTIVE (3 Parent Seats)"
                statusBadge.setTextColor(Color.parseColor("#FFD54F"))
                Toast.makeText(this@PaywallActivity, "Pro Family Shield unlocked for evaluation! Entitlement active.", Toast.LENGTH_LONG).show()
            }
        }
        promoRow.addView(promoInput)
        promoRow.addView(unlockBtn)
        judgeCard.addView(judgeTitle)
        judgeCard.addView(judgeDesc)
        judgeCard.addView(promoRow)
        root.addView(judgeCard, planCardLp)

        // 8. Footer Restore & Legal
        val footerRow = LinearLayout(this).apply {
            orientation = LinearLayout.HORIZONTAL
            gravity = Gravity.CENTER
            setPadding(0, 16, 0, 24)
        }
        val restoreBtn = Button(this).apply {
            text = "Restore Purchases"
            textSize = 12f
            setTextColor(Color.parseColor("#90A4AE"))
            setBackgroundColor(Color.TRANSPARENT)
            isAllCaps = false
            setOnClickListener { onRestoreTapped() }
        }
        footerRow.addView(restoreBtn)
        root.addView(footerRow)

        setContentView(scroll)
        fetchOfferings {}
    }

    private fun activateTier(tier: String) {
        val hid = (application as KavachApp).store.getString("household_id") ?: "demo_family_household"

        // TEST MODE (no SDK key / judges without store): promo-code unlock only.
        if (!Purchases.isConfigured) {
            if (tier == "free") {
                syncTierToBackend(hid, "free")
            } else {
                Toast.makeText(this, "TEST MODE: Tap 'Unlock Pro' in Judge Evaluation section below.", Toast.LENGTH_LONG).show()
            }
            return
        }

        val pkg = if (tier == "ultra") familyPackage ?: proPackage else proPackage
        if (pkg == null) {
            fetchOfferings { fetched ->
                val p = if (tier == "ultra") familyPackage ?: proPackage else proPackage
                if (p != null) purchasePackage(p, tier, hid)
                else if (fetched) purchasePackage(null, tier, hid)
                else Toast.makeText(this, "Store unavailable. Try promo unlock below.", Toast.LENGTH_LONG).show()
            }
        } else {
            purchasePackage(pkg, tier, hid)
        }
    }

    private fun fetchOfferings(done: (Boolean) -> Unit) {
        try {
            Purchases.sharedInstance.getOfferings(object : ReceiveOfferingsCallback {
                override fun onReceived(offerings: Offerings) {
                    val def = offerings.current
                    proPackage = def?.availablePackages?.firstOrNull {
                        it.identifier.contains("pro", true) || it.identifier.contains("monthly", true)
                    } ?: def?.availablePackages?.firstOrNull()
                    familyPackage = def?.availablePackages?.firstOrNull {
                        it.identifier.contains("family", true) || it.identifier.contains("annual", true)
                    }
                    done(true)
                }

                override fun onError(error: PurchasesError) {
                    done(false)
                }
            })
        } catch (_: Exception) {
            done(false)
        }
    }

    private fun purchasePackage(pkg: Package?, tier: String, hid: String) {
        if (pkg == null) {
            syncTierToBackend(hid, tier)
            return
        }
        // Server authority: family/annual packages map to ultra, monthly to pro —
        // never trust the pre-selected card alone once a real package is known.
        val resolved = if (pkg.identifier.contains("family", true)
            || pkg.identifier.contains("annual", true)
            || pkg.identifier.contains("ultra", true)) "ultra" else "pro"
        val params = PurchaseParams.Builder(this, pkg).build()
        Purchases.sharedInstance.purchase(params, object : PurchaseCallback {
            override fun onCompleted(storeTransaction: StoreTransaction, customerInfo: CustomerInfo) {
                if (hasProEntitlement(customerInfo)) {
                    syncTierToBackend(hid, resolved)
                    statusBadge.text = if (resolved == "ultra")
                        "✨ FAMILY FORTRESS ACTIVE (Parent Seats)"
                    else "✨ PRO FAMILY SHIELD ACTIVE (3 Parent Seats)"
                    statusBadge.setTextColor(Color.parseColor("#FFD54F"))
                }
            }

            override fun onError(error: PurchasesError, userCancelled: Boolean) {
                if (!userCancelled) {
                    Toast.makeText(this@PaywallActivity, "Purchase error: ${error.message}", Toast.LENGTH_LONG).show()
                }
            }
        })
    }

    private fun onRestoreTapped() {
        if (!Purchases.isConfigured) {
            Toast.makeText(this, "TEST MODE: no SDK key. Use judge promo unlock.", Toast.LENGTH_LONG).show()
            return
        }
        Purchases.sharedInstance.restorePurchases(object : ReceiveCustomerInfoCallback {
            override fun onReceived(customerInfo: CustomerInfo) {
                val hasPro = hasProEntitlement(customerInfo)
                val hid = (application as KavachApp).store.getString("household_id") ?: "demo_family_household"
                if (hasPro) {
                    syncTierToBackend(hid, "pro")
                    statusBadge.text = "✨ PRO FAMILY SHIELD ACTIVE (3 Parent Seats)"
                    statusBadge.setTextColor(Color.parseColor("#FFD54F"))
                    Toast.makeText(this@PaywallActivity, "Purchases restored: Pro entitlement active.", Toast.LENGTH_LONG).show()
                } else {
                    Toast.makeText(this@PaywallActivity, "No active subscriptions found.", Toast.LENGTH_SHORT).show()
                }
            }

            override fun onError(error: PurchasesError) {
                Toast.makeText(this@PaywallActivity, "Restore error: ${error.message}", Toast.LENGTH_LONG).show()
            }
        })
    }

    private fun hasProEntitlement(info: CustomerInfo): Boolean {
        // Canonical Next Gen entitlement is `shield_protection`.
        // Accept legacy/alias IDs so dashboard renames never lock judges out.
        val ids = listOf("shield_protection", "family_fortress", "pro_caregiver", "pro", "family_pro_shield", "kavach_pro", "kavach_premium")
        return ids.any { info.entitlements[it]?.isActive == true }
    }

    private fun syncTierToBackend(hid: String, tier: String) {
        val app = application as KavachApp
        app.store.putString("tier", tier)
        Thread {
            try {
                client.setTier(hid, tier)
                runOnUiThread {
                    Toast.makeText(this, "Family Shield tier updated to $tier ✓", Toast.LENGTH_SHORT).show()
                }
            } catch (e: Exception) {
                runOnUiThread {
                    Toast.makeText(this, "Local tier saved as $tier", Toast.LENGTH_SHORT).show()
                }
            }
        }.start()
    }
}
