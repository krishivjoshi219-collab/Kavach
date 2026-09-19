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
            setBackgroundColor(KavachTheme.DARK_BG)
        }
        val pad = KavachTheme.dp(this, 20f)
        val root = LinearLayout(this).apply {
            orientation = LinearLayout.VERTICAL
            setPadding(pad, KavachTheme.dp(this@QuarantineActivity, 24f), pad, pad)
        }
        scroll.addView(root)

        val title = TextView(this).apply {
            text = "Quarantine Vault 📥"
            textSize = 20f
            setTextColor(KavachTheme.DARK_TEXT)
            typeface = android.graphics.Typeface.DEFAULT_BOLD
            gravity = Gravity.CENTER
            setPadding(0, 0, 0, KavachTheme.dp(this@QuarantineActivity, 6f))
        }
        root.addView(title)

        val sub = TextView(this).apply {
            text = "Scam messages intercepted silently (zero buzz on senior device).\nConfidential OTPs are masked. Full evidence decrypts for household guardian."
            textSize = 13f
            setTextColor(KavachTheme.DARK_MUTED)
            gravity = Gravity.CENTER
            setLineSpacing(3f, 1.2f)
            setPadding(0, 0, 0, KavachTheme.dp(this@QuarantineActivity, 20f))
        }
        root.addView(sub)

        val items = store.quarantine()
        if (items.length() == 0) {
            val emptyCard = KavachTheme.card(this, isDark = true, radiusDp = 16f, paddingDp = 24).apply {
                gravity = Gravity.CENTER
            }
            emptyCard.addView(TextView(this).apply {
                text = "🛡️ Vault is Clean"
                textSize = 17f
                setTextColor(KavachTheme.EMERALD_PRO)
                typeface = android.graphics.Typeface.DEFAULT_BOLD
                gravity = Gravity.CENTER
            })
            emptyCard.addView(TextView(this).apply {
                text = "No suspicious messages have been intercepted yet.\nYou can test quarantine in Scam Lab."
                textSize = 13f
                setTextColor(KavachTheme.DARK_MUTED)
                gravity = Gravity.CENTER
                setPadding(0, KavachTheme.dp(this@QuarantineActivity, 6f), 0, 0)
            })
            root.addView(emptyCard)
        }

        val marginBot16 = LinearLayout.LayoutParams(
            LinearLayout.LayoutParams.MATCH_PARENT,
            LinearLayout.LayoutParams.WRAP_CONTENT
        ).apply { setMargins(0, 0, 0, KavachTheme.dp(this@QuarantineActivity, 16f)) }

        for (i in 0 until items.length()) {
            val o = items.getJSONObject(i)
            val card = LinearLayout(this).apply {
                orientation = LinearLayout.VERTICAL
                background = KavachTheme.rounded(this@QuarantineActivity, KavachTheme.DARK_SURFACE, 16f, Color.parseColor("#7F1D1D"), 1.5f)
                val p = KavachTheme.dp(this@QuarantineActivity, 18f)
                setPadding(p, p, p, p)
            }

            val headerRow = LinearLayout(this).apply {
                orientation = LinearLayout.HORIZONTAL
                gravity = Gravity.CENTER_VERTICAL
            }
            val verdictBadge = KavachTheme.badge(
                this@QuarantineActivity,
                "🔴 ${o.optString("verdict", "SCAM")}",
                KavachTheme.DANGER_RED,
                KavachTheme.DANGER_RED_BG
            )
            val hashText = TextView(this).apply {
                text = "Hash: ${o.optString("h").take(12)}…"
                textSize = 12f
                setTextColor(KavachTheme.DARK_MUTED)
                setPadding(KavachTheme.dp(this@QuarantineActivity, 10f), 0, 0, 0)
            }
            headerRow.addView(verdictBadge)
            headerRow.addView(hashText)
            card.addView(headerRow)

            val body = TextView(this).apply {
                text = maskOtp(o.optString("summary"))
                textSize = 14f
                setTextColor(KavachTheme.DARK_TEXT)
                setPadding(0, KavachTheme.dp(this@QuarantineActivity, 12f), 0, KavachTheme.dp(this@QuarantineActivity, 14f))
                setLineSpacing(2f, 1.2f)
            }
            card.addView(body)

            val blockBtn = KavachTheme.button(this, "🛡️ Block Hash for Household", KavachTheme.DANGER_RED, Color.WHITE, 10f, 42f) {
                val hash = o.optString("h")
                if (hash.isNotEmpty()) {
                    store.addBlockedHash(hash, "Quarantine block")
                    Thread {
                        try {
                            val client = RelayClient(BuildConfig.KAVACH_API)
                            client.block(hid, hash, "Quarantine block")
                        } catch (_: Exception) {}
                    }.start()
                    Toast.makeText(this@QuarantineActivity, "Sender hash added to family blocklist.", Toast.LENGTH_SHORT).show()
                }
            }
            card.addView(blockBtn)
            root.addView(card, marginBot16)
        }
        setContentView(scroll)
    }

    private fun maskOtp(s: String): String {
        var out = s.replace(Regex("\\b\\d{4,8}\\b"), "******")
        out = out.replace(Regex("(?i)otp[^.]{0,20}\\d+"), "OTP ******")
        return out
    }
}
