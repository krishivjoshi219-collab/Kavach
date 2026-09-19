package com.kavach.guardian.ui

import android.graphics.Color
import android.os.Bundle
import android.view.Gravity
import android.widget.Button
import android.widget.LinearLayout
import android.widget.ScrollView
import android.widget.TextView
import android.widget.Toast
import androidx.appcompat.app.AppCompatActivity
import com.kavach.guardian.BuildConfig
import com.kavach.guardian.KavachApp
import com.kavach.guardian.net.RelayClient

/**
 * On-Device Quarantine Vault:
 * Displays intercepted scam SMS kept in local encrypted storage.
 * Confidential OTP numbers are masked. Allows 1-tap household hash blocking.
 */
class QuarantineActivity : AppCompatActivity() {
    override fun onCreate(savedInstanceState: Bundle?) {
        super.onCreate(savedInstanceState)
        val app = application as KavachApp
        val store = app.store
        val hid = store.getString("household_id") ?: "default"

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
            text = "📥 Quarantine Vault"
            textSize = 24f
            setTextColor(Color.parseColor("#B3541E"))
            typeface = android.graphics.Typeface.DEFAULT_BOLD
            gravity = Gravity.CENTER
            setPadding(0, 0, 0, 6)
        }
        root.addView(title)

        val sub = TextView(this).apply {
            text = "Scam messages intercepted here silently (zero buzz on senior phone).\nSensitive OTPs are masked. Full evidence decrypts only on family manager device."
            textSize = 14f
            setTextColor(Color.parseColor("#666666"))
            gravity = Gravity.CENTER
            setLineSpacing(3f, 1.15f)
            setPadding(0, 0, 0, 24)
        }
        root.addView(sub)

        val items = store.quarantine()
        if (items.length() == 0) {
            val emptyCard = LinearLayout(this).apply {
                orientation = LinearLayout.VERTICAL
                background = KavachTheme.rounded(this@QuarantineActivity, Color.WHITE, 14f, Color.parseColor("#E0D7C7"), 1f)
                setPadding(32, 28, 32, 28)
                gravity = Gravity.CENTER
            }
            emptyCard.addView(TextView(this).apply {
                text = "🛡️ Vault is Clean"
                textSize = 18f
                setTextColor(Color.parseColor("#2E7D32"))
                typeface = android.graphics.Typeface.DEFAULT_BOLD
                gravity = Gravity.CENTER
            })
            emptyCard.addView(TextView(this).apply {
                text = "No suspicious messages have been intercepted yet.\nYou can run a test attack in Scam Lab to see quarantine in action."
                textSize = 13f
                setTextColor(Color.parseColor("#616161"))
                gravity = Gravity.CENTER
                setPadding(0, 6, 0, 0)
            })
            root.addView(emptyCard)
        }

        for (i in 0 until items.length()) {
            val o = items.getJSONObject(i)
            val card = LinearLayout(this).apply {
                orientation = LinearLayout.VERTICAL
                background = KavachTheme.rounded(this@QuarantineActivity, Color.WHITE, 14f, Color.parseColor("#EF9A9A"), 1.5f)
                setPadding(26, 22, 26, 22)
            }
            val lp = LinearLayout.LayoutParams(
                LinearLayout.LayoutParams.MATCH_PARENT,
                LinearLayout.LayoutParams.WRAP_CONTENT
            ).apply { setMargins(0, 0, 0, 16) }

            val headerRow = LinearLayout(this).apply {
                orientation = LinearLayout.HORIZONTAL
                gravity = Gravity.CENTER_VERTICAL
            }
            val verdictBadge = TextView(this).apply {
                text = "🔴 ${o.optString("verdict", "SCAM")}"
                textSize = 12f
                typeface = android.graphics.Typeface.DEFAULT_BOLD
                setTextColor(Color.parseColor("#C62828"))
                background = KavachTheme.rounded(this@QuarantineActivity, Color.parseColor("#FFEBEE"), 8f)
                setPadding(16, 6, 16, 6)
            }
            val hashText = TextView(this).apply {
                text = "Hash: ${o.optString("h").take(12)}…"
                textSize = 12f
                setTextColor(Color.parseColor("#757575"))
                setPadding(12, 0, 0, 0)
            }
            headerRow.addView(verdictBadge)
            headerRow.addView(hashText)
            card.addView(headerRow)

            val body = TextView(this).apply {
                text = maskOtp(o.optString("summary"))
                textSize = 14f
                setTextColor(Color.parseColor("#212121"))
                setPadding(0, 12, 0, 14)
                setLineSpacing(2f, 1.15f)
            }
            card.addView(body)

            val blockBtn = Button(this).apply {
                text = "🛡️ Block Hash for Household"
                textSize = 13f
                typeface = android.graphics.Typeface.DEFAULT_BOLD
                setTextColor(Color.WHITE)
                background = KavachTheme.rounded(this@QuarantineActivity, Color.parseColor("#C62828"), 10f)
                setPadding(20, 14, 20, 14)
                isAllCaps = false
                setOnClickListener {
                    val hash = o.optString("h")
                    if (hash.isNotEmpty()) {
                        store.addBlockedHash(hash, "Quarantine block")
                        Thread {
                            try {
                                val client = RelayClient(BuildConfig.KAVACH_API)
                                client.block(hid, hash, "Quarantine block")
                            } catch (_: Exception) {}
                        }.start()
                        text = "Blocked ✓ Future calls killed pre-ring"
                        isEnabled = false
                        background = KavachTheme.rounded(this@QuarantineActivity, Color.parseColor("#757575"), 10f)
                        Toast.makeText(this@QuarantineActivity, "Sender hash added to family blocklist.", Toast.LENGTH_SHORT).show()
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
