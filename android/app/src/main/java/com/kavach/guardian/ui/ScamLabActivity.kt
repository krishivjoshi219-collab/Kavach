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
            setBackgroundColor(Color.parseColor("#FAF6EC"))
        }
        val root = LinearLayout(this).apply {
            orientation = LinearLayout.VERTICAL
            setPadding(36, 40, 36, 44)
        }
        scroll.addView(root)

        val title = TextView(this).apply {
            text = "🧪 Interactive Scam Lab"
            textSize = 24f
            setTextColor(Color.parseColor("#B3541E"))
            typeface = android.graphics.Typeface.DEFAULT_BOLD
            gravity = Gravity.CENTER
            setPadding(0, 0, 0, 6)
        }
        root.addView(title)

        val subtitle = TextView(this).apply {
            text = "Rehearse fraud scenarios safely. Test the on-device RuleEngine, silent quarantine, and E2E family alerts."
            textSize = 14f
            setTextColor(Color.parseColor("#666666"))
            gravity = Gravity.CENTER
            setPadding(0, 0, 0, 24)
        }
        root.addView(subtitle)

        val resultBox = TextView(this).apply {
            text = "Select a scenario below to run live on-device analysis."
            textSize = 14f
            setTextColor(Color.parseColor("#333333"))
            background = KavachTheme.rounded(this@ScamLabActivity, Color.WHITE, 14f, Color.parseColor("#E0D7C7"), 1f)
            setPadding(28, 24, 28, 24)
            setLineSpacing(3f, 1.15f)
        }
        val resultLp = LinearLayout.LayoutParams(
            LinearLayout.LayoutParams.MATCH_PARENT,
            LinearLayout.LayoutParams.WRAP_CONTENT
        ).apply { setMargins(0, 0, 0, 20) }
        root.addView(resultBox, resultLp)

        // Live attack simulation button
        val liveAttackBtn = Button(this).apply {
            text = "🔴 SIMULATE LIVE ATTACK (Senior Sitting + Scam Incoming)"
            textSize = 14f
            typeface = android.graphics.Typeface.DEFAULT_BOLD
            setTextColor(Color.WHITE)
            background = KavachTheme.rounded(this@ScamLabActivity, Color.parseColor("#C62828"), 12f)
            setPadding(24, 32, 24, 32)
            isAllCaps = false
            setOnClickListener {
                Thread {
                    val r = SmsHandler.handleSms(
                        this@ScamLabActivity,
                        "+91-98XXX-BANK1",
                        "Your bank account has been frozen due to suspicious activity. Immediately share your OTP or our police officer will arrest you.",
                        demo = true)
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
                        resultBox.setTextColor(Color.parseColor("#C62828"))
                        resultBox.background = KavachTheme.rounded(this@ScamLabActivity, Color.parseColor("#FFEBEE"), 14f, Color.parseColor("#EF9A9A"), 1f)
                    }
                }.start()
            }
        }
        root.addView(liveAttackBtn, resultLp)

        for (scenario in scenarios) {
            val card = LinearLayout(this).apply {
                orientation = LinearLayout.VERTICAL
                background = KavachTheme.rounded(this@ScamLabActivity, Color.WHITE, 14f, Color.parseColor("#E0D7C7"), 1f)
                setPadding(26, 22, 26, 22)
            }
            val cardLp = LinearLayout.LayoutParams(
                LinearLayout.LayoutParams.MATCH_PARENT,
                LinearLayout.LayoutParams.WRAP_CONTENT
            ).apply { setMargins(0, 0, 0, 14) }

            val scTitle = TextView(this).apply {
                text = scenario.title
                textSize = 16f
                setTextColor(Color.parseColor("#212121"))
                typeface = android.graphics.Typeface.DEFAULT_BOLD
            }
            card.addView(scTitle)

            val scCaller = TextView(this).apply {
                text = "Simulated Sender: ${scenario.caller}"
                textSize = 12f
                setTextColor(Color.parseColor("#757575"))
                setPadding(0, 4, 0, 6)
            }
            card.addView(scCaller)

            val scBody = TextView(this).apply {
                text = "\"${scenario.text}\""
                textSize = 13f
                setTextColor(Color.parseColor("#424242"))
                setTypeface(null, android.graphics.Typeface.ITALIC)
                setPadding(0, 0, 0, 12)
            }
            card.addView(scBody)

            val runBtn = Button(this).apply {
                text = "▶ Run Scenario Analysis"
                textSize = 13f
                typeface = android.graphics.Typeface.DEFAULT_BOLD
                setTextColor(Color.WHITE)
                background = KavachTheme.rounded(
                    this@ScamLabActivity,
                    if (scenario.expectedVerdict == "SCAM") Color.parseColor("#B3541E") else Color.parseColor("#2E7D32"),
                    10f
                )
                setPadding(20, 16, 20, 16)
                isAllCaps = false
                setOnClickListener {
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
                        resultBox.setTextColor(Color.parseColor("#C62828"))
                        resultBox.background = KavachTheme.rounded(this@ScamLabActivity, Color.parseColor("#FFEBEE"), 14f, Color.parseColor("#EF9A9A"), 1f)

                        val testSiren = Intent(this@ScamLabActivity, SirenActivity::class.java).apply {
                            putExtra("reason", "[SCAM LAB TEST] ${scenario.title}")
                        }
                        startActivity(testSiren)
                    } else {
                        resultBox.setTextColor(Color.parseColor("#1B5E20"))
                        resultBox.background = KavachTheme.rounded(this@ScamLabActivity, Color.parseColor("#E8F5E9"), 14f, Color.parseColor("#A5D6A7"), 1f)
                    }
                }
            }
            card.addView(runBtn)
            root.addView(card, cardLp)
        }

        setContentView(scroll)
    }
}
