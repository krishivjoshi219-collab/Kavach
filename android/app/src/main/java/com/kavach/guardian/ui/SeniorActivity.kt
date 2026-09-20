package com.kavach.guardian.ui

import android.content.Intent
import android.graphics.Color
import android.graphics.Typeface
import android.os.Bundle
import android.speech.tts.TextToSpeech
import android.view.Gravity
import android.view.View
import android.widget.Button
import android.widget.EditText
import android.widget.HorizontalScrollView
import android.widget.LinearLayout
import android.widget.ScrollView
import android.widget.TextView
import android.widget.Toast
import androidx.appcompat.app.AlertDialog
import androidx.appcompat.app.AppCompatActivity
import com.kavach.guardian.KavachApp
import com.kavach.guardian.screen.RuleEngine
import com.kavach.guardian.siren.SirenActivity
import java.util.Locale

/**
 * Senior Sanctuary Interface:
 * Accessible, calming, senior-first design.
 * Clear visual hierarchy, generous touch targets (64dp), WCAG AAA contrast, zero developer jargon.
 * Features inline bilingual Scam Defense Advisor, instant TTS audio playback, and pre-ring defense status.
 */
class SeniorActivity : AppCompatActivity() {

    private var tts: TextToSpeech? = null
    private var lastSpokenText: String = ""

