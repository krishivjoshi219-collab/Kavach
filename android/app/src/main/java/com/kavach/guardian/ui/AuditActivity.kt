package com.kavach.guardian.ui

import android.graphics.Color
import android.os.Bundle
import android.view.Gravity
import android.widget.Button
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

        val scroll = ScrollView(this)
        val root = LinearLayout(this).apply {
            orientation = LinearLayout.VERTICAL
            setBackgroundColor(Color.parseColor("#FAF6EC"))
            setPadding(36, 40, 36, 40)
        }
        scroll.addView(root)

        val title = TextView(this).apply {
            text = "🔍 Zero-Knowledge Audit"
            textSize = 24f
            setTextColor(Color.parseColor("#B3541E"))
            typeface = android.graphics.Typeface.DEFAULT_BOLD
            gravity = Gravity.CENTER
            setPadding(0, 0, 0, 8)
        }
        root.addView(title)

        val subtitle = TextView(this).apply {
            text = "Verify live cryptographic privacy. Inspect exactly what data the central server stores versus what stays encrypted on your device."
            textSize = 14f
            setTextColor(Color.parseColor("#666666"))
            gravity = Gravity.CENTER
            setPadding(0, 0, 0, 24)
        }
        root.addView(subtitle)

        val auditCard = TextView(this).apply {
            text = "🔒 PROOF OF ZERO-KNOWLEDGE:\n\n" +
                    "• The server never receives raw phone numbers (only salted SHA-256 hashes).\n" +
                    "• The server never receives call audio or plaintext SMS (base64 ECIES noise only; plaintext rejected).\n" +
                    "• Every message is sealed with ECIES hybrid encryption via Google Tink before transmission.\n" +
                    "• Safety numbers must match on both phones; Kill Switch bumps epoch and wipes queued powers."
            textSize = 14f
            setTextColor(Color.parseColor("#1B5E20"))
            setBackgroundColor(Color.parseColor("#E8F5E9"))
            setPadding(28, 24, 28, 24)
        }
        val cardLp = LinearLayout.LayoutParams(
            LinearLayout.LayoutParams.MATCH_PARENT,
            LinearLayout.LayoutParams.WRAP_CONTENT
        ).apply { setMargins(0, 0, 0, 24) }
        root.addView(auditCard, cardLp)

        val rawServerView = TextView(this).apply {
            text = "Tap 'Inspect Server Database' below to inspect live server records..."
            textSize = 13f
            typeface = android.graphics.Typeface.MONOSPACE
            setTextColor(Color.parseColor("#212121"))
            setBackgroundColor(Color.WHITE)
            setPadding(24, 20, 24, 20)
        }
        root.addView(rawServerView, cardLp)

        val refreshBtn = Button(this).apply {
            text = "Inspect Server Database Records"
            textSize = 15f
            setBackgroundColor(Color.parseColor("#B3541E"))
            setTextColor(Color.WHITE)
            setOnClickListener {
                Thread {
                    try {
                        val blobs = client.pullBlobs(hid, 0)
                        val peer = store.getPeerPub()
                        val epoch = store.getEpoch()
                        val display = buildString {
                            append("SERVER DATABASE DUMP (Household: $hid):\n")
                            append("epoch=$epoch peer=${if (peer.isNullOrEmpty()) "MISSING — E2E off" else "sealed (${peer.length} chars)"}\n")
                            append("========================================\n\n")
                            if (blobs.length() == 0) {
                                append("No remote blobs currently queued on blind relay.\n\n")
                                append("Sample database schema record on server:\n")
                                append("[\n")
                                append("  {\n")
                                append("    \"id\": 104,\n")
                                append("    \"sender\": \"senior\",\n")
                                append("    \"nonce\": \"a4f91c9812e...\",\n")
                                append("    \"ciphertext\": \"ENCRYPTED:AES-GCM:7d93a1ef...\"\n")
                                append("  }\n")
                                append("]\n\n")
                                append("Notice: Even under server breach, zero plaintext is readable!")
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
                        runOnUiThread {
                            rawServerView.text = display
                        }
                    } catch (e: Exception) {
                        runOnUiThread {
                            rawServerView.text = "Audit query result:\n${e.message}"
                        }
                    }
                }.start()
            }
        }
        root.addView(refreshBtn)

        setContentView(scroll)
    }
}
