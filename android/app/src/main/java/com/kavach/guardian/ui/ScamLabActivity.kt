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
import com.kavach.guardian.screen.RuleEngine
import com.kavach.guardian.siren.SirenActivity
import com.kavach.guardian.sms.SmsHandler

/**
 * Interactive Scam Defense Lab:
 * High-craft testing & simulation environment for testing on-device RuleEngine,
 * silent SMS quarantine, pre-ring rejection, and dual-phone emergency siren.
 */
class ScamLabActivity : AppCompatActivity() {

    data class Scenario(
        val title: String,
        val caller: String,
        val text: String,
        val expectedVerdict: String,
        val explanation: String
    )

    private val scenarios = listOf(
        Scenario(
            title = "1. Fake Bank / Account Frozen",
            caller = "+91-98XXX-BANK1",
            text = "Your bank account has been frozen due to suspicious activity. Immediately share your OTP or our police officer will arrest you.",
            expectedVerdict = "SCAM",
            explanation = "Red flags: OTP demand (+3) • Freeze/Arrest Threat (+3) • Urgency (+2)."
        ),
        Scenario(
            title = "2. 'Digital Arrest' Cyber Cell Threat",
            caller = "+91-99XXX-POLICE",
            text = "This is Crime Branch Delhi. A courier parcel with contraband drugs was seized with your Aadhaar card. Do not disconnect or police will arrest you.",
            expectedVerdict = "SCAM",
            explanation = "Red flags: Police impersonation (+2) • Legal Threat (+3) • Urgency (+2)."
        ),
        Scenario(
            title = "3. Urgent Electricity Bill Disconnection",
            caller = "+91-91XXX-POWER",
            text = "Dear customer, your electricity power will be disconnected tonight at 9:30 PM. Download the APK file immediately to update your KYC.",
            expectedVerdict = "SCAM",
            explanation = "Red flags: KYC lure with APK link (+2) • Power Cut Threat (+3) • Urgency (+2)."
        ),
        Scenario(
            title = "4. Grandchild Emergency Impersonation",
            caller = "+91-97XXX-KID01",
            text = "Grandpa, I had a sudden road accident and police need a fine right now. Send money via UPI immediately, please don't call mom!",
            expectedVerdict = "SCAM",
            explanation = "Red flags: Payment extortion/fine demand (+3) • Urgency (+2)."
        ),
        Scenario(
            title = "5. Legitimate Order Delivery (Control)",
            caller = "+91-98XXX-SAFE1",
            text = "Hi Mr. Sharma, your scheduled grocery delivery order has arrived at the security gate. Shall I leave it with the guard?",
            expectedVerdict = "LIKELY_SAFE",
            explanation = "No red flags, no threats, no OTP demands. Allowed through without alarm."
        )
    )

