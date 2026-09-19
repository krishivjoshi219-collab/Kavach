package com.kavach.guardian.ui

import android.content.Intent
import android.graphics.Color
import android.graphics.Typeface
import android.os.Bundle
import android.view.Gravity
import android.widget.Button
import android.widget.LinearLayout
import android.widget.ScrollView
import android.widget.TextView
import androidx.appcompat.app.AlertDialog
import androidx.appcompat.app.AppCompatActivity
import com.kavach.guardian.KavachApp
import com.kavach.guardian.siren.SirenActivity

/**
 * Senior Sanctuary Interface:
 * Accessible, calming, senior-first design.
 * Clear visual hierarchy, generous touch targets (64dp), WCAG AAA contrast, zero developer jargon.
 */
class SeniorActivity : AppCompatActivity() {

    override fun onCreate(savedInstanceState: Bundle?) {
        super.onCreate(savedInstanceState)

        val app = application as KavachApp
        val store = app.store

        if (store.getString("onboarded") != "1") {
            startActivity(Intent(this, OnboardingActivity::class.java))
        }

        val scroll = ScrollView(this).apply {
            isFillViewport = true
            setBackgroundColor(KavachTheme.SENIOR_BG)
        }

        val pad = KavachTheme.dp(this, 20f)
        val root = LinearLayout(this).apply {
            orientation = LinearLayout.VERTICAL
            setPadding(pad, KavachTheme.dp(this@SeniorActivity, 28f), pad, pad)
            gravity = Gravity.CENTER_HORIZONTAL
        }
        scroll.addView(root)

        val marginBot16 = LinearLayout.LayoutParams(
            LinearLayout.LayoutParams.MATCH_PARENT,
            LinearLayout.LayoutParams.WRAP_CONTENT
        ).apply { setMargins(0, 0, 0, KavachTheme.dp(this@SeniorActivity, 16f)) }

        val marginBot24 = LinearLayout.LayoutParams(
            LinearLayout.LayoutParams.MATCH_PARENT,
            LinearLayout.LayoutParams.WRAP_CONTENT
        ).apply { setMargins(0, 0, 0, KavachTheme.dp(this@SeniorActivity, 24f)) }

        // 1. Top Warm Header
        val brandRow = LinearLayout(this).apply {
            orientation = LinearLayout.HORIZONTAL
            gravity = Gravity.CENTER
            setPadding(0, 0, 0, KavachTheme.dp(this@SeniorActivity, 4f))
        }
        val brandIcon = TextView(this).apply {
            text = "🛡️ "
            textSize = 20f
        }
        val brandName = TextView(this).apply {
            text = "Kavach"
            textSize = 20f
            typeface = Typeface.DEFAULT_BOLD
            setTextColor(KavachTheme.SENIOR_TEXT)
        }
        brandRow.addView(brandIcon)
        brandRow.addView(brandName)
        root.addView(brandRow)

        val greeting = TextView(this).apply {
            text = "Namaste 🙏"
            textSize = 28f
            typeface = Typeface.DEFAULT_BOLD
            setTextColor(KavachTheme.SENIOR_TEXT)
            gravity = Gravity.CENTER
            setPadding(0, KavachTheme.dp(this@SeniorActivity, 8f), 0, KavachTheme.dp(this@SeniorActivity, 4f))
        }
        root.addView(greeting)

        val subGreeting = TextView(this).apply {
            text = "Aapka phone surakshit hai • Your phone is safe"
            textSize = 14f
            setTextColor(KavachTheme.SENIOR_MUTED)
            gravity = Gravity.CENTER
            setPadding(0, 0, 0, KavachTheme.dp(this@SeniorActivity, 24f))
        }
        root.addView(subGreeting)

        // 2. Calming Reassurance Card
        val statusCard = LinearLayout(this).apply {
            orientation = LinearLayout.VERTICAL
            background = KavachTheme.rounded(this@SeniorActivity, KavachTheme.SENIOR_GREEN_BG, 18f, Color.parseColor("#86EFAC"), 1.5f)
            val p = KavachTheme.dp(this@SeniorActivity, 24f)
            setPadding(p, p, p, p)
            gravity = Gravity.CENTER_HORIZONTAL
        }
        val shieldPill = KavachTheme.badge(this, "SHIELD ACTIVE", KavachTheme.SENIOR_GREEN, Color.parseColor("#BBF7D0"))
        statusCard.addView(shieldPill)

        val statusHeading = TextView(this).apply {
            text = "Guarding Your Calls & Messages"
            textSize = 18f
            typeface = Typeface.DEFAULT_BOLD
            setTextColor(KavachTheme.SENIOR_GREEN)
            gravity = Gravity.CENTER
            setPadding(0, KavachTheme.dp(this@SeniorActivity, 10f), 0, KavachTheme.dp(this@SeniorActivity, 4f))
        }
        val statusDesc = TextView(this).apply {
            text = "Scams and fake bank calls are quietly blocked before ringing. You don't need to do anything."
            textSize = 14f
            setTextColor(Color.parseColor("#166534"))
            gravity = Gravity.CENTER
            setLineSpacing(3f, 1.2f)
        }
        statusCard.addView(statusHeading)
        statusCard.addView(statusDesc)
        root.addView(statusCard, marginBot24)

        // Silent background rulepack refresh
        Thread {
            try {
                val client = com.kavach.guardian.net.RelayClient(com.kavach.guardian.BuildConfig.KAVACH_API)
                com.kavach.guardian.net.RulePack.refresh(client, store)
                com.kavach.guardian.net.CommunityShield.sync(client, store)
            } catch (_: Exception) {}
        }.start()

        // Section Title
        val actionTitle = KavachTheme.sectionHeader(this, "Quick Safety Actions")
        actionTitle.gravity = Gravity.CENTER_HORIZONTAL
        root.addView(actionTitle)

        // 3. Primary Action 1: "Ask Kavach / Something Feels Wrong"
        val askCard = LinearLayout(this).apply {
            orientation = LinearLayout.VERTICAL
            background = KavachTheme.rounded(this@SeniorActivity, KavachTheme.SENIOR_AMBER_BG, 16f, Color.parseColor("#FDE68A"), 1.5f)
            val p = KavachTheme.dp(this@SeniorActivity, 20f)
            setPadding(p, p, p, p)
            isClickable = true
            isFocusable = true
            setOnClickListener { showSafetyDialog() }
        }
        val askRow = LinearLayout(this).apply {
            orientation = LinearLayout.HORIZONTAL
            gravity = Gravity.CENTER_VERTICAL
        }
        val askIcon = TextView(this).apply {
            text = "❓"
            textSize = 24f
            setPadding(0, 0, KavachTheme.dp(this@SeniorActivity, 14f), 0)
        }
        val askTextCol = LinearLayout(this).apply {
            orientation = LinearLayout.VERTICAL
            layoutParams = LinearLayout.LayoutParams(0, LinearLayout.LayoutParams.WRAP_CONTENT, 1f)
            addView(TextView(this@SeniorActivity).apply {
                text = "Something Feels Strange?"
                textSize = 17f
                typeface = Typeface.DEFAULT_BOLD
                setTextColor(KavachTheme.SENIOR_AMBER)
            })
            addView(TextView(this@SeniorActivity).apply {
                text = "Got a strange message or call? Tap to verify safely."
                textSize = 13f
                setTextColor(Color.parseColor("#92400E"))
                setPadding(0, KavachTheme.dp(this@SeniorActivity, 2f), 0, 0)
            })
        }
        askRow.addView(askIcon)
        askRow.addView(askTextCol)
        askCard.addView(askRow)
        root.addView(askCard, marginBot16)

        // 4. Primary Action 2: "Alert Family / Need Help"
        val alertCard = LinearLayout(this).apply {
            orientation = LinearLayout.VERTICAL
            background = KavachTheme.rounded(this@SeniorActivity, KavachTheme.SENIOR_RED_BG, 16f, Color.parseColor("#FECACA"), 1.5f)
            val p = KavachTheme.dp(this@SeniorActivity, 20f)
            setPadding(p, p, p, p)
            isClickable = true
            isFocusable = true
            setOnClickListener {
                startActivity(Intent(this@SeniorActivity, SirenActivity::class.java).apply {
                    putExtra("reason", "Senior requested urgent family assistance")
                })
            }
        }
        val alertRow = LinearLayout(this).apply {
            orientation = LinearLayout.HORIZONTAL
            gravity = Gravity.CENTER_VERTICAL
        }
        val alertIcon = TextView(this).apply {
            text = "🚨"
            textSize = 24f
            setPadding(0, 0, KavachTheme.dp(this@SeniorActivity, 14f), 0)
        }
        val alertTextCol = LinearLayout(this).apply {
            orientation = LinearLayout.VERTICAL
            layoutParams = LinearLayout.LayoutParams(0, LinearLayout.LayoutParams.WRAP_CONTENT, 1f)
            addView(TextView(this@SeniorActivity).apply {
                text = "Alert My Family War Room"
                textSize = 17f
                typeface = Typeface.DEFAULT_BOLD
                setTextColor(KavachTheme.SENIOR_RED)
            })
            addView(TextView(this@SeniorActivity).apply {
                text = "Feeling pressured or scared? Tap to notify family instantly."
                textSize = 13f
                setTextColor(Color.parseColor("#991B1B"))
                setPadding(0, KavachTheme.dp(this@SeniorActivity, 2f), 0, 0)
            })
        }
        alertRow.addView(alertIcon)
        alertRow.addView(alertTextCol)
        alertCard.addView(alertRow)
        root.addView(alertCard, marginBot24)

        // 5. Connection Footer
        val hid = store.getString("household_id") ?: ""
        val connectionBadge = TextView(this).apply {
            text = if (hid.isNotEmpty()) "Connected with Family Guardian ✓" else "Pair with son or daughter's device"
            textSize = 13f
            typeface = Typeface.DEFAULT_BOLD
            setTextColor(KavachTheme.SENIOR_MUTED)
            gravity = Gravity.CENTER
            setPadding(0, KavachTheme.dp(this@SeniorActivity, 8f), 0, KavachTheme.dp(this@SeniorActivity, 8f))
            if (hid.isEmpty()) {
                setOnClickListener { startActivity(Intent(this@SeniorActivity, PairingActivity::class.java)) }
            }
        }
        root.addView(connectionBadge)

        val privacyFootnote = TextView(this).apply {
            text = "🔒 Zero Cloud Spying: Audio and private SMS never leave this device."
            textSize = 12f
            setTextColor(Color.parseColor("#A8A29E"))
            gravity = Gravity.CENTER
            setPadding(0, 0, 0, KavachTheme.dp(this@SeniorActivity, 20f))
        }
        root.addView(privacyFootnote)

        setContentView(scroll)
    }

