package com.kavach.guardian.ui

import android.content.Intent
import android.graphics.Color
import android.graphics.drawable.GradientDrawable
import android.os.Bundle
import android.view.Gravity
import android.view.View
import android.widget.Button
import android.widget.LinearLayout
import android.widget.ScrollView
import android.widget.TextView
import android.widget.Toast
import androidx.appcompat.app.AlertDialog
import androidx.appcompat.app.AppCompatActivity
import com.kavach.guardian.KavachApp
import com.kavach.guardian.siren.SirenActivity

/**
 * Senior Sanctuary View:
 * Calm, dignified, senior-first interface.
 * Zero developer jargon. High contrast, large fonts, simple 1-tap safety reassurance.
 */
class SeniorActivity : AppCompatActivity() {

    override fun onCreate(savedInstanceState: Bundle?) {
        super.onCreate(savedInstanceState)

        val app = application as KavachApp
        val store = app.store

        // First-run onboarding
        if (store.getString("onboarded") != "1") {
            startActivity(Intent(this, OnboardingActivity::class.java))
        }

        val scroll = ScrollView(this).apply {
            isFillViewport = true
            setBackgroundColor(Color.parseColor("#FAF6EC")) // Warm cream
        }

        val root = LinearLayout(this).apply {
            orientation = LinearLayout.VERTICAL
            setPadding(44, 48, 44, 48)
            gravity = Gravity.CENTER_HORIZONTAL
        }
        scroll.addView(root)

        fun createRoundedDrawable(bgColor: Int, cornerRadiusDp: Float = 18f, strokeColor: Int = Color.TRANSPARENT, strokeWidthPx: Int = 0): GradientDrawable {
            return GradientDrawable().apply {
                shape = GradientDrawable.RECTANGLE
                cornerRadius = cornerRadiusDp * resources.displayMetrics.density
                setColor(bgColor)
                if (strokeWidthPx > 0) {
                    setStroke(strokeWidthPx, strokeColor)
                }
            }
        }

        // 1. Top Gentle Greeting
        val greeting = TextView(this).apply {
            text = "Namaste 🙏"
            textSize = 28f
            setTextColor(Color.parseColor("#9A3D0C"))
            gravity = Gravity.CENTER
            typeface = android.graphics.Typeface.DEFAULT_BOLD
        }
        root.addView(greeting)

        val subGreeting = TextView(this).apply {
            text = "Aapka Phone Surakshit Hai • Your Phone is Safe"
            textSize = 15f
            setTextColor(Color.parseColor("#6D5D50"))
            gravity = Gravity.CENTER
            setPadding(0, 6, 0, 28)
        }
        root.addView(subGreeting)

        // 2. Large Peaceful Green Status Card
        val statusCard = LinearLayout(this).apply {
            orientation = LinearLayout.VERTICAL
            background = createRoundedDrawable(Color.parseColor("#E6F4EC"), 20f, Color.parseColor("#A8DFBC"), 2)
            setPadding(36, 32, 36, 32)
            gravity = Gravity.CENTER
        }
        val statusIcon = TextView(this).apply {
            text = "🛡️"
            textSize = 40f
            gravity = Gravity.CENTER
        }
        val statusTitle = TextView(this).apply {
            text = "Kavach is Guarding You"
            textSize = 22f
            setTextColor(Color.parseColor("#1B5E20"))
            typeface = android.graphics.Typeface.DEFAULT_BOLD
            gravity = Gravity.CENTER
            setPadding(0, 8, 0, 6)
        }
        val statusDesc = TextView(this).apply {
            text = "Scam calls and fake bank messages are quietly blocked before your phone rings.\nRelax and enjoy your day."
            textSize = 15f
            setTextColor(Color.parseColor("#2E7D32"))
            gravity = Gravity.CENTER
            setLineSpacing(4f, 1.15f)
        }
        statusCard.addView(statusIcon)
        statusCard.addView(statusTitle)
        statusCard.addView(statusDesc)

        val cardLp = LinearLayout.LayoutParams(
            LinearLayout.LayoutParams.MATCH_PARENT,
            LinearLayout.LayoutParams.WRAP_CONTENT
        ).apply { setMargins(0, 0, 0, 28) }
        root.addView(statusCard, cardLp)

        // Background sync: silent rule updates
        Thread {
            try {
                val client = com.kavach.guardian.net.RelayClient(com.kavach.guardian.BuildConfig.KAVACH_API)
                com.kavach.guardian.net.RulePack.refresh(client, store)
                com.kavach.guardian.net.CommunityShield.sync(client, store)
            } catch (_: Exception) {}
        }.start()

        // 3. Action Card 1: "Something Feels Strange / Ask Kavach"
        val askCard = LinearLayout(this).apply {
            orientation = LinearLayout.VERTICAL
            background = createRoundedDrawable(Color.parseColor("#FFF3E0"), 20f, Color.parseColor("#FFCC80"), 2)
            setPadding(32, 28, 32, 28)
            isClickable = true
            isFocusable = true
            setOnClickListener {
                showQuickSafetyGuidance()
            }
        }
        val askTitle = TextView(this).apply {
            text = "❓ Something Feels Strange?"
            textSize = 21f
            setTextColor(Color.parseColor("#B3541E"))
            typeface = android.graphics.Typeface.DEFAULT_BOLD
            gravity = Gravity.CENTER_HORIZONTAL
        }
        val askSubtitle = TextView(this).apply {
            text = "Got a strange call or SMS? Tap here. We will check it together calmly."
            textSize = 15f
            setTextColor(Color.parseColor("#795548"))
            gravity = Gravity.CENTER_HORIZONTAL
            setPadding(0, 6, 0, 0)
        }
        askCard.addView(askTitle)
        askCard.addView(askSubtitle)
        root.addView(askCard, cardLp)

        // 4. Action Card 2: "Need Help / Call Family"
        val helpCard = LinearLayout(this).apply {
            orientation = LinearLayout.VERTICAL
            background = createRoundedDrawable(Color.parseColor("#FFEBEE"), 20f, Color.parseColor("#FFCDD2"), 2)
            setPadding(32, 28, 32, 28)
            isClickable = true
            isFocusable = true
            setOnClickListener {
                val intent = Intent(this@SeniorActivity, SirenActivity::class.java).apply {
                    putExtra("reason", "Senior requested urgent family assistance")
                }
                startActivity(intent)
            }
        }
        val helpTitle = TextView(this).apply {
            text = "🚨 Alert My Family / Need Help"
            textSize = 21f
            setTextColor(Color.parseColor("#C62828"))
            typeface = android.graphics.Typeface.DEFAULT_BOLD
            gravity = Gravity.CENTER_HORIZONTAL
        }
        val helpSubtitle = TextView(this).apply {
            text = "Press if you feel pressured or scared. Sounds alert & pings your family war room."
            textSize = 15f
            setTextColor(Color.parseColor("#B71C1C"))
            gravity = Gravity.CENTER_HORIZONTAL
            setPadding(0, 6, 0, 0)
        }
        helpCard.addView(helpTitle)
        helpCard.addView(helpSubtitle)
        root.addView(helpCard, cardLp)

        // 5. Reassurance & Family Connection
        val pairingStatus = TextView(this).apply {
            val hid = store.getString("household_id") ?: ""
            text = if (hid.isNotEmpty()) "👨‍👩‍👧 Paired with Family: Your family is connected and watching over this phone."
                   else "🔗 Tap to pair with your son/daughter's phone"
            textSize = 14f
            setTextColor(Color.parseColor("#5D4037"))
            gravity = Gravity.CENTER
            setPadding(16, 8, 16, 16)
            if (hid.isEmpty()) {
                setOnClickListener { startActivity(Intent(this@SeniorActivity, PairingActivity::class.java)) }
            }
        }
        root.addView(pairingStatus)

        // 6. Dignified Privacy Note
        val privacyNote = TextView(this).apply {
            text = "🔒 Zero Cloud Spying: Your personal calls and chats never leave this phone."
            textSize = 13f
            setTextColor(Color.parseColor("#8D6E63"))
            gravity = Gravity.CENTER
            setPadding(16, 0, 16, 24)
        }
        root.addView(privacyNote)

        // 7. Subtle Switcher to Adult Child / Guardian Console
        val guardianSwitch = Button(this).apply {
            text = "⚙️ Family Guardian Console (Adult Child Mode) →"
            textSize = 14f
            setTextColor(Color.parseColor("#9A3D0C"))
            setBackgroundColor(Color.TRANSPARENT)
            isAllCaps = false
            setOnClickListener {
                startActivity(Intent(this@SeniorActivity, FamilyActivity::class.java))
            }
        }
        root.addView(guardianSwitch)

        setContentView(scroll)
    }

