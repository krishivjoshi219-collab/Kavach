package com.kavach.guardian.ui

import android.content.Intent
import android.graphics.Color
import android.os.Bundle
import android.view.Gravity
import android.widget.Button
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

        val scroll = ScrollView(this)
        val root = LinearLayout(this).apply {
            orientation = LinearLayout.VERTICAL
            setBackgroundColor(Color.parseColor("#FAF6EC"))
            setPadding(40, 48, 40, 48)
        }
        scroll.addView(root)

        fun step(num: String, title: String, body: String): LinearLayout {
            val card = LinearLayout(this).apply {
                orientation = LinearLayout.VERTICAL
                setBackgroundColor(Color.WHITE)
                setPadding(28, 24, 28, 24)
            }
            card.addView(TextView(this).apply {
                text = num
                textSize = 13f
                setTextColor(Color.parseColor("#B3541E"))
                typeface = android.graphics.Typeface.DEFAULT_BOLD
            })
            card.addView(TextView(this).apply {
                text = title
                textSize = 20f
                typeface = android.graphics.Typeface.DEFAULT_BOLD
            })
            card.addView(TextView(this).apply {
                text = body
                textSize = 16f
                setPadding(0, 8, 0, 0)
            })
            val lp = LinearLayout.LayoutParams(
                LinearLayout.LayoutParams.MATCH_PARENT,
                LinearLayout.LayoutParams.WRAP_CONTENT).apply { setMargins(0, 0, 0, 16) }
            root.addView(card, lp)
            return card
        }

        root.addView(TextView(this).apply {
            text = "🛡️ Welcome to Kavach"
            textSize = 26f
            gravity = Gravity.CENTER
            typeface = android.graphics.Typeface.DEFAULT_BOLD
            setPadding(0, 0, 0, 16)
        })

        step("1 / 3 — WHY", "Pause pressure, verify independently",
            "Scammers rush you. Kavach helps you pause, check through a contact YOU find, and ask family. Nothing uploads calls.")
        step("2 / 3 — PAIR", "Scan together, senior approves",
            "Family shows a QR + 6-letter code + safety emojis. Senior scans, both screens must match. Senior can revoke anytime with Kill Switch.")
        val c3 = step("3 / 3 — TEST", "Hear the siren once, calmly",
            "Tap below to hear the alert now, so a real scam never surprises you. Then open Scam Lab to rehearse.")
        c3.addView(Button(this).apply {
            text = "🔊 Test siren now"
            setOnClickListener {
                startActivity(Intent(this@OnboardingActivity, SirenActivity::class.java).apply {
                    putExtra("reason", "Onboarding test — calm rehearsal, no danger")
                })
            }
        })
        c3.addView(Button(this).apply {
            text = "🔗 Pair with family →"
            setOnClickListener { startActivity(Intent(this@OnboardingActivity, PairingActivity::class.java)) }
        })

        val done = Button(this).apply {
            text = "Done — open Shield ✓"
            setBackgroundColor(Color.parseColor("#2E7D32"))
            setTextColor(Color.WHITE)
            setOnClickListener {
                store.putString("onboarded", "1")
                finish()
            }
        }
        root.addView(done)
        setContentView(scroll)
    }
}