    private fun showSafetyDialog() {
        val options = arrayOf(
            "🏦 Bank Officer asking for OTP to unfreeze account",
            "⚡ Electricity disconnection threat tonight",
            "👮 Police / Customs calling about seized parcel",
            "🧪 Practice test in Scam Lab",
            "⚙️ Device Settings & Re-Pairing"
        )

        AlertDialog.Builder(this)
            .setTitle("What happened?")
            .setItems(options) { _, which ->
                when (which) {
                    0 -> showAdvice(
                        "RUKO! Never Give OTP 🛑",
                        "Banks NEVER call asking for OTPs to unfreeze accounts. " +
                        "This is 100% fraud. Hang up now. Your money is safe as long as you do not share the code."
                    )
                    1 -> showAdvice(
                        "DO NOT PANIC ⚡",
                        "Electricity boards do not cut power at night or demand APK downloads. " +
                        "Do not tap any links or pay over UPI. This is a known scam."
                    )
                    2 -> showAdvice(
                        "Digital Arrest is FAKE 🚨",
                        "Police and CBI never make video calls to arrest citizens or demand secret payments. " +
                        "Stay calm. Disconnect the call and let your family know."
                    )
                    3 -> startActivity(Intent(this, ScamLabActivity::class.java))
                    4 -> showDeviceSettingsDialog()
                }
            }
            .setNegativeButton("Close", null)
            .show()
    }

    private fun showDeviceSettingsDialog() {
        val app = application as KavachApp
        val items = arrayOf(
            "🔗 Pair with Son / Daughter's Device",
            "🔄 Switch Device Role (Parent / Guardian)",
            "🛡️ Test Threat Siren"
        )
        AlertDialog.Builder(this)
            .setTitle("Device Settings")
            .setItems(items) { _, which ->
                when (which) {
                    0 -> startActivity(Intent(this, PairingActivity::class.java))
                    1 -> {
                        app.store.putString("app_role", "")
                        startActivity(Intent(this, RoleSelectionActivity::class.java))
                        finish()
                    }
                    2 -> startActivity(Intent(this, com.kavach.guardian.siren.SirenActivity::class.java).apply {
                        putExtra("reason", "Safety Siren Rehearsal")
                    })
                }
            }
            .setNegativeButton("Back", null)
            .show()
    }

    private fun showAdvice(title: String, body: String) {
        AlertDialog.Builder(this)
            .setTitle(title)
            .setMessage(body)
            .setPositiveButton("I Understand", null)
            .show()
    }
}