    private fun showQuickSafetyGuidance() {
        val options = arrayOf(
            "🏦 Bank Officer asking for OTP to unfreeze account",
            "⚡ Electricity Bill cut tonight warning",
            "👮 Police / Customs calling about a courier parcel",
            "🧪 Practice a test scam (Scam Lab)"
        )

        AlertDialog.Builder(this)
            .setTitle("What happened?")
            .setItems(options) { _, which ->
                when (which) {
                    0 -> showAdviceDialog(
                        "RUKO! Do not give OTP 🛑",
                        "Banks NEVER ask for OTP over the phone to unfreeze accounts. " +
                        "This is 100% a scam. Hang up immediately. Your money is safe as long as you do not share the code."
                    )
                    1 -> showAdviceDialog(
                        "DO NOT PANIC ⚡",
                        "Electricity boards do not disconnect power at night or ask you to install APK files. " +
                        "Do not click any link or send money over UPI. This is a common fake message."
                    )
                    2 -> showAdviceDialog(
                        "Digital Arrest is FAKE 🚨",
                        "Police and CBI never make video calls to 'arrest' people or demand secret money transfers. " +
                        "Stay calm. They are lying. Hang up and tell your family."
                    )
                    3 -> startActivity(Intent(this, ScamLabActivity::class.java))
                }
            }
            .setNegativeButton("Cancel", null)
            .show()
    }

    private fun showAdviceDialog(title: String, body: String) {
        AlertDialog.Builder(this)
            .setTitle(title)
            .setMessage(body)
            .setPositiveButton("I Understand, Thank You", null)
            .show()
    }
}
