package com.kavach.guardian.ui

import android.graphics.Bitmap
import android.graphics.Color
import android.os.Bundle
import android.view.Gravity
import android.widget.Button
import android.widget.EditText
import android.widget.ImageView
import android.widget.LinearLayout
import android.widget.ScrollView
import android.widget.TextView
import android.widget.Toast
import androidx.appcompat.app.AppCompatActivity
import com.google.zxing.BarcodeFormat
import com.journeyapps.barcodescanner.BarcodeEncoder
import com.kavach.guardian.BuildConfig
import com.kavach.guardian.KavachApp
import com.kavach.guardian.crypto.SasFingerprint
import com.kavach.guardian.crypto.ShieldCrypto
import com.kavach.guardian.net.RelayClient

class PairingActivity : AppCompatActivity() {

    private lateinit var client: RelayClient
    private lateinit var crypto: ShieldCrypto

    override fun onCreate(savedInstanceState: Bundle?) {
        super.onCreate(savedInstanceState)

        val app = application as KavachApp
        val store = app.store
        client = RelayClient(BuildConfig.KAVACH_API)
        crypto = ShieldCrypto(this, "device")

        val scroll = ScrollView(this).apply {
            isFillViewport = true
            setBackgroundColor(KavachTheme.DARK_BG)
        }
        val pad = KavachTheme.dp(this, 20f)
        val root = LinearLayout(this).apply {
            orientation = LinearLayout.VERTICAL
            setPadding(pad, KavachTheme.dp(this@PairingActivity, 24f), pad, pad)
            gravity = Gravity.CENTER_HORIZONTAL
        }
        scroll.addView(root)

        val title = TextView(this).apply {
            text = "Zero-Knowledge Pairing 🔐"
            textSize = 20f
            setTextColor(KavachTheme.DARK_TEXT)
            typeface = android.graphics.Typeface.DEFAULT_BOLD
            gravity = Gravity.CENTER
            setPadding(0, 0, 0, KavachTheme.dp(this@PairingActivity, 6f))
        }
        root.addView(title)

        val desc = TextView(this).apply {
            text = "Direct ECIES key exchange. The relay only transports encrypted blobs and cannot read messages."
            textSize = 13f
            setTextColor(KavachTheme.DARK_MUTED)
            gravity = Gravity.CENTER
            setPadding(0, 0, 0, KavachTheme.dp(this@PairingActivity, 20f))
        }
        root.addView(desc)

        val marginBot16 = LinearLayout.LayoutParams(
            LinearLayout.LayoutParams.MATCH_PARENT,
            LinearLayout.LayoutParams.WRAP_CONTENT
        ).apply { setMargins(0, 0, 0, KavachTheme.dp(this@PairingActivity, 16f)) }

        // Section 1: Manager QR & Code
        val managerCard = KavachTheme.card(this, isDark = true, radiusDp = 16f, paddingDp = 20).apply {
            gravity = Gravity.CENTER_HORIZONTAL
        }
        val managerHeader = TextView(this).apply {
            text = "1. Manager: Share Code / QR with Parent"
            textSize = 15f
            setTextColor(KavachTheme.DARK_TEXT)
            typeface = android.graphics.Typeface.DEFAULT_BOLD
            gravity = Gravity.CENTER_HORIZONTAL
        }
        managerCard.addView(managerHeader)

        val qrImage = ImageView(this).apply {
            layoutParams = LinearLayout.LayoutParams(
                KavachTheme.dp(this@PairingActivity, 180f),
                KavachTheme.dp(this@PairingActivity, 180f)
            ).apply {
                gravity = Gravity.CENTER_HORIZONTAL
                setMargins(0, KavachTheme.dp(this@PairingActivity, 12f), 0, KavachTheme.dp(this@PairingActivity, 12f))
            }
        }
        managerCard.addView(qrImage)

        val codeDisplay = TextView(this).apply {
            text = "Tap below to generate pairing code"
            textSize = 15f
            setTextColor(KavachTheme.GOLD_VIP)
            typeface = android.graphics.Typeface.DEFAULT_BOLD
            gravity = Gravity.CENTER
            setPadding(0, KavachTheme.dp(this@PairingActivity, 4f), 0, KavachTheme.dp(this@PairingActivity, 12f))
        }
        managerCard.addView(codeDisplay)

        val genBtn = KavachTheme.button(this, "Generate Manager Pairing Code", KavachTheme.EMERALD_PRO, Color.BLACK, 10f, 42f) {
            Thread {
                try {
                    var hid = store.getString("household_id") ?: ""
                    if (hid.isEmpty()) {
                        hid = client.createHousehold()
                        store.putString("household_id", hid)
                    }
                    val pubB64 = ShieldCrypto.b64e(crypto.publicKeyBytes())
                    val resp = client.pairInit(hid, pubB64)
                    val code = resp.optString("pairing_code", "ERROR")

                    val encoder = BarcodeEncoder()
                    val pkHash = try {
                        val md = java.security.MessageDigest.getInstance("SHA-256")
                        md.digest(pubB64.toByteArray()).joinToString("") { "%02x".format(it) }.take(12)
                    } catch (_: Exception) { "kavach" }
                    val qrPayload = "kavach://pair?hid=$hid&code=$code&ph=$pkHash"
                    val bitmap: Bitmap = encoder.encodeBitmap(qrPayload, BarcodeFormat.QR_CODE, 360, 360)

                    runOnUiThread {
                        codeDisplay.text = "PAIRING CODE: $code"
                        qrImage.setImageBitmap(bitmap)
                        Toast.makeText(this@PairingActivity, "Pairing code generated!", Toast.LENGTH_SHORT).show()
                    }
                } catch (e: Exception) {
                    runOnUiThread {
                        Toast.makeText(this@PairingActivity, "Error: ${e.message}", Toast.LENGTH_SHORT).show()
                    }
                }
            }.start()
        }
        val genBtnLp = LinearLayout.LayoutParams(
            LinearLayout.LayoutParams.MATCH_PARENT,
            LinearLayout.LayoutParams.WRAP_CONTENT
        )
        managerCard.addView(genBtn, genBtnLp)
        root.addView(managerCard, marginBot16)

        // Emoji verification fingerprint
        val fingerprintView = TextView(this).apply {
            text = "Shield Verification Fingerprint:\n(pair after both sides seal)"
            textSize = 13f
            setTextColor(Color.parseColor("#A7F3D0"))
            background = KavachTheme.rounded(this@PairingActivity, KavachTheme.EMERALD_PRO_BG, 12f, KavachTheme.EMERALD_PRO, 1f)
            val p = KavachTheme.dp(this@PairingActivity, 14f)
            setPadding(p, p, p, p)
            gravity = Gravity.CENTER
        }
        root.addView(fingerprintView, marginBot16)

        fun refreshFingerprint() {
            val myPub = try { ShieldCrypto.b64e(crypto.publicKeyBytes()) } catch (_: Exception) { "" }
            val peer = store.getPeerPub() ?: ""
            if (myPub.isNotEmpty() && peer.isNotEmpty()) {
                val (a, b) = if (myPub < peer) myPub to peer else peer to myPub
                fingerprintView.text = "Shield Verification Fingerprint:\n${SasFingerprint.of(a, b)}\nBoth screens must match."
            }
        }
        refreshFingerprint()

        // Section 2: Senior Enter Code
        val seniorCard = KavachTheme.card(this, isDark = true, radiusDp = 16f, paddingDp = 20)
        val seniorHeader = TextView(this).apply {
            text = "2. Parent: Enter 6-character Code"
            textSize = 15f
            setTextColor(KavachTheme.DARK_TEXT)
            typeface = android.graphics.Typeface.DEFAULT_BOLD
            gravity = Gravity.CENTER_HORIZONTAL
            setPadding(0, 0, 0, KavachTheme.dp(this@PairingActivity, 10f))
        }
        seniorCard.addView(seniorHeader)

        val codeInput = EditText(this).apply {
            hint = "e.g. AB12CD"
            textSize = 18f
            gravity = Gravity.CENTER
            setTextColor(Color.WHITE)
            setHintTextColor(KavachTheme.DARK_MUTED)
            background = KavachTheme.rounded(this@PairingActivity, KavachTheme.DARK_SURFACE_ELEVATED, 10f, KavachTheme.DARK_BORDER, 1f)
            val p = KavachTheme.dp(this@PairingActivity, 14f)
            setPadding(p, p, p, p)
        }
        seniorCard.addView(codeInput)

        val pairSeniorBtn = KavachTheme.button(this, "Seal Shield with Manager", KavachTheme.EMERALD_PRO, Color.BLACK, 10f, 44f) {
            val entered = codeInput.text.toString().trim().uppercase()
            if (entered.length == 6) {
                Thread {
                    try {
                        val seniorPubB64 = ShieldCrypto.b64e(crypto.publicKeyBytes())
                        val seniorId = store.getString("senior_id") ?: "senior_dad"
                        val res = client.pairComplete(entered, seniorPubB64, seniorId)
                        val ok = res.optBoolean("ok", false)
                        runOnUiThread {
                            if (ok) {
                                val returnedHid = res.optString("household_id", "")
                                if (returnedHid.isNotEmpty()) {
                                    store.putString("household_id", returnedHid)
                                }
                                val mgrPub = res.optString("manager_pubkey", "")
                                if (mgrPub.isNotEmpty()) {
                                    store.putPeerPub(mgrPub)
                                    refreshFingerprint()
                                }
                                try {
                                    val c = client.consent(returnedHid.ifEmpty { store.getString("household_id") ?: "" }, seniorId)
                                    store.putEpoch(c.optInt("epoch", store.getEpoch()))
                                } catch (_: Exception) {}
                                Toast.makeText(this@PairingActivity, "Shield Sealed Successfully! 🛡️", Toast.LENGTH_LONG).show()
                                finish()
                            } else {
                                Toast.makeText(this@PairingActivity, "Pairing failed or code expired", Toast.LENGTH_LONG).show()
                            }
                        }
                    } catch (e: Exception) {
                        runOnUiThread {
                            Toast.makeText(this@PairingActivity, "Error: ${e.message}", Toast.LENGTH_SHORT).show()
                        }
                    }
                }.start()
            } else {
                Toast.makeText(this@PairingActivity, "Enter valid 6-char code", Toast.LENGTH_SHORT).show()
            }
        }
        val pairBtnLp = LinearLayout.LayoutParams(
            LinearLayout.LayoutParams.MATCH_PARENT,
            LinearLayout.LayoutParams.WRAP_CONTENT
        ).apply { setMargins(0, KavachTheme.dp(this@PairingActivity, 12f), 0, 0) }
        seniorCard.addView(pairSeniorBtn, pairBtnLp)
        root.addView(seniorCard, marginBot16)

        setContentView(scroll)
    }
}
