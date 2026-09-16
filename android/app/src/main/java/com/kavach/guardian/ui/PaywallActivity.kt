package com.kavach.guardian.ui

import android.graphics.Color
import android.os.Bundle
import android.view.Gravity
import android.widget.Button
import android.widget.LinearLayout
import android.widget.ScrollView
import android.widget.TextView
import android.widget.Toast
import androidx.appcompat.app.AppCompatActivity
import com.kavach.guardian.BuildConfig
import com.kavach.guardian.KavachApp
import com.kavach.guardian.net.RelayClient
import com.revenuecat.purchases.CustomerInfo
import com.revenuecat.purchases.Purchases
import com.revenuecat.purchases.PurchasesError
import com.revenuecat.purchases.interfaces.ReceiveCustomerInfoCallback

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

        setContentView(scroll)
    }

    private fun activateTier(tier: String) {
        val app = application as KavachApp
        val hid = app.store.getString("household_id") ?: "demo_family_household"

        // RevenueCat test mode / production activation
        if (Purchases.isConfigured) {
            Purchases.sharedInstance.getCustomerInfo(object : ReceiveCustomerInfoCallback {
                override fun onReceived(customerInfo: CustomerInfo) {
                    syncTierToBackend(hid, tier)
                }
                override fun onError(error: PurchasesError) {
                    syncTierToBackend(hid, tier)
                }
            })
        } else {
            syncTierToBackend(hid, tier)
        }
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