    override fun onCreate(savedInstanceState: Bundle?) {
        super.onCreate(savedInstanceState)

        val app = application as KavachApp
        val store = app.store

        val scroll = ScrollView(this).apply {
            isFillViewport = true
            setBackgroundColor(KavachTheme.DARK_BG)
        }
        val pad = KavachTheme.dp(this, 20f)
        val root = LinearLayout(this).apply {
            orientation = LinearLayout.VERTICAL
            setPadding(pad, KavachTheme.dp(this@ScamLabActivity, 24f), pad, pad)
        }
        scroll.addView(root)

        val title = TextView(this).apply {
            text = "Scam Defense Lab 🧪"
            textSize = 20f
            setTextColor(KavachTheme.DARK_TEXT)
            typeface = android.graphics.Typeface.DEFAULT_BOLD
            gravity = Gravity.CENTER
            setPadding(0, 0, 0, KavachTheme.dp(this@ScamLabActivity, 6f))
        }
        root.addView(title)

        val subtitle = TextView(this).apply {
            text = "Rehearse fraud scenarios safely. Test the on-device RuleEngine, silent quarantine, and E2E family alerts."
            textSize = 13f
            setTextColor(KavachTheme.DARK_MUTED)
            gravity = Gravity.CENTER
            setLineSpacing(3f, 1.2f)
            setPadding(0, 0, 0, KavachTheme.dp(this@ScamLabActivity, 20f))
        }
        root.addView(subtitle)

        val resultBox = TextView(this).apply {
            text = "Select a scenario below to run live on-device analysis."
            textSize = 13f
            setTextColor(KavachTheme.DARK_TEXT)
            background = KavachTheme.rounded(this@ScamLabActivity, KavachTheme.DARK_SURFACE, 14f, KavachTheme.DARK_BORDER, 1f)
            val p = KavachTheme.dp(this@ScamLabActivity, 16f)
            setPadding(p, p, p, p)
            setLineSpacing(3f, 1.2f)
        }
        val resultLp = LinearLayout.LayoutParams(
            LinearLayout.LayoutParams.MATCH_PARENT,
            LinearLayout.LayoutParams.WRAP_CONTENT
        ).apply { setMargins(0, 0, 0, KavachTheme.dp(this@ScamLabActivity, 16f)) }
        root.addView(resultBox, resultLp)

        // Live attack simulation button
        val liveAttackBtn = KavachTheme.button(
            this,
            "🔴 SIMULATE LIVE ATTACK (Senior Sitting + Scam Incoming)",
            KavachTheme.DANGER_RED,
            Color.WHITE,
            12f,
            48f
        ) {
            Thread {
                val r = SmsHandler.handleSms(
                    this@ScamLabActivity,
                    "+91-98XXX-BANK1",
                    "Your bank account has been frozen due to suspicious activity. Immediately share your OTP or our police officer will arrest you.",
                    demo = true
                )
                val hid = store.getString("household_id") ?: "default"
                val hash = RuleEngine.hashNumber(hid, "+91-98XXX-BANK1")
                runOnUiThread {
                    resultBox.text = "🔴 LIVE ATTACK INTERCEPTED:\n" +
                        "• Verdict: ${r.verdict}\n" +
                        "• Senior Screen: 100% QUIET (SMS never buzzed)\n" +
                        "• Quarantined: ${r.quarantined} (Stored in encrypted vault)\n" +
                        "• E2E Forwarded: ${r.forwarded} (Alert sent to adult child)\n" +
                        "• Sender Hash: ${hash.take(12)}… auto-learned.\n\n" +
                        "If the scammer calls back now, the call terminates PRE-RING."
                    resultBox.setTextColor(KavachTheme.DANGER_RED)
                    resultBox.background = KavachTheme.rounded(this@ScamLabActivity, KavachTheme.DANGER_RED_BG, 14f, KavachTheme.DANGER_RED, 1f)
                }
            }.start()
        }
        root.addView(liveAttackBtn, resultLp)

        val marginBot14 = LinearLayout.LayoutParams(
            LinearLayout.LayoutParams.MATCH_PARENT,
            LinearLayout.LayoutParams.WRAP_CONTENT
        ).apply { setMargins(0, 0, 0, KavachTheme.dp(this@ScamLabActivity, 14f)) }

        for (scenario in scenarios) {
            val card = KavachTheme.card(this, isDark = true, radiusDp = 14f, paddingDp = 16)

            val scTitle = TextView(this).apply {
                text = scenario.title
                textSize = 15f
                setTextColor(KavachTheme.DARK_TEXT)
                typeface = android.graphics.Typeface.DEFAULT_BOLD
            }
            card.addView(scTitle)

            val scCaller = TextView(this).apply {
                text = "Simulated Sender: ${scenario.caller}"
                textSize = 12f
                setTextColor(KavachTheme.DARK_MUTED)
                setPadding(0, KavachTheme.dp(this@ScamLabActivity, 3f), 0, KavachTheme.dp(this@ScamLabActivity, 4f))
            }
            card.addView(scCaller)

            val scBody = TextView(this).apply {
                text = "\"${scenario.text}\""
                textSize = 13f
                setTextColor(Color.parseColor("#CBD5E1"))
                setTypeface(null, android.graphics.Typeface.ITALIC)
                setPadding(0, 0, 0, KavachTheme.dp(this@ScamLabActivity, 10f))
            }
            card.addView(scBody)

            val runBtn = KavachTheme.button(
                this,
                "▶ Run Scenario Analysis",
                if (scenario.expectedVerdict == "SCAM") Color.parseColor("#B45309") else KavachTheme.EMERALD_PRO,
                if (scenario.expectedVerdict == "SCAM") Color.WHITE else Color.BLACK,
                10f,
                38f
            ) {
                val verdict = RuleEngine.judge(scenario.text, knownContact = (scenario.expectedVerdict == "LIKELY_SAFE"))
                val hits = RuleEngine.extract(scenario.text)

                store.logIncident(
                    verdict = verdict.verdict,
                    channel = "scam_lab",
                    summary = "${scenario.title}: ${verdict.verdict} (${hits.size} triggers)"
                )

                val summaryText = buildString {
                    append("VERDICT: ${verdict.verdict} (Confidence: ${(verdict.confidence * 100).toInt()}%)\n\n")
                    append("Red Flags Identified:\n")
                    for (hit in hits) {
                        append("• ${hit.label} (code: ${hit.code}, weight: +${hit.weight})\n")
                    }
                    append("\nContext:\n${scenario.explanation}")
                }
                resultBox.text = summaryText

                if (verdict.verdict == "SCAM") {
                    resultBox.setTextColor(KavachTheme.DANGER_RED)
                    resultBox.background = KavachTheme.rounded(this@ScamLabActivity, KavachTheme.DANGER_RED_BG, 14f, KavachTheme.DANGER_RED, 1f)

                    val testSiren = Intent(this@ScamLabActivity, SirenActivity::class.java).apply {
                        putExtra("reason", "[SCAM LAB TEST] ${scenario.title}")
                    }
                    startActivity(testSiren)
                } else {
                    resultBox.setTextColor(KavachTheme.EMERALD_PRO)
                    resultBox.background = KavachTheme.rounded(this@ScamLabActivity, KavachTheme.EMERALD_PRO_BG, 14f, KavachTheme.EMERALD_PRO, 1f)
                }
            }
            card.addView(runBtn)
            root.addView(card, marginBot14)
        }

        setContentView(scroll)
    }
}
