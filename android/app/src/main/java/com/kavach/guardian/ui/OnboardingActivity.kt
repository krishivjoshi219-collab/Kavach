package com.kavach.guardian.ui

import android.content.Intent
import android.graphics.Color
import android.graphics.Typeface
import android.os.Bundle
import android.view.Gravity
import android.widget.LinearLayout
import android.widget.ScrollView
import android.widget.TextView
import androidx.appcompat.app.AppCompatActivity
import com.kavach.guardian.KavachApp
import com.kavach.guardian.siren.SirenActivity

class OnboardingActivity : AppCompatActivity() {
    override fun onCreate(savedInstanceState: Bundle?) {
        super.onCreate(savedInstanceState)
        val app = application as KavachApp
        val store = app.store

        val scroll = ScrollView(this).apply {
            isFillViewport = true
            setBackgroundColor(KavachTheme.SENIOR_BG)
        }
        val p = KavachTheme.dp(this, 24f)
        val root = LinearLayout(this).apply {
            orientation = LinearLayout.VERTICAL
            setPadding(p, p, p, p)
        }
        scroll.addView(root)

        val header = TextView(this).apply {
            text = "Welcome to Kavach 🛡️"
            textSize = 24f
            gravity = Gravity.CENTER
            typeface = Typeface.DEFAULT_BOLD
            setTextColor(KavachTheme.SENIOR_TEXT)
            setPadding(0, 0, 0, KavachTheme.dp(this@OnboardingActivity, 8f))
        }
        val headerSub = TextView(this).apply {
            text = "Your sovereign family shield against phone fraud."
            textSize = 14f
            gravity = Gravity.CENTER
            setTextColor(KavachTheme.SENIOR_MUTED)
            setPadding(0, 0, 0, KavachTheme.dp(this@OnboardingActivity, 24f))
        }
        root.addView(header)
        root.addView(headerSub)

        val marginBot16 = LinearLayout.LayoutParams(
            LinearLayout.LayoutParams.MATCH_PARENT,
            LinearLayout.LayoutParams.WRAP_CONTENT
        ).apply { setMargins(0, 0, 0, KavachTheme.dp(this@OnboardingActivity, 16f)) }

        fun step(num: String, title: String, body: String): LinearLayout {
            val card = KavachTheme.card(this, isDark = false, radiusDp = 16f, paddingDp = 18)
            card.addView(TextView(this).apply {
                text = num
                textSize = 11f
                setTextColor(KavachTheme.SENIOR_AMBER)
                typeface = Typeface.DEFAULT_BOLD
            })
            card.addView(TextView(this).apply {
                text = title
                textSize = 18f
                typeface = Typeface.DEFAULT_BOLD
                setTextColor(KavachTheme.SENIOR_TEXT)
                setPadding(0, KavachTheme.dp(this@OnboardingActivity, 4f), 0, KavachTheme.dp(this@OnboardingActivity, 6f))
            })
            card.addView(TextView(this).apply {
                text = body
                textSize = 14f
                setTextColor(KavachTheme.SENIOR_MUTED)
                setLineSpacing(2f, 1.2f)
            })
            root.addView(card, marginBot16)
            return card
        }

        step("1 / 3 — ZERO PANIC", "Pause pressure, verify safely",
            "Scammers rely on artificial urgency. Kavach helps you pause and silently intercepts threats before you can be harmed. Personal calls and SMS never touch the cloud.")
        step("2 / 3 — FAMILY PAIRING", "Direct cryptographic link",
            "Connect with your son or daughter's device using zero-knowledge ECIES keys. You maintain full sovereign control with the local Kill Switch.")

        val c3 = step("3 / 3 — CALM REHEARSAL", "Test the alert tone",
            "Hear the calm alert tone in advance so a real scam never surprises you.")

        val btnSiren = KavachTheme.button(this, "🔊 Hear Calm Siren Rehearsal", Color.parseColor("#475569"), Color.WHITE, 10f, 44f) {
            startActivity(Intent(this, SirenActivity::class.java).apply {
                putExtra("reason", "Onboarding test — calm rehearsal, no danger")
            })
        }
        val sirenLp = LinearLayout.LayoutParams(
            LinearLayout.LayoutParams.MATCH_PARENT,
            LinearLayout.LayoutParams.WRAP_CONTENT
        ).apply { setMargins(0, KavachTheme.dp(this@OnboardingActivity, 12f), 0, KavachTheme.dp(this@OnboardingActivity, 8f)) }
        c3.addView(btnSiren, sirenLp)

        val btnPair = KavachTheme.button(this, "🔗 Pair with Family Device →", Color.parseColor("#0E7490"), Color.WHITE, 10f, 44f) {
            startActivity(Intent(this, PairingActivity::class.java))
        }
        val pairLp = LinearLayout.LayoutParams(
            LinearLayout.LayoutParams.MATCH_PARENT,
            LinearLayout.LayoutParams.WRAP_CONTENT
        ).apply { setMargins(0, 0, 0, 0) }
        c3.addView(btnPair, pairLp)

        val doneBtn = KavachTheme.button(this, "Open Shield ✓", KavachTheme.SENIOR_GREEN, Color.WHITE, 12f, 52f) {
            store.putString("onboarded", "1")
            finish()
        }
        val doneLp = LinearLayout.LayoutParams(
            LinearLayout.LayoutParams.MATCH_PARENT,
            LinearLayout.LayoutParams.WRAP_CONTENT
        ).apply { setMargins(0, KavachTheme.dp(this@OnboardingActivity, 8f), 0, 0) }
        root.addView(doneBtn, doneLp)

        setContentView(scroll)
    }
}

