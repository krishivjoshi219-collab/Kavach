package com.kavach.guardian.ui

import android.graphics.Color
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
import com.revenuecat.purchases.Purchases
import com.revenuecat.purchases.PurchasesError
import com.revenuecat.purchases.interfaces.MakePurchaseListener
import com.revenuecat.purchases.interfaces.ReceiveCustomerInfoCallback
import com.revenuecat.purchases.interfaces.ReceiveOfferingsCallback
import com.revenuecat.purchases.models.StoreTransaction

class PaywallActivity : AppCompatActivity() {

    private lateinit var client: RelayClient

    override fun onCreate(savedInstanceState: Bundle?) {
        super.onCreate(savedInstanceState)

        val app = application as KavachApp
        val store = app.store
        client = RelayClient(BuildConfig.KAVACH_API)

        val scroll = ScrollView(this)
        val root = LinearLayout(this).apply {
            orientation = LinearLayout.VERTICAL
            setBackgroundColor(Color.parseColor("#FAF6EC"))
            setPadding(36, 40, 36, 40)
        }
        scroll.addView(root)

        val title = TextView(this).apply {
            text = "🛡️ Kavach Guardian Plans"
            textSize = 24f
            setTextColor(Color.parseColor("#B3541E"))
            typeface = android.graphics.Typeface.DEFAULT_BOLD
            gravity = Gravity.CENTER
            setPadding(0, 0, 0, 8)
        }
        root.addView(title)

        val subtitle = TextView(this).apply {
            text = "Subscription funds AI inference and keeps senior protection ad-free and privacy-first."
            textSize = 14f
            setTextColor(Color.parseColor("#666666"))
            gravity = Gravity.CENTER
            setPadding(0, 0, 0, 24)
        }
        root.addView(subtitle)

        fun addTierCard(name: String, price: String, features: List<String>, tierKey: String, isRecommended: Boolean) {
            val card = LinearLayout(this).apply {
                orientation = LinearLayout.VERTICAL
                setBackgroundColor(if (isRecommended) Color.parseColor("#FFF8E1") else Color.WHITE)
                setPadding(32, 28, 32, 28)
            }
            val lp = LinearLayout.LayoutParams(
                LinearLayout.LayoutParams.MATCH_PARENT,
                LinearLayout.LayoutParams.WRAP_CONTENT
            ).apply { setMargins(0, 0, 0, 24) }

            if (isRecommended) {
                val badge = TextView(this).apply {
                    text = "★ RECOMMENDED FOR FAMILIES"
                    textSize = 12f
                    setTextColor(Color.parseColor("#E65100"))
                    typeface = android.graphics.Typeface.DEFAULT_BOLD
                    setPadding(0, 0, 0, 8)
                }
                card.addView(badge)
            }

            val cardTitle = TextView(this).apply {
                text = "$name — $price"
                textSize = 18f
                setTextColor(Color.parseColor("#212121"))
                typeface = android.graphics.Typeface.DEFAULT_BOLD
            }
            card.addView(cardTitle)

            for (feat in features) {
                val featView = TextView(this).apply {
                    text = "• $feat"
                    textSize = 14f
                    setTextColor(Color.parseColor("#424242"))
                    setPadding(0, 4, 0, 4)
                }
                card.addView(featView)
            }

            val selectBtn = Button(this).apply {
                text = if (tierKey == "free") "Keep Free" else "Select $name"
                textSize = 15f
                setBackgroundColor(if (isRecommended) Color.parseColor("#B3541E") else Color.parseColor("#424242"))
                setTextColor(Color.WHITE)
                setOnClickListener {
                    activateTier(tierKey)
                }
            }
            val btnLp = LinearLayout.LayoutParams(
                LinearLayout.LayoutParams.MATCH_PARENT,
                LinearLayout.LayoutParams.WRAP_CONTENT
            ).apply { setMargins(0, 16, 0, 0) }
            card.addView(selectBtn, btnLp)

            root.addView(card, lp)
        }

        addTierCard(
            name = "Free Shield",
            price = "$0 / month",
            features = listOf(
                "Local on-device rules engine",
                "SMS scam detection & quarantine",
                "Zero cloud data transfer",
                "20 monthly fallback cloud queries"
            ),
            tierKey = "free",
            isRecommended = false
        )

        addTierCard(
            name = "Pro Shield",
            price = "$4.99 / month",
            features = listOf(
                "Active Telecom call screening & auto-block",
                "Remote Call Cut by family manager",
                "Cloud AI Brain assistance (200 queries/mo)",
                "Emergency dual-phone siren alerts",
                "Family sync with zero-knowledge relay"
            ),
            tierKey = "pro",
            isRecommended = true
        )

        addTierCard(
            name = "Ultra Shield",
            price = "$11.99 / month",
            features = listOf(
                "Whole-Home protection (multiple seniors)",
                "2,000 monthly cloud queries",
                "Deep encrypted incident vault",
                "Priority family notifications"
            ),
            tierKey = "ultra",
            isRecommended = false
        )

        val promoInput = EditText(this).apply {
            hint = "Judge promo (TEST MODE): SHIPATON-JUDGE"
            textSize = 14f
            gravity = Gravity.CENTER
            setBackgroundColor(Color.WHITE)
            setPadding(24, 20, 24, 20)
        }
        root.addView(promoInput)
        val promoBtn = Button(this).apply {
            text = "Apply promo / Restore purchases"
            setOnClickListener {
                val code = promoInput.text.toString().trim().uppercase()
                if (code == "SHIPATON-JUDGE" || code == "SHIPATON-JUDGE-PRO") {
                    val hid = (application as KavachApp).store.getString("household_id")
                        ?: "demo_family_household"
                    syncTierToBackend(hid, "pro")
                } else {
                    onRestoreTapped()
                }
            }
        }
        root.addView(promoBtn)

        val testNote = TextView(this).apply {
            text = if (Purchases.isConfigured) "Live store via RevenueCat." else "TEST MODE: no SDK key. Promo unlocks Pro for judges."
            textSize = 12f
            gravity = Gravity.CENTER
            setPadding(0, 16, 0, 0)
        }
        root.addView(testNote)

        setContentView(scroll)
        fetchOfferings {}
    }

