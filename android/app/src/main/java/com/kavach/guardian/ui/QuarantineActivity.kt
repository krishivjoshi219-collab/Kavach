package com.kavach.guardian.ui

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

class QuarantineActivity : AppCompatActivity() {
    override fun onCreate(savedInstanceState: Bundle?) {
        super.onCreate(savedInstanceState)
        val app = application as KavachApp
        val store = app.store
        val hid = store.getString("household_id") ?: "default"

        val scroll = ScrollView(this)
        val root = LinearLayout(this).apply {
            orientation = LinearLayout.VERTICAL
            setBackgroundColor(Color.parseColor("#FAF6EC"))
            setPadding(36, 40, 36, 40)
        }
        scroll.addView(root)

        val title = TextView(this).apply {
            text = "📥 Quarantine Vault"
            textSize = 24f
            setTextColor(Color.parseColor("#B3541E"))
            typeface = android.graphics.Typeface.DEFAULT_BOLD
            gravity = Gravity.CENTER
        }
        root.addView(title)

        val sub = TextView(this).apply {
            text = "Scam SMS kept here, never buzzing. Full text decrypts on manager only after E2E seal."
            textSize = 14f
            setTextColor(Color.parseColor("#666666"))
            gravity = Gravity.CENTER
            setPadding(0, 8, 0, 24)
        }
        root.addView(sub)

        val items = store.quarantine()
        if (items.length() == 0) {
            root.addView(TextView(this).apply {
                text = "Clean — nothing quarantined yet. Run Scam Lab live attack to test."
                textSize = 16f
                setPadding(0, 16, 0, 16)
            })
        }
        for (i in 0 until items.length()) {
            val o = items.getJSONObject(i)
            val card = LinearLayout(this).apply {
                orientation = LinearLayout.VERTICAL
                setBackgroundColor(Color.WHITE)
                setPadding(28, 24, 28, 24)
            }
            val lp = LinearLayout.LayoutParams(
                LinearLayout.LayoutParams.MATCH_PARENT,
                LinearLayout.LayoutParams.WRAP_CONTENT).apply { setMargins(0, 0, 0, 16) }
            card.addView(TextView(this).apply {
                text = "${o.optString("verdict")} · ${o.optString("h").take(12)}…"
                textSize = 16f
                typeface = android.graphics.Typeface.DEFAULT_BOLD
            })
            card.addView(TextView(this).apply {
                text = maskOtp(o.optString("summary"))
                textSize = 14f
            })
            val blockBtn = Button(this).apply {
                text = "Block hash for household"
                setOnClickListener {
                    val hash = o.optString("h")
                    if (hash.isNotEmpty()) {
                        store.addBlockedHash(hash, "Quarantine block")
                        Thread {
                            try {
                                val client = com.kavach.guardian.net.RelayClient(
                                    com.kavach.guardian.BuildConfig.KAVACH_API)
                                client.block(hid, hash, "Quarantine block")
                            } catch (_: Exception) {}
                        }.start()
                        text = "Blocked ✓ future calls auto-reject"
                        isEnabled = false
                    }
                }
            }
            card.addView(blockBtn)
            root.addView(card, lp)
        }
        setContentView(scroll)
    }

    private fun maskOtp(s: String): String {
        var out = s.replace(Regex("\\b\\d{4,8}\\b"), "******")
        out = out.replace(Regex("(?i)otp[^.]{0,20}\\d+"), "OTP ******")
        return out
    }
}
