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
            explanation = "Red flags: OTP demand (Weight 3) + Freeze/Arrest Threat (Weight 3) + Urgency (Weight 2)."
        ),
        Scenario(
            title = "2. 'Digital Arrest' Cyber Cell Threat",
            caller = "+91-99XXX-POLICE",
            text = "This is Crime Branch Delhi. A courier parcel with drugs was seized with your Aadhaar card. Do not hang up or you will be arrested immediately.",
            expectedVerdict = "SCAM",
            explanation = "Red flags: Impersonation of police (Weight 2) + Arrest/Legal Threat (Weight 3) + Artificial Urgency (Weight 2)."
        ),
        Scenario(
            title = "3. Urgent Electricity Bill Disconnection",
            caller = "+91-91XXX-POWER",
            text = "Dear customer, your electricity power will be disconnected tonight at 9:30 PM. Download the APK file immediately to update your KYC.",
            expectedVerdict = "SCAM",
            explanation = "Red flags: KYC lure with APK link (Weight 2) + Power Cut Threat (Weight 3) + Urgency (Weight 2)."
        ),
        Scenario(
            title = "4. Grandchild Emergency Impersonation",
            caller = "+91-97XXX-KID01",
            text = "Grandpa, I had a sudden accident and police need a fine right now. Send money via UPI immediately, please don't call mom!",
            expectedVerdict = "SCAM",
            explanation = "Red flags: Payment extortion/fine demand (Weight 3) + Urgency (Weight 2)."
        ),
        Scenario(
            title = "5. Legitimate Safe Call (Control)",
            caller = "+91-98XXX-SAFE1",
            text = "Hi Mr. Sharma, your scheduled grocery delivery order has arrived at the security gate. Shall I leave it with the guard?",
            expectedVerdict = "LIKELY_SAFE",
            explanation = "No red flag keywords, no threats, no OTP demands."
        )
    )

    override fun onCreate(savedInstanceState: Bundle?) {
        super.onCreate(savedInstanceState)

        val app = application as KavachApp
        val store = app.store

        val scroll = ScrollView(this)
        val root = LinearLayout(this).apply {
            orientation = LinearLayout.VERTICAL
            setBackgroundColor(Color.parseColor("#FAF6EC"))
            setPadding(36, 40, 36, 40)
        }
        scroll.addView(root)

        val title = TextView(this).apply {
            text = "🧪 Interactive Scam Lab"
            textSize = 24f
            setTextColor(Color.parseColor("#B3541E"))
            typeface = android.graphics.Typeface.DEFAULT_BOLD
            gravity = Gravity.CENTER
            setPadding(0, 0, 0, 8)
        }
        root.addView(title)

        val subtitle = TextView(this).apply {
            text = "Rehearse real-world fraud scenarios without real risk.\nTest the on-device RuleEngine, sirens, and remote alerts on demand."
            textSize = 14f
            setTextColor(Color.parseColor("#666666"))
            gravity = Gravity.CENTER
            setPadding(0, 0, 0, 24)
        }
        root.addView(subtitle)

        val resultBox = TextView(this).apply {
            text = "Select a scenario below to run live on-device analysis."
            textSize = 15f
            setTextColor(Color.parseColor("#333333"))
            setBackgroundColor(Color.WHITE)
            setPadding(28, 24, 28, 24)
        }
        val resultLp = LinearLayout.LayoutParams(
            LinearLayout.LayoutParams.MATCH_PARENT,
            LinearLayout.LayoutParams.WRAP_CONTENT
        ).apply { setMargins(0, 0, 0, 24) }
        root.addView(resultBox, resultLp)

        // Killer demo: simulated senior sitting + live spam incoming through the
        // SAME production path as the real receiver (not a fake UI).
        val liveAttackBtn = Button(this).apply {
            text = "🔴 SIMULATE LIVE ATTACK (senior sitting + spam incoming)"
            textSize = 16f
            setBackgroundColor(Color.parseColor("#C62828"))
            setTextColor(Color.WHITE)
            setOnClickListener {
                Thread {
                    val r = SmsHandler.handleSms(
                        this@ScamLabActivity,
                        "+91-98XXX-BANK1",
                        "Your bank account has been frozen due to suspicious activity. Immediately share your OTP or our police officer will arrest you.",
                        demo = true)
                    val hid = store.getString("household_id") ?: "default"
                    val hash = com.kavach.guardian.screen.RuleEngine.hashNumber(hid, "+91-98XXX-BANK1")
                    runOnUiThread {
                        resultBox.text = "LIVE ATTACK: verdict=${r.verdict} forwarded=${r.forwarded} quarantined=${r.quarantined}\n" +
                            "Sender hash ${hash.take(12)}… auto-learned. Ask the same number to call now — second call auto-rejects pre-ring.\n" +
                            "Manager phone should siren with the full decrypted text."
                        if (r.verdict == "SCAM") {
                            resultBox.setTextColor(Color.parseColor("#C62828"))
                            resultBox.setBackgroundColor(Color.parseColor("#FFEBEE"))
                        }
                    }
                }.start()
            }
        }
        root.addView(liveAttackBtn, resultLp)

        for (scenario in scenarios) {
            val card = LinearLayout(this).apply {
                orientation = LinearLayout.VERTICAL
                setBackgroundColor(Color.WHITE)
                setPadding(28, 24, 28, 24)
            }
            val cardLp = LinearLayout.LayoutParams(
                LinearLayout.LayoutParams.MATCH_PARENT,
                LinearLayout.LayoutParams.WRAP_CONTENT
            ).apply { setMargins(0, 0, 0, 16) }

            val scTitle = TextView(this).apply {
                text = scenario.title
                textSize = 17f
                setTextColor(Color.parseColor("#212121"))
                typeface = android.graphics.Typeface.DEFAULT_BOLD
            }
            card.addView(scTitle)

            val scCaller = TextView(this).apply {
                text = "Simulated caller: ${scenario.caller}"
                textSize = 13f
                setTextColor(Color.parseColor("#777777"))
                setPadding(0, 4, 0, 8)
            }
            card.addView(scCaller)

            val scBody = TextView(this).apply {
                text = "\"${scenario.text}\""
                textSize = 14f
                setTextColor(Color.parseColor("#444444"))
                setTypeface(null, android.graphics.Typeface.ITALIC)
                setPadding(0, 0, 0, 12)
            }
            card.addView(scBody)

            val runBtn = Button(this).apply {
                text = "▶ Run Scenario Simulation"
                textSize = 14f
                setBackgroundColor(if (scenario.expectedVerdict == "SCAM") Color.parseColor("#B3541E") else Color.parseColor("#2E7D32"))
                setTextColor(Color.WHITE)
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
                        append("Triggers detected:\n")
                        for (hit in hits) {
                            append("• ${hit.label} (code: ${hit.code}, weight: +${hit.weight})\n")
                        }
                        append("\nContext:\n${scenario.explanation}")
                    }
                    resultBox.text = summaryText

                    if (verdict.verdict == "SCAM") {
                        resultBox.setTextColor(Color.parseColor("#C62828"))
                        resultBox.setBackgroundColor(Color.parseColor("#FFEBEE"))

                        // Offer user to trigger siren
                        val testSiren = Intent(this@ScamLabActivity, SirenActivity::class.java).apply {
                            putExtra("reason", "[SCAM LAB TEST] ${scenario.title}")
                        }
                        startActivity(testSiren)
                    } else {
                        resultBox.setTextColor(Color.parseColor("#1B5E20"))
                        resultBox.setBackgroundColor(Color.parseColor("#E8F5E9"))
                    }
                }
            }
            card.addView(runBtn)
            root.addView(card, cardLp)
        }

        setContentView(scroll)
    }
}
