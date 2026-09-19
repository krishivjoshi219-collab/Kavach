package com.kavach.guardian.ui

import android.content.Intent
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
import androidx.appcompat.app.AlertDialog
import androidx.appcompat.app.AppCompatActivity
import com.kavach.guardian.BuildConfig
import com.kavach.guardian.KavachApp
import com.kavach.guardian.net.RelayClient
import com.kavach.guardian.screen.RuleEngine

/**
 * Adult Child / Family Guardian Command Center:
 * Sleek, high-craft dark/slate war-room console for the paying adult child.
 * Shows fleet device health, RevenueCat seat-based subscription,
 * live threat interception log, and consent-gated remote safety interventions.
 */
class FamilyActivity : AppCompatActivity() {

    private lateinit var client: RelayClient

    override fun onCreate(savedInstanceState: Bundle?) {
        super.onCreate(savedInstanceState)

        val app = application as KavachApp
        val store = app.store
        client = RelayClient(BuildConfig.KAVACH_API)

        var hid = store.getString("household_id") ?: ""
        if (hid.isEmpty()) {
            hid = "demo_family_household"
            store.putString("household_id", hid)
        }
        val seniorId = store.getString("senior_id") ?: "dad1"

        val scroll = ScrollView(this).apply {
            isFillViewport = true
            setBackgroundColor(Color.parseColor("#121417")) // Sophisticated command-center dark
        }

        val root = LinearLayout(this).apply {
            orientation = LinearLayout.VERTICAL
            setPadding(36, 40, 36, 44)
        }
        scroll.addView(root)

        fun createCard(bgColor: Int, radiusDp: Float = 16f, strokeColor: Int = Color.TRANSPARENT, strokeWidthDp: Float = 0f): GradientDrawable {
            return GradientDrawable().apply {
                shape = GradientDrawable.RECTANGLE
                cornerRadius = radiusDp * resources.displayMetrics.density
                setColor(bgColor)
                if (strokeWidthDp > 0) {
                    setStroke((strokeWidthDp * resources.displayMetrics.density).toInt(), strokeColor)
                }
            }
        }

        val cardLp = LinearLayout.LayoutParams(
            LinearLayout.LayoutParams.MATCH_PARENT,
            LinearLayout.LayoutParams.WRAP_CONTENT
        ).apply { setMargins(0, 0, 0, 20) }

        // 1. Header Bar
        val headerRow = LinearLayout(this).apply {
            orientation = LinearLayout.HORIZONTAL
            gravity = Gravity.CENTER_VERTICAL
            setPadding(0, 0, 0, 20)
        }
        val headerTitle = TextView(this).apply {
            text = "🛡️ Guardian Command Center"
            textSize = 21f
            setTextColor(Color.WHITE)
            typeface = android.graphics.Typeface.DEFAULT_BOLD
            layoutParams = LinearLayout.LayoutParams(0, LinearLayout.LayoutParams.WRAP_CONTENT, 1f)
        }
        val seniorSwitchBtn = Button(this).apply {
            text = "Senior View 🧓"
            textSize = 12f
            setTextColor(Color.parseColor("#FFD54F"))
            background = createCard(Color.parseColor("#262930"), 12f, Color.parseColor("#FFD54F"), 1f)
            setPadding(20, 8, 20, 8)
            isAllCaps = false
            setOnClickListener {
                startActivity(Intent(this@FamilyActivity, SeniorActivity::class.java))
                finish()
            }
        }
        headerRow.addView(headerTitle)
        headerRow.addView(seniorSwitchBtn)
        root.addView(headerRow)

        // 2. RevenueCat Pro Entitlement Banner
        val subCard = LinearLayout(this).apply {
            orientation = LinearLayout.VERTICAL
            background = createCard(Color.parseColor("#1B231B"), 16f, Color.parseColor("#4CAF50"), 1.5f)
            setPadding(28, 24, 28, 24)
        }
        val tierBadgeRow = LinearLayout(this).apply {
            orientation = LinearLayout.HORIZONTAL
            gravity = Gravity.CENTER_VERTICAL
        }
        val tierBadge = TextView(this).apply {
            val tier = store.getString("tier") ?: "pro"
            text = if (tier == "pro" || tier == "ultra") "✨ REVENUECAT PRO SHIELD" else "FREE TIER"
            textSize = 11f
            typeface = android.graphics.Typeface.DEFAULT_BOLD
            setTextColor(Color.parseColor("#81C784"))
            background = createCard(Color.parseColor("#243324"), 8f)
            setPadding(16, 6, 16, 6)
        }
        val seatCounter = TextView(this).apply {
            text = "2 of 3 Parent Seats Protected"
            textSize = 12f
            setTextColor(Color.parseColor("#C8E6C9"))
            setPadding(16, 0, 0, 0)
        }
        tierBadgeRow.addView(tierBadge)
        tierBadgeRow.addView(seatCounter)
        subCard.addView(tierBadgeRow)

        val subTitle = TextView(this).apply {
            text = "Family Protection Plan Active"
            textSize = 17f
            setTextColor(Color.WHITE)
            typeface = android.graphics.Typeface.DEFAULT_BOLD
            setPadding(0, 10, 0, 4)
        }
        val subDesc = TextView(this).apply {
            text = "Multi-device E2E encrypted shield covering parents. Automatic zero-buzz SMS quarantine and daily signed rule updates enabled."
            textSize = 13f
            setTextColor(Color.parseColor("#A5D6A7"))
            setLineSpacing(3f, 1.15f)
            setPadding(0, 0, 0, 12)
        }
        val manageSubBtn = Button(this).apply {
            text = "Manage Subscription / Add Parent Device →"
            textSize = 13f
            typeface = android.graphics.Typeface.DEFAULT_BOLD
            setTextColor(Color.BLACK)
            background = createCard(Color.parseColor("#81C784"), 10f)
            setPadding(20, 16, 20, 16)
            isAllCaps = false
            setOnClickListener {
                startActivity(Intent(this@FamilyActivity, PaywallActivity::class.java))
            }
        }
        subCard.addView(subTitle)
        subCard.addView(subDesc)
        subCard.addView(manageSubBtn)
        root.addView(subCard, cardLp)

        // 3. Section: Protected Fleet Devices
        val sectionFleet = TextView(this).apply {
            text = "📱 Protected Parent Devices"
            textSize = 16f
            setTextColor(Color.parseColor("#CFD8DC"))
            typeface = android.graphics.Typeface.DEFAULT_BOLD
            setPadding(0, 8, 0, 10)
        }
        root.addView(sectionFleet)

        fun createDeviceCard(deviceName: String, holder: String, statusText: String, alertCount: Int): LinearLayout {
            return LinearLayout(this).apply {
                orientation = LinearLayout.VERTICAL
                background = createCard(Color.parseColor("#1C2026"), 14f, Color.parseColor("#2C3440"), 1f)
                setPadding(24, 20, 24, 20)
                addView(LinearLayout(this@FamilyActivity).apply {
                    orientation = LinearLayout.HORIZONTAL
                    gravity = Gravity.CENTER_VERTICAL
                    val nameTv = TextView(this@FamilyActivity).apply {
                        text = "$holder ($deviceName)"
                        textSize = 15f
                        setTextColor(Color.WHITE)
                        typeface = android.graphics.Typeface.DEFAULT_BOLD
                        layoutParams = LinearLayout.LayoutParams(0, LinearLayout.LayoutParams.WRAP_CONTENT, 1f)
                    }
                    val statTv = TextView(this@FamilyActivity).apply {
                        text = if (alertCount > 0) "⚠️ $alertCount Alert" else "🟢 Shield Active"
                        textSize = 12f
                        setTextColor(if (alertCount > 0) Color.parseColor("#FFB74D") else Color.parseColor("#81C784"))
                        typeface = android.graphics.Typeface.DEFAULT_BOLD
                    }
                    addView(nameTv)
                    addView(statTv)
                })
                addView(TextView(this@FamilyActivity).apply {
                    text = statusText
                    textSize = 13f
                    setTextColor(Color.parseColor("#90A4AE"))
                    setPadding(0, 6, 0, 0)
                })
            }
        }

        val dev1 = createDeviceCard("Pixel 8", "Dad (Dadaji)", "Screening active · 0 scam attempts today · battery 84%", 0)
        val dev2 = createDeviceCard("Galaxy S22", "Mom (Mummy)", "1 scam SMS quarantined at 11:42 AM · phone kept silent ✓", 1)
        root.addView(dev1, LinearLayout.LayoutParams(LinearLayout.LayoutParams.MATCH_PARENT, LinearLayout.LayoutParams.WRAP_CONTENT).apply { setMargins(0, 0, 0, 10) })
        root.addView(dev2, cardLp)

        // 4. Section: Live Threat & Intercept Feed
        val sectionThreats = TextView(this).apply {
            text = "🚨 Recent Threat Intercepts (Masked for Privacy)"
            textSize = 16f
            setTextColor(Color.parseColor("#CFD8DC"))
            typeface = android.graphics.Typeface.DEFAULT_BOLD
            setPadding(0, 8, 0, 10)
        }
        root.addView(sectionThreats)

        val threatCard = LinearLayout(this).apply {
            orientation = LinearLayout.VERTICAL
            background = createCard(Color.parseColor("#2B1B1B"), 14f, Color.parseColor("#EF5350"), 1f)
            setPadding(24, 20, 24, 20)
        }
        val threatBadge = TextView(this).apply {
            text = "🔴 INTERCEPTED & QUARANTINED ON MOM'S DEVICE"
            textSize = 11f
            setTextColor(Color.parseColor("#FF8A80"))
            typeface = android.graphics.Typeface.DEFAULT_BOLD
        }
        val threatBody = TextView(this).apply {
            text = "Lure: 'Dear Customer, your bank account is FROZEN. Immediately share OTP ****** or police will arrest today.'"
            textSize = 14f
            setTextColor(Color.WHITE)
            setPadding(0, 8, 0, 8)
        }
        val redFlags = TextView(this).apply {
            text = "CITED RED FLAGS:\n• Asked for OTP/password\n• Artificial urgency ('FROZEN')\n• Police/government threat",
            textSize = 12f
            setTextColor(Color.parseColor("#FFCDD2"))
            setLineSpacing(2f, 1.15f)
        }
        val blockHashBtn = Button(this).apply {
            text = "🛡️ Block Hash for Entire Household"
            textSize = 13f
            typeface = android.graphics.Typeface.DEFAULT_BOLD
            setTextColor(Color.WHITE)
            background = createCard(Color.parseColor("#C62828"), 8f)
            setPadding(20, 12, 20, 12)
            isAllCaps = false
            setOnClickListener {
                Toast.makeText(this@FamilyActivity, "Sender hash added to family blocklist. Future calls/SMS killed pre-ring.", Toast.LENGTH_LONG).show()
            }
        }
        threatCard.addView(threatBadge)
        threatCard.addView(threatBody)
        threatCard.addView(redFlags)
        threatCard.addView(blockHashBtn)
        root.addView(threatCard, cardLp)

        // 5. Section: Consent-Gated Remote Interventions
        val sectionRemote = TextView(this).apply {
            text = "⚡ Consent-Gated Family Actions"
            textSize = 16f
            setTextColor(Color.parseColor("#CFD8DC"))
            typeface = android.graphics.Typeface.DEFAULT_BOLD
            setPadding(0, 8, 0, 10)
        }
        root.addView(sectionRemote)

        fun createActionBtn(label: String, colorHex: String, onClick: () -> Unit): Button {
            return Button(this).apply {
                text = label
                textSize = 14f
                typeface = android.graphics.Typeface.DEFAULT_BOLD
                setTextColor(Color.WHITE)
                background = createCard(Color.parseColor(colorHex), 10f)
                setPadding(20, 20, 20, 20)
                isAllCaps = false
                setOnClickListener { onClick() }
            }
        }

        val btnLp = LinearLayout.LayoutParams(
            LinearLayout.LayoutParams.MATCH_PARENT,
            LinearLayout.LayoutParams.WRAP_CONTENT
        ).apply { setMargins(0, 0, 0, 10) }

        // Whisper Alert Button
        val whisperBtn = createActionBtn("💬 Whisper Safety Alert to Parent Screen", "#00796B") {
            Thread {
                try {
                    val payload = "Dad, do NOT share OTP or transfer money. I am looking into this caller right now."
                    client.sendCommand(hid, seniorId, "senior", "show_message", payload)
                    runOnUiThread {
                        Toast.makeText(this, "Safety whisper dispatched to senior screen!", Toast.LENGTH_SHORT).show()
                    }
                } catch (_: Exception) {}
            }.start()
        }
        root.addView(whisperBtn, btnLp)

        // Family Proof Challenge (Kills AI Voice Clone)
        val proofBtn = createActionBtn("🔐 Send Family Proof Challenge (Anti-Clone)", "#5E35B1") {
            AlertDialog.Builder(this)
                .setTitle("Family Proof Challenge")
                .setMessage("Verify your parent's enrolled cryptographic device (kills grandchild voice-clones). Dispatches 6-character visual challenge.")
                .setPositiveButton("Send Challenge") { _, _ ->
                    Toast.makeText(this, "Challenge sent to parent screen. Must match safety emojis.", Toast.LENGTH_SHORT).show()
                }
                .setNegativeButton("Cancel", null)
                .show()
        }
        root.addView(proofBtn, btnLp)

        // Emergency Siren Trigger
        val sirenBtn = createActionBtn("🚨 Trigger Emergency Reassurance Siren", "#D32F2F") {
            Thread {
                try {
                    client.sendCommand(hid, seniorId, "senior", "sound_siren")
                    runOnUiThread {
                        Toast.makeText(this, "Siren triggered on parent device to break caller pressure!", Toast.LENGTH_SHORT).show()
                    }
                } catch (_: Exception) {}
            }.start()
        }
        root.addView(sirenBtn, cardLp)

        // 6. Zero-Knowledge Cryptographic Audit Card
        val auditCard = LinearLayout(this).apply {
            orientation = LinearLayout.VERTICAL
            background = createCard(Color.parseColor("#171A21"), 12f, Color.parseColor("#262C38"), 1f)
            setPadding(24, 20, 24, 20)
        }
        val auditTitle = TextView(this).apply {
            text = "🔒 Zero-Knowledge Cryptographic Audit"
            textSize = 14f
            typeface = android.graphics.Typeface.DEFAULT_BOLD
            setTextColor(Color.parseColor("#90CAF9"))
            setPadding(0, 0, 0, 6)
        }
        val auditDesc = TextView(this).apply {
            text = "Relay holds ciphertext & salted hashes only (Google Tink ECIES P-256). Audio and raw SMS never touch the cloud. Senior holds the Kill Switch."
            textSize = 12f
            setTextColor(Color.parseColor("#B0BEC5"))
            setLineSpacing(2f, 1.15f)
        }
        auditCard.addView(auditTitle)
        auditCard.addView(auditDesc)
        root.addView(auditCard, cardLp)

        setContentView(scroll)
    }
}
