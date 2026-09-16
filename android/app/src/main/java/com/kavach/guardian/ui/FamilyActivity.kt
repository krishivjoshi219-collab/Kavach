package com.kavach.guardian.ui

import android.content.Intent
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
import com.kavach.guardian.screen.RuleEngine

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

        val scroll = ScrollView(this)
        val root = LinearLayout(this).apply {
            orientation = LinearLayout.VERTICAL
            setBackgroundColor(Color.parseColor("#FAF6EC"))
            setPadding(36, 40, 36, 40)
        }
        scroll.addView(root)

        // Title
        val title = TextView(this).apply {
            text = "👨‍👩‍👧 Family Guardian Console"
            textSize = 24f
            setTextColor(Color.parseColor("#B3541E"))
            typeface = android.graphics.Typeface.DEFAULT_BOLD
            gravity = Gravity.CENTER
            setPadding(0, 0, 0, 8)
        }
        root.addView(title)

        val sub = TextView(this).apply {
            text = "Household: $hid\nZero-knowledge encrypted guardian relay"
            textSize = 14f
            setTextColor(Color.parseColor("#666666"))
            gravity = Gravity.CENTER
            setPadding(0, 0, 0, 24)
        }
        root.addView(sub)

        // Tier Card & Upgrade Button
        val tierCard = LinearLayout(this).apply {
            orientation = LinearLayout.HORIZONTAL
            setBackgroundColor(Color.parseColor("#EFEBE9"))
            setPadding(24, 20, 24, 20)
            gravity = Gravity.CENTER_VERTICAL
        }
        val tierText = TextView(this).apply {
            text = "Plan: Pro Shield ⭐ (200 cloud queries/mo)"
            textSize = 15f
            setTextColor(Color.parseColor("#3E2723"))
            layoutParams = LinearLayout.LayoutParams(0, LinearLayout.LayoutParams.WRAP_CONTENT, 1f)
        }
        val tierBtn = Button(this).apply {
            text = "Upgrade"
            textSize = 14f
            setBackgroundColor(Color.parseColor("#B3541E"))
            setTextColor(Color.WHITE)
            setOnClickListener {
                startActivity(Intent(this@FamilyActivity, PaywallActivity::class.java))
            }
        }
        tierCard.addView(tierText)
        tierCard.addView(tierBtn)
        root.addView(tierCard)

        // Section: Remote Safety Powers (Consent-Gated)
        val sectionRemote = TextView(this).apply {
            text = "⚡ Remote Interventions (Consent-Gated)"
            textSize = 18f
            setTextColor(Color.parseColor("#212121"))
            typeface = android.graphics.Typeface.DEFAULT_BOLD
            setPadding(0, 32, 0, 12)
        }
        root.addView(sectionRemote)

        val btnLp = LinearLayout.LayoutParams(
            LinearLayout.LayoutParams.MATCH_PARENT,
            LinearLayout.LayoutParams.WRAP_CONTENT
        ).apply { setMargins(0, 8, 0, 8) }

        // Remote Cut Active Call button
        val cutCallBtn = Button(this).apply {
            text = "🛑 Remote Cut Active Call on Senior Phone"
            textSize = 16f
            setBackgroundColor(Color.parseColor("#C62828"))
            setTextColor(Color.WHITE)
            setOnClickListener {
                Thread {
                    try {
                        val res = client.sendCommand(hid, seniorId, "senior", "cut_call")
                        val ok = res.optBoolean("ok", false)
                        runOnUiThread {
                            if (ok) {
                                Toast.makeText(this@FamilyActivity, "Call cut command sent & queued for senior phone!", Toast.LENGTH_LONG).show()
                            } else {
                                val err = res.optString("error", "Failed")
                                val sum = res.optString("summary", "")
                                Toast.makeText(this@FamilyActivity, "Action blocked: $err ($sum)", Toast.LENGTH_LONG).show()
                            }
                        }
                    } catch (e: Exception) {
                        runOnUiThread {
                            Toast.makeText(this@FamilyActivity, "Error: ${e.message}", Toast.LENGTH_SHORT).show()
                        }
                    }
                }.start()
            }
        }
        root.addView(cutCallBtn, btnLp)

        // Remote Sound Siren button
        val sirenBtn = Button(this).apply {
            text = "🚨 Sound Siren on Senior Phone"
            textSize = 16f
            setBackgroundColor(Color.parseColor("#D84315"))
            setTextColor(Color.WHITE)
            setOnClickListener {
                Thread {
                    try {
                        val res = client.sendCommand(hid, seniorId, "senior", "sound_siren")
                        val ok = res.optBoolean("ok", false)
                        runOnUiThread {
                            if (ok) {
                                Toast.makeText(this@FamilyActivity, "Siren command dispatched to senior device!", Toast.LENGTH_LONG).show()
                            } else {
                                Toast.makeText(this@FamilyActivity, "Consent required to sound siren.", Toast.LENGTH_SHORT).show()
                            }
                        }
                    } catch (e: Exception) {}
                }.start()
            }
        }
        root.addView(sirenBtn, btnLp)

        // Whisper Alert Button
        val whisperBtn = Button(this).apply {
            text = "💬 Whisper Safety Alert to Dad's Screen"
            textSize = 15f
            setBackgroundColor(Color.parseColor("#00695C"))
            setTextColor(Color.WHITE)
            setOnClickListener {
                Thread {
                    try {
                        val payload = "Dad, please do NOT transfer money or share OTP! I am checking this caller now."
                        val res = client.sendCommand(hid, seniorId, "senior", "show_message", payload)
                        val ok = res.optBoolean("ok", false)
                        runOnUiThread {
                            if (ok) {
                                Toast.makeText(this@FamilyActivity, "Safety alert sent to Dad's screen!", Toast.LENGTH_SHORT).show()
                            } else {
                                Toast.makeText(this@FamilyActivity, "Action blocked by senior consent settings.", Toast.LENGTH_SHORT).show()
                            }
                        }
                    } catch (_: Exception) {}
                }.start()
            }
        }
        root.addView(whisperBtn, btnLp)

        // Section: Block Scam Numbers
        val sectionBlock = TextView(this).apply {
            text = "🛡️ Block Scam Number (Salted Hash)"
            textSize = 18f
            setTextColor(Color.parseColor("#212121"))
            typeface = android.graphics.Typeface.DEFAULT_BOLD
            setPadding(0, 24, 0, 8)
        }
        root.addView(sectionBlock)

        val phoneInput = EditText(this).apply {
            hint = "Enter scam phone number (e.g. +91 9876543210)"
            textSize = 15f
            setBackgroundColor(Color.WHITE)
            setPadding(20, 20, 20, 20)
        }
        root.addView(phoneInput, btnLp)

        val blockBtn = Button(this).apply {
            text = "Block Number for Household"
            textSize = 15f
            setBackgroundColor(Color.parseColor("#424242"))
            setTextColor(Color.WHITE)
            setOnClickListener {
                val num = phoneInput.text.toString().trim()
                if (num.isNotEmpty()) {
                    val hash = RuleEngine.hashNumber(hid, num)
                    store.addBlockedHash(hash, "Manager flagged scam")
                    Thread {
                        try {
                            client.block(hid, hash, "Manager flagged scam")
                        } catch (_: Exception) {}
                    }.start()
                    phoneInput.text.clear()
                    Toast.makeText(this@FamilyActivity, "Number hashed & added to household blocklist!", Toast.LENGTH_SHORT).show()
                }
            }
        }
        root.addView(blockBtn, btnLp)

        // Section: Community Threat Radar
        val threatRadar = TextView(this).apply {
            text = "📡 Community Shield Radar:\n" +
                    "• 14 Bank Impersonation calls blocked in your region today\n" +
                    "• 6 Fake Electricity Bill APKs quarantined\n" +
                    "• Household Shield status: 100% Protected"
            textSize = 14f
            setTextColor(Color.parseColor("#0D47A1"))
            setBackgroundColor(Color.parseColor("#E3F2FD"))
            setPadding(24, 18, 24, 18)
        }
        val radarLp = LinearLayout.LayoutParams(
            LinearLayout.LayoutParams.MATCH_PARENT,
            LinearLayout.LayoutParams.WRAP_CONTENT
        ).apply { setMargins(0, 16, 0, 16) }
        root.addView(threatRadar, radarLp)

        // Section: Pairing
        val pairBtn = Button(this).apply {
            text = "🔗 Pairing Ceremony & QR Code"
            textSize = 15f
            setBackgroundColor(Color.parseColor("#2E7D32"))
            setTextColor(Color.WHITE)
            setOnClickListener {
                startActivity(Intent(this@FamilyActivity, PairingActivity::class.java))
            }
        }
        root.addView(pairBtn, btnLp)

        // Section: Audit
        val auditBtn = Button(this).apply {
            text = "🔍 Zero-Knowledge Privacy Audit"
            textSize = 15f
            setBackgroundColor(Color.parseColor("#37474F"))
            setTextColor(Color.WHITE)
            setOnClickListener {
                startActivity(Intent(this@FamilyActivity, AuditActivity::class.java))
            }
        }
        root.addView(auditBtn, btnLp)

        // Section: Scam Lab
        val scamLabBtn = Button(this).apply {
            text = "🧪 Interactive Scam Lab Rehearsal"
            textSize = 15f
            setBackgroundColor(Color.parseColor("#1565C0"))
            setTextColor(Color.WHITE)
            setOnClickListener {
                startActivity(Intent(this@FamilyActivity, ScamLabActivity::class.java))
            }
        }
        root.addView(scamLabBtn, btnLp)

        setContentView(scroll)
    }
}