    override fun onCreate(savedInstanceState: Bundle?) {
        super.onCreate(savedInstanceState)

        val app = application as KavachApp
        val store = app.store

        if (store.getString("onboarded") != "1") {
            startActivity(Intent(this, OnboardingActivity::class.java))
        }

        // Initialize Speech Synthesis for voice guidance in Hindi / Indian English
        tts = TextToSpeech(this) { status ->
            if (status == TextToSpeech.SUCCESS) {
                tts?.language = Locale("en", "IN")
            }
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

        val marginBot12 = LinearLayout.LayoutParams(
            LinearLayout.LayoutParams.MATCH_PARENT,
            LinearLayout.LayoutParams.WRAP_CONTENT
        ).apply { setMargins(0, 0, 0, KavachTheme.dp(this@SeniorActivity, 12f)) }

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
        brandRow.addView(TextView(this).apply {
            text = "🛡️ "
            textSize = 20f
        })
        brandRow.addView(TextView(this).apply {
            text = "Kavach"
            textSize = 20f
            typeface = Typeface.DEFAULT_BOLD
            setTextColor(KavachTheme.SENIOR_TEXT)
        })
        brandRow.addView(TextView(this).apply {
            text = " कवच"
            textSize = 15f
            setTextColor(KavachTheme.SENIOR_MUTED)
            setPadding(KavachTheme.dp(this@SeniorActivity, 4f), 0, 0, 0)
        })
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
            setPadding(0, 0, 0, KavachTheme.dp(this@SeniorActivity, 20f))
        }
        root.addView(subGreeting)

        // 2. Calming Reassurance Card with Live Pulse
        val statusCard = LinearLayout(this).apply {
            orientation = LinearLayout.VERTICAL
            background = KavachTheme.rounded(this@SeniorActivity, KavachTheme.SENIOR_GREEN_BG, 18f, Color.parseColor("#86EFAC"), 1.5f)
            val p = KavachTheme.dp(this@SeniorActivity, 20f)
            setPadding(p, p, p, p)
            gravity = Gravity.CENTER_HORIZONTAL
        }
        val shieldPill = KavachTheme.badge(this, "● SHIELD ACTIVE & SCREENING", KavachTheme.SENIOR_GREEN, Color.parseColor("#BBF7D0"))
        statusCard.addView(shieldPill)

        val statusHeading = TextView(this).apply {
            text = "Pre-Ring Number & SMS Shield"
            textSize = 18f
            typeface = Typeface.DEFAULT_BOLD
            setTextColor(KavachTheme.SENIOR_GREEN)
            gravity = Gravity.CENTER
            setPadding(0, KavachTheme.dp(this@SeniorActivity, 8f), 0, KavachTheme.dp(this@SeniorActivity, 4f))
        }
        val statusDesc = TextView(this).apply {
            text = "Known scam numbers are rejected pre-ring. Suspicious SMS messages are evaluated locally on your phone."
            textSize = 13.5f
            setTextColor(Color.parseColor("#166534"))
            gravity = Gravity.CENTER
            setLineSpacing(3f, 1.2f)
        }
        statusCard.addView(statusHeading)
        statusCard.addView(statusDesc)
        root.addView(statusCard, marginBot20)

        // Silent background rulepack + shield refresh (household list included
        // so a guardian block on one phone protects this phone too).
        Thread {
            try {
                val client = com.kavach.guardian.net.RelayClient(com.kavach.guardian.BuildConfig.KAVACH_API)
                com.kavach.guardian.net.RulePack.refresh(client, store)
                com.kavach.guardian.net.CommunityShield.sync(client, store)
                val hid = store.getString("household_id") ?: ""
                if (hid.isNotEmpty()) {
                    com.kavach.guardian.net.CommunityShield.syncHousehold(client, store, hid)
                }
            } catch (_: Exception) {}
        }.start()

        // 3. Interactive In-App Scam Defense Advisor
        val advisorCard = LinearLayout(this).apply {
            orientation = LinearLayout.VERTICAL
            background = KavachTheme.rounded(this@SeniorActivity, KavachTheme.SENIOR_SURFACE, 18f, KavachTheme.SENIOR_BORDER, 1.5f)
            val p = KavachTheme.dp(this@SeniorActivity, 18f)
            setPadding(p, p, p, p)
        }

        val advisorTitleRow = LinearLayout(this).apply {
            orientation = LinearLayout.HORIZONTAL
            gravity = Gravity.CENTER_VERTICAL
        }
        advisorTitleRow.addView(TextView(this).apply {
            text = "🔍 "
            textSize = 20f
        })
        advisorTitleRow.addView(TextView(this).apply {
            text = "Check a Message or Call"
            textSize = 17f
            typeface = Typeface.DEFAULT_BOLD
            setTextColor(KavachTheme.SENIOR_TEXT)
        })
        advisorCard.addView(advisorTitleRow)

        advisorCard.addView(TextView(this).apply {
            text = "Tap a common threat below, or paste any strange message to verify safety:"
            textSize = 13f
            setTextColor(KavachTheme.SENIOR_MUTED)
            setPadding(0, KavachTheme.dp(this@SeniorActivity, 4f), 0, KavachTheme.dp(this@SeniorActivity, 12f))
        })

        // Quick Preset Chips (Horizontal Scroll)
        val chipsScroll = HorizontalScrollView(this).apply {
            isHorizontalScrollBarEnabled = false
        }
        val chipsRow = LinearLayout(this).apply {
            orientation = LinearLayout.HORIZONTAL
        }

        val inputMsg = EditText(this).apply {
            hint = "Type or paste suspicious message here..."
            textSize = 15f
            setTextColor(KavachTheme.SENIOR_TEXT)
            setHintTextColor(Color.parseColor("#A8A29E"))
            background = KavachTheme.rounded(this@SeniorActivity, Color.parseColor("#F5F2EB"), 12f, Color.parseColor("#E7E3DA"), 1f)
            val px = KavachTheme.dp(this@SeniorActivity, 14f)
            val py = KavachTheme.dp(this@SeniorActivity, 12f)
            setPadding(px, py, px, py)
            minLines = 2
            maxLines = 4
        }

        // Result Container (Updated dynamically)
        val resultCard = LinearLayout(this).apply {
            orientation = LinearLayout.VERTICAL
            visibility = View.GONE
            val p = KavachTheme.dp(this@SeniorActivity, 14f)
            setPadding(p, p, p, p)
        }

        fun evaluateText(textToJudge: String) {
            val t = textToJudge.trim()
            if (t.isEmpty()) return
            inputMsg.setText(t)

            val verdict = RuleEngine.judge(t)
            val hits = RuleEngine.extract(t)

            store.logIncident(verdict.verdict, "senior_checker", t.take(120))

            resultCard.removeAllViews()
            resultCard.visibility = View.VISIBLE

            if (verdict.verdict == "SCAM") {
                resultCard.background = KavachTheme.rounded(this@SeniorActivity, KavachTheme.SENIOR_RED_BG, 14f, Color.parseColor("#FCA5A5"), 1.5f)

                val badge = KavachTheme.badge(this@SeniorActivity, "🛑 FRAUD DETECTED / ख़तरा!", Color.WHITE, KavachTheme.SENIOR_RED)
                resultCard.addView(badge)

                val title = TextView(this@SeniorActivity).apply {
                    text = "RUKO! Never Share OTP or Money"
                    textSize = 16f
                    typeface = Typeface.DEFAULT_BOLD
                    setTextColor(KavachTheme.SENIOR_RED)
                    setPadding(0, KavachTheme.dp(this@SeniorActivity, 8f), 0, KavachTheme.dp(this@SeniorActivity, 4f))
                }
                resultCard.addView(title)

                val advice = TextView(this@SeniorActivity).apply {
                    text = "Banks and police NEVER threaten arrest or demand OTPs over phone. Hang up now — your money is safe as long as you do not share any numbers."
                    textSize = 13.5f
                    setTextColor(Color.parseColor("#7F1D1D"))
                    setLineSpacing(3f, 1.2f)
                    setPadding(0, 0, 0, KavachTheme.dp(this@SeniorActivity, 8f))
                }
                resultCard.addView(advice)

                lastSpokenText = "Ruko! This is a fraud message. Never share OTP or transfer money. Your bank will never call demanding a code."

                if (hits.isNotEmpty()) {
                    val flags = TextView(this@SeniorActivity).apply {
                        text = "Flags detected: " + hits.joinToString(", ") { it.label }
                        textSize = 12f
                        setTextColor(Color.parseColor("#991B1B"))
                        setPadding(0, 0, 0, KavachTheme.dp(this@SeniorActivity, 10f))
                    }
                    resultCard.addView(flags)
                }

                val actionRow = LinearLayout(this@SeniorActivity).apply {
                    orientation = LinearLayout.HORIZONTAL
                }
                val speakBtn = KavachTheme.button(this@SeniorActivity, "🔊 Speak Advice", Color.parseColor("#991B1B"), Color.WHITE, 8f, 38f) {
                    speakAdvice(lastSpokenText)
                }
                val sirenBtn = KavachTheme.button(this@SeniorActivity, "🚨 Alert Family", Color.parseColor("#DC2626"), Color.WHITE, 8f, 38f) {
                    startActivity(Intent(this@SeniorActivity, SirenActivity::class.java).apply {
                        putExtra("reason", "Senior flagged fraud: ${t.take(60)}")
                    })
                }
                val lp1 = LinearLayout.LayoutParams(0, LinearLayout.LayoutParams.WRAP_CONTENT, 1f).apply {
                    setMargins(0, 0, KavachTheme.dp(this@SeniorActivity, 6f), 0)
                }
                val lp2 = LinearLayout.LayoutParams(0, LinearLayout.LayoutParams.WRAP_CONTENT, 1f).apply {
                    setMargins(KavachTheme.dp(this@SeniorActivity, 6f), 0, 0, 0)
                }
                actionRow.addView(speakBtn, lp1)
                actionRow.addView(sirenBtn, lp2)
                resultCard.addView(actionRow)

            } else {
                resultCard.background = KavachTheme.rounded(this@SeniorActivity, KavachTheme.SENIOR_GREEN_BG, 14f, Color.parseColor("#86EFAC"), 1.5f)

                val badge = KavachTheme.badge(this@SeniorActivity, "🟢 LIKELY SAFE / सुरक्षित", Color.WHITE, KavachTheme.SENIOR_GREEN)
                resultCard.addView(badge)

                val title = TextView(this@SeniorActivity).apply {
                    text = "No Threat Signs Detected"
                    textSize = 16f
                    typeface = Typeface.DEFAULT_BOLD
                    setTextColor(KavachTheme.SENIOR_GREEN)
                    setPadding(0, KavachTheme.dp(this@SeniorActivity, 8f), 0, KavachTheme.dp(this@SeniorActivity, 4f))
                }
                resultCard.addView(title)

                val advice = TextView(this@SeniorActivity).apply {
                    text = "No urgency threats, OTP demands, or suspicious APK download links were found in this message."
                    textSize = 13.5f
                    setTextColor(Color.parseColor("#166534"))
                    setLineSpacing(3f, 1.2f)
                }
                resultCard.addView(advice)

                lastSpokenText = "This message looks safe. No fraud keywords or OTP requests were detected."
            }
        }

        fun addChip(label: String, sample: String) {
            val btn = Button(this).apply {
                text = label
                textSize = 12f
                typeface = Typeface.DEFAULT_BOLD
                setTextColor(Color.parseColor("#451A03"))
                background = KavachTheme.rounded(this@SeniorActivity, Color.parseColor("#FEF3C7"), 8f, Color.parseColor("#FDE68A"), 1f)
                val px = KavachTheme.dp(this@SeniorActivity, 10f)
                val py = KavachTheme.dp(this@SeniorActivity, 6f)
                setPadding(px, py, px, py)
                isAllCaps = false
                setOnClickListener { evaluateText(sample) }
            }
            val lp = LinearLayout.LayoutParams(
                LinearLayout.LayoutParams.WRAP_CONTENT,
                LinearLayout.LayoutParams.WRAP_CONTENT
            ).apply { setMargins(0, 0, KavachTheme.dp(this@SeniorActivity, 8f), 0) }
            chipsRow.addView(btn, lp)
        }

        addChip("🏦 Bank OTP Demand", "Dear customer, your bank account is frozen. Immediately share OTP with manager or police will arrest.")
        addChip("⚡ Power Cut Threat", "Electricity power will be disconnected at 9:30 PM tonight. Download bill.apk immediately to avoid blackout.")
        addChip("👮 Digital Arrest", "Crime Branch Delhi. Drugs courier seized with your Aadhaar card. Do not disconnect or police will arrive.")
        addChip("👶 Grandchild Emergency", "Dada, I had an accident and police need urgent fine money on UPI right now.")

        chipsScroll.addView(chipsRow)
        advisorCard.addView(chipsScroll)

        val marginInput = LinearLayout.LayoutParams(
            LinearLayout.LayoutParams.MATCH_PARENT,
            LinearLayout.LayoutParams.WRAP_CONTENT
        ).apply { setMargins(0, KavachTheme.dp(this@SeniorActivity, 12f), 0, KavachTheme.dp(this@SeniorActivity, 12f)) }
        advisorCard.addView(inputMsg, marginInput)

        val checkBtn = KavachTheme.button(this, "🛡️ जांचें / Check with Kavach", KavachTheme.EMERALD_PRO, Color.BLACK, 10f, 48f) {
            evaluateText(inputMsg.text.toString())
        }
        advisorCard.addView(checkBtn)

        val marginResult = LinearLayout.LayoutParams(
            LinearLayout.LayoutParams.MATCH_PARENT,
            LinearLayout.LayoutParams.WRAP_CONTENT
        ).apply { setMargins(0, KavachTheme.dp(this@SeniorActivity, 14f), 0, 0) }
        advisorCard.addView(resultCard, marginResult)

        root.addView(advisorCard, marginBot20)

        // 4. Primary Action 2: "Alert Family / Need Help"
        val alertCard = LinearLayout(this).apply {
            orientation = LinearLayout.VERTICAL
            background = KavachTheme.rounded(this@SeniorActivity, KavachTheme.SENIOR_RED_BG, 16f, Color.parseColor("#FECACA"), 1.5f)
            val p = KavachTheme.dp(this@SeniorActivity, 18f)
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
                text = "Emergency Siren & Family Alert"
                textSize = 17f
                typeface = Typeface.DEFAULT_BOLD
                setTextColor(KavachTheme.SENIOR_RED)
            })
            addView(TextView(this@SeniorActivity).apply {
                text = "Feeling pressured or scared? Tap to sound siren & alert family."
                textSize = 13f
                setTextColor(Color.parseColor("#991B1B"))
                setPadding(0, KavachTheme.dp(this@SeniorActivity, 2f), 0, 0)
            })
        }
        alertRow.addView(alertIcon)
        alertRow.addView(alertTextCol)
        alertCard.addView(alertRow)
        root.addView(alertCard, marginBot20)

        // 5. Connection Footer & Device Settings
        val hid = store.getString("household_id") ?: ""
        val connectionBadge = TextView(this).apply {
            text = if (hid.isNotEmpty()) "Connected with Family Guardian ✓" else "🔗 Pair with son or daughter's device"
            textSize = 13f
            typeface = Typeface.DEFAULT_BOLD
            setTextColor(KavachTheme.SENIOR_MUTED)
            gravity = Gravity.CENTER
            setPadding(0, KavachTheme.dp(this@SeniorActivity, 6f), 0, KavachTheme.dp(this@SeniorActivity, 6f))
            setOnClickListener {
                if (hid.isEmpty()) {
                    startActivity(Intent(this@SeniorActivity, PairingActivity::class.java))
                } else {
                    showDeviceSettingsDialog()
                }
            }
        }
        root.addView(connectionBadge)

        val settingsBtn = TextView(this).apply {
            text = "⚙️ Device Settings & Scam Rehearsal Lab"
            textSize = 12f
            setTextColor(Color.parseColor("#94A3B8"))
            gravity = Gravity.CENTER
            setPadding(0, KavachTheme.dp(this@SeniorActivity, 4f), 0, KavachTheme.dp(this@SeniorActivity, 12f))
            setOnClickListener { showDeviceSettingsDialog() }
        }
        root.addView(settingsBtn)

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

    private fun speakAdvice(text: String) {
        if (text.isEmpty()) return
        try {
            tts?.speak(text, TextToSpeech.QUEUE_FLUSH, null, "KavachSeniorTTS")
            Toast.makeText(this, "🔊 Playing voice guidance...", Toast.LENGTH_SHORT).show()
        } catch (_: Exception) {}
    }

    private fun showDeviceSettingsDialog() {
        val app = application as KavachApp
        val items = arrayOf(
            "🔗 Pair with Son / Daughter's Device",
            "🧪 Practice Test in Scam Defense Lab",
            "🔄 Switch Device Role (Parent / Guardian)",
            "🛡️ Test Threat Siren"
        )
        AlertDialog.Builder(this)
            .setTitle("Settings & Safety Lab")
            .setItems(items) { _, which ->
                when (which) {
                    0 -> startActivity(Intent(this, PairingActivity::class.java))
                    1 -> startActivity(Intent(this, ScamLabActivity::class.java))
                    2 -> {
                        app.store.putString("app_role", "")
                        startActivity(Intent(this, RoleSelectionActivity::class.java))
                        finish()
                    }
                    3 -> startActivity(Intent(this, SirenActivity::class.java).apply {
                        putExtra("reason", "Safety Siren Rehearsal")
                    })
                }
            }
            .setNegativeButton("Back", null)
            .show()
    }

    override fun onDestroy() {
        try {
            tts?.stop()
            tts?.shutdown()
        } catch (_: Exception) {}
        super.onDestroy()
    }
}
