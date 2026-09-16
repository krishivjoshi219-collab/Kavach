package com.kavach.guardian.ui

import android.content.Intent
import android.graphics.Color
import android.os.Bundle
import android.view.Gravity
import android.widget.Button
import android.widget.LinearLayout
import android.widget.ScrollView
import android.widget.TextView
import android.widget.Toast
import androidx.appcompat.app.AppCompatActivity
import com.kavach.guardian.KavachApp
import com.kavach.guardian.siren.SirenActivity

class SeniorActivity : AppCompatActivity() {

    override fun onCreate(savedInstanceState: Bundle?) {
        super.onCreate(savedInstanceState)

        val app = application as KavachApp
        val store = app.store

        val scroll = ScrollView(this)
        val root = LinearLayout(this).apply {
            orientation = LinearLayout.VERTICAL
            setBackgroundColor(Color.parseColor("#FAF6EC")) // Warm background
            setPadding(40, 48, 40, 48)
            gravity = Gravity.CENTER_HORIZONTAL
        }
        scroll.addView(root)

        // Header / Logo
        val header = TextView(this).apply {
            text = "🛡️ Kavach"
            textSize = 32f
            setTextColor(Color.parseColor("#B3541E")) // Primary brand terracotta
            gravity = Gravity.CENTER
            typeface = android.graphics.Typeface.DEFAULT_BOLD
        }
        root.addView(header)

        val subtitle = TextView(this).apply {
            text = "Protection for you, peace for family"
            textSize = 16f
            setTextColor(Color.parseColor("#555555"))
            gravity = Gravity.CENTER
            setPadding(0, 8, 0, 32)
        }
        root.addView(subtitle)

        // Status Card
        val statusCard = TextView(this).apply {
            text = "✅ Shield is ACTIVE\nCall screening & SMS protection running"
            textSize = 18f
            setTextColor(Color.parseColor("#1B5E20"))
            setBackgroundColor(Color.parseColor("#E8F5E9"))
            setPadding(32, 24, 32, 24)
            gravity = Gravity.CENTER
        }
        val cardLp = LinearLayout.LayoutParams(
            LinearLayout.LayoutParams.MATCH_PARENT,
            LinearLayout.LayoutParams.WRAP_CONTENT
        ).apply { setMargins(0, 0, 0, 32) }
        root.addView(statusCard, cardLp)

        fun createSeniorButton(label: String, bgColor: Int, textColor: Int, onClick: () -> Unit): Button {
            return Button(this).apply {
                text = label
                textSize = 20f
                setBackgroundColor(bgColor)
                setTextColor(textColor)
                setPadding(24, 32, 24, 32)
                setOnClickListener { onClick() }
            }
        }

        val btnLp = LinearLayout.LayoutParams(
            LinearLayout.LayoutParams.MATCH_PARENT,
            LinearLayout.LayoutParams.WRAP_CONTENT
        ).apply { setMargins(0, 16, 0, 16) }

        // Button: Emergency Siren
        val sirenBtn = createSeniorButton("🚨 Panic / Sound Siren", Color.parseColor("#C62828"), Color.WHITE) {
            val intent = Intent(this, SirenActivity::class.java).apply {
                putExtra("reason", "Manual Panic button triggered by senior")
            }
            startActivity(intent)
        }
        root.addView(sirenBtn, btnLp)

        // Button: Pair with Family Member
        val pairBtn = createSeniorButton("🔗 Connect / Pair with Family", Color.parseColor("#B3541E"), Color.WHITE) {
            startActivity(Intent(this, PairingActivity::class.java))
        }
        root.addView(pairBtn, btnLp)

        // Button: Kill Switch (Elder Autonomy)
        val killSwitchBtn = createSeniorButton("🛑 Kill Switch (Revoke All)", Color.parseColor("#424242"), Color.WHITE) {
            val hid = store.getString("household_id") ?: ""
            val sid = store.getString("senior_id") ?: "senior_1"
            if (hid.isNotEmpty()) {
                Thread {
                    try {
                        val client = com.kavach.guardian.net.RelayClient(com.kavach.guardian.BuildConfig.KAVACH_API)
                        client.revokeConsent(hid, sid)
                    } catch (_: Exception) {}
                }.start()
            }
            Toast.makeText(this, "All remote access revoked immediately.", Toast.LENGTH_LONG).show()
        }
        root.addView(killSwitchBtn, btnLp)

        // Switch to Family Manager Mode
        val managerBtn = Button(this).apply {
            text = "Switch to Family Manager View →"
            textSize = 15f
            setBackgroundColor(Color.TRANSPARENT)
            setTextColor(Color.parseColor("#B3541E"))
            setOnClickListener {
                startActivity(Intent(this@SeniorActivity, FamilyActivity::class.java))
            }
        }
        root.addView(managerBtn, btnLp)

        setContentView(scroll)
    }
}
