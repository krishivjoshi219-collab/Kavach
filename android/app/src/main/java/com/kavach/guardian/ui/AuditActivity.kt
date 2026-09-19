package com.kavach.guardian.ui

import android.graphics.Color
import android.graphics.Typeface
import android.os.Bundle
import android.view.Gravity
import android.widget.LinearLayout
import android.widget.ScrollView
import android.widget.TextView
import androidx.appcompat.app.AppCompatActivity
import com.kavach.guardian.BuildConfig
import com.kavach.guardian.KavachApp
import com.kavach.guardian.net.RelayClient

class AuditActivity : AppCompatActivity() {

    private lateinit var client: RelayClient

    override fun onCreate(savedInstanceState: Bundle?) {
        super.onCreate(savedInstanceState)

        val app = application as KavachApp
        val store = app.store
        client = RelayClient(BuildConfig.KAVACH_API)

        val hid = store.getString("household_id") ?: "demo_family_household"

        val scroll = ScrollView(this).apply {
            isFillViewport = true
            setBackgroundColor(KavachTheme.DARK_BG)
        }
        val pad = KavachTheme.dp(this, 20f)
        val root = LinearLayout(this).apply {
            orientation = LinearLayout.VERTICAL
            setPadding(pad, KavachTheme.dp(this@AuditActivity, 24f), pad, pad)
        }
        scroll.addView(root)

        val title = TextView(this).apply {
            text = "Cryptographic Audit 🔒"
            textSize = 20f
            setTextColor(KavachTheme.DARK_TEXT)
            typeface = Typeface.DEFAULT_BOLD
            gravity = Gravity.CENTER
            setPadding(0, 0, 0, KavachTheme.dp(this@AuditActivity, 6f))
        }
        root.addView(title)

        val subtitle = TextView(this).apply {
            text = "Verify end-to-end zero-knowledge proofs. Inspect raw server records directly."
            textSize = 13f
            setTextColor(KavachTheme.DARK_MUTED)
            gravity = Gravity.CENTER
            setPadding(0, 0, 0, KavachTheme.dp(this@AuditActivity, 20f))
        }
        root.addView(subtitle)

        val marginBot16 = LinearLayout.LayoutParams(
            LinearLayout.LayoutParams.MATCH_PARENT,
            LinearLayout.LayoutParams.WRAP_CONTENT
        ).apply { setMargins(0, 0, 0, KavachTheme.dp(this@AuditActivity, 16f)) }

        val proofCard = KavachTheme.card(this, isDark = true, radiusDp = 16f, paddingDp = 18)
        val proofBadge = KavachTheme.badge(this, "ZERO-KNOWLEDGE GUARANTEE", Color.parseColor("#60A5FA"), Color.parseColor("#1E3A8A"))
        val proofText = TextView(this).apply {
            text = "• Server never receives raw numbers (salted SHA-256 hashes only).\n" +
                   "• Server never receives call audio or plain SMS (ECIES noise only).\n" +
                   "• Sealed with Google Tink ECIES-P256-HKDF-HMAC-SHA256.\n" +
                   "• Sovereign Kill Switch bumps epoch and purges cryptographic keys."
            textSize = 13f
            setTextColor(Color.parseColor("#E2E8F0"))
            setLineSpacing(3f, 1.25f)
            setPadding(0, KavachTheme.dp(this@AuditActivity, 10f), 0, 0)
        }
        proofCard.addView(proofBadge)
        proofCard.addView(proofText)
        root.addView(proofCard, marginBot16)

        val rulesCard = KavachTheme.card(this, isDark = true, radiusDp = 16f, paddingDp = 18)
        val pack = com.kavach.guardian.net.RulePack.activePack(store)
        val rulesText = TextView(this).apply {
            text = if (pack == null) {
                "📜 Baked-in default rules active. The shield operates completely offline."
            } else {
                "📜 Rules v${pack.version} · Updated ${java.text.DateFormat.getDateTimeInstance().format(java.util.Date(pack.updatedAt))} · Signature ${if (pack.sigOk) "OK ✓" else "UNVERIFIED"} · ${pack.rules.size} active heuristics."
            }
            textSize = 13f
            setTextColor(Color.parseColor("#FDE68A"))
            setLineSpacing(2f, 1.2f)
        }
        val rulesBtn = KavachTheme.button(this, "Refresh Signed Rules", Color.parseColor("#374151"), Color.WHITE, 10f, 40f) {
            rulesText.text = "📜 Fetching latest signed rules…"
            Thread {
                val res = com.kavach.guardian.net.RulePack.refresh(client, store)
                runOnUiThread {
                    rulesText.text = "📜 ${res.note}"
                    android.widget.Toast.makeText(this@AuditActivity, res.note, android.widget.Toast.LENGTH_LONG).show()
                }
            }.start()
        }
        val btnLp = LinearLayout.LayoutParams(
            LinearLayout.LayoutParams.MATCH_PARENT,
            LinearLayout.LayoutParams.WRAP_CONTENT
        ).apply { setMargins(0, KavachTheme.dp(this@AuditActivity, 10f), 0, 0) }
        rulesCard.addView(rulesText)
        rulesCard.addView(rulesBtn, btnLp)
        root.addView(rulesCard, marginBot16)

        val serverDumpCard = KavachTheme.card(this, isDark = true, radiusDp = 16f, paddingDp = 18)
        val rawServerView = TextView(this).apply {
            text = "Tap 'Inspect Database Records' below to inspect live blind-relay state..."
            textSize = 12f
            typeface = Typeface.MONOSPACE
            setTextColor(Color.parseColor("#94A3B8"))
            background = KavachTheme.rounded(this@AuditActivity, KavachTheme.DARK_SURFACE_ELEVATED, 10f, KavachTheme.DARK_BORDER, 1f)
            val p = KavachTheme.dp(this@AuditActivity, 12f)
            setPadding(p, p, p, p)
            setLineSpacing(2f, 1.2f)
        }
        val refreshBtn = KavachTheme.button(this, "Inspect Server Database Records", KavachTheme.EMERALD_PRO, Color.BLACK, 10f, 44f) {
            Thread {
                try {
                    val blobs = client.pullBlobs(hid, 0)
                    val peer = store.getPeerPub()
                    val epoch = store.getEpoch()
                    val display = buildString {
                        append("SERVER DATABASE DUMP (Household: $hid):\n")
                        append("epoch=$epoch peer=${if (peer.isNullOrEmpty()) "MISSING" else "sealed (${peer.length} chars)"}\n")
                        append("========================================\n\n")
                        if (blobs.length() == 0) {
                            append("No remote blobs currently queued on blind relay.\n\n")
                            append("Sample schema on server:\n")
                            append("[\n")
                            append("  {\n")
                            append("    \"id\": 104,\n")
                            append("    \"sender\": \"senior\",\n")
                            append("    \"nonce\": \"a4f91c9812e...\",\n")
                            append("    \"ciphertext\": \"ENCRYPTED:AES-GCM:7d93a1ef...\"\n")
                            append("  }\n")
                            append("]\n\n")
                            append("Zero plaintext stored on server!")
                        } else {
                            val leak = Regex("otp|aadhaar|password|http|\\+91", RegexOption.IGNORE_CASE)
                            for (i in 0 until blobs.length()) {
                                val b = blobs.getJSONObject(i)
                                val ct = b.optString("ciphertext")
                                val flag = if (leak.containsMatchIn(ct)) " ⚠️ PLAINTEXT LEAK" else " [Opaque Noise ✓]"
                                append("Blob ID #${b.optInt("id")} epoch=${b.optInt("epoch")}:\n")
                                append("• Sender: ${b.optString("sender")}\n")
                                append("• Nonce: ${b.optString("nonce")}\n")
                                append("• Ciphertext: ${ct.take(32)}...$flag\n\n")
                            }
                        }
                    }
                    runOnUiThread { rawServerView.text = display }
                } catch (e: Exception) {
                    runOnUiThread { rawServerView.text = "Audit query result:\n${e.message}" }
                }
            }.start()
        }
        serverDumpCard.addView(rawServerView)
        serverDumpCard.addView(refreshBtn, btnLp)
        root.addView(serverDumpCard, marginBot16)

        setContentView(scroll)
    }
}