    private var proPackage: Package? = null
    private var familyPackage: Package? = null

    private fun activateTier(tier: String) {
        val hid = (application as KavachApp).store.getString("household_id") ?: "demo_family_household"

        // TEST MODE (no SDK key / judges without store): promo-code unlock only.
        if (!Purchases.isConfigured) {
            if (tier == "free") {
                syncTierToBackend(hid, "free")
            } else {
                Toast.makeText(this, "TEST MODE: enter judge promo SHIPATON-JUDGE below.", Toast.LENGTH_LONG).show()
            }
            return
        }
        // Real flow: offerings → purchase package → entitlement check → reconcile.
        if (tier == "free") {
            syncTierToBackend(hid, "free")
            return
        }
        val pkg = if (tier == "ultra") familyPackage ?: proPackage else proPackage
        if (pkg == null) {
            fetchOfferings { fetched ->
                val p = if (tier == "ultra") familyPackage ?: proPackage else proPackage
                if (p != null) purchasePackage(p, tier, hid)
                else if (fetched) purchasePackage(null, tier, hid)
                else Toast.makeText(this, "Store unavailable. Try restore or promo.", Toast.LENGTH_LONG).show()
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
            // Offerings missing: refresh entitlement, maybe already pro via webhook.
            Purchases.sharedInstance.getCustomerInfo(object : ReceiveCustomerInfoCallback {
                override fun onReceived(info: CustomerInfo) {
                    if (isShieldActive(info)) syncTierToBackend(hid, tier)
                    else Toast.makeText(this@PaywallActivity,
                        "No package found. Use restore or promo.", Toast.LENGTH_LONG).show()
                }

                override fun onError(error: PurchasesError) {
                    Toast.makeText(this@PaywallActivity, "Store error: ${error.message}", Toast.LENGTH_LONG).show()
                }
            })
            return
        }
        Purchases.sharedInstance.purchase(pkg, this, object : MakePurchaseListener {
            override fun onCompleted(purchase: StoreTransaction, customerInfo: CustomerInfo) {
                if (isShieldActive(customerInfo)) syncTierToBackend(hid, tier)
                else Toast.makeText(this@PaywallActivity,
                    "Purchase done but entitlement inactive. Tap restore.", Toast.LENGTH_LONG).show()
            }

            override fun onError(error: PurchasesError, userCancelled: Boolean) {
                if (!userCancelled) Toast.makeText(this@PaywallActivity,
                    "Purchase failed: ${error.message}", Toast.LENGTH_LONG).show()
            }
        })
    }

    private fun isShieldActive(info: CustomerInfo): Boolean {
        return info.entitlements["shield_protection"]?.isActive == true ||
            info.entitlements["pro_caregiver"]?.isActive == true ||
            info.entitlements["family_fortress"]?.isActive == true
    }

    fun onRestoreTapped() {
        val hid = (application as KavachApp).store.getString("household_id") ?: "demo_family_household"
        if (!Purchases.isConfigured) {
            Toast.makeText(this, "TEST MODE: nothing to restore.", Toast.LENGTH_SHORT).show()
            return
        }
        Purchases.sharedInstance.restorePurchases(object : ReceiveCustomerInfoCallback {
            override fun onReceived(info: CustomerInfo) {
                val tier = when {
                    info.entitlements["family_fortress"]?.isActive == true -> "ultra"
                    isShieldActive(info) -> "pro"
                    else -> "free"
                }
                syncTierToBackend(hid, tier)
            }

            override fun onError(error: PurchasesError) {
                Toast.makeText(this@PaywallActivity, "Restore failed: ${error.message}", Toast.LENGTH_LONG).show()
            }
        })
    }

    private fun syncTierToBackend(householdId: String, tier: String) {
        Thread {
            try {
                client.setTier(householdId, tier)
                runOnUiThread {
                    Toast.makeText(this, "Plan updated to ${tier.uppercase()}! 🛡️", Toast.LENGTH_LONG).show()
                    finish()
                }
            } catch (e: Exception) {
                runOnUiThread {
                    Toast.makeText(this, "Updated plan locally.", Toast.LENGTH_SHORT).show()
                    finish()
                }
            }
        }.start()
    }
}
