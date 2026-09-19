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
            setBackgroundColor(Color.parseColor("#FAF6EC"))
        }
        val root = LinearLayout(this).apply {
            orientation = LinearLayout.VERTICAL
            setPadding(36, 40, 36, 44)
            gravity = Gravity.CENTER_HORIZONTAL
        }
        scroll.addView(root)

        val title = TextView(this).apply {
            text = "🔐 Zero-Knowledge Pairing"
            textSize = 24f
            setTextColor(Color.parseColor("#B3541E"))
            typeface = android.graphics.Typeface.DEFAULT_BOLD
            gravity = Gravity.CENTER
            setPadding(0, 0, 0, 6)
        }
        root.addView(title)

        val desc = TextView(this).apply {
            text = "Direct ECIES key exchange. The relay only transports encrypted blobs and cannot read messages."
            textSize = 14f
            setTextColor(Color.parseColor("#666666"))
            gravity = Gravity.CENTER
            setPadding(0, 0, 0, 20)
        }
        root.addView(desc)

        val cardLp = LinearLayout.LayoutParams(
            LinearLayout.LayoutParams.MATCH_PARENT,
            LinearLayout.LayoutParams.WRAP_CONTENT
        ).apply { setMargins(0, 0, 0, 16) }

        // Section 1: Manager QR & Code
        val managerCard = LinearLayout(this).apply {
            orientation = LinearLayout.VERTICAL
            background = KavachTheme.rounded(this@PairingActivity, Color.WHITE, 14f, Color.parseColor("#E0D7C7"), 1f)
            setPadding(24, 20, 24, 20)
            gravity = Gravity.CENTER_HORIZONTAL
        }
        val managerHeader = TextView(this).apply {
            text = "1. Manager: Share Code / QR with Senior"
            textSize = 15f
            setTextColor(Color.parseColor("#212121"))
            typeface = android.graphics.Typeface.DEFAULT_BOLD
            gravity = Gravity.CENTER_HORIZONTAL
        }
        managerCard.addView(managerHeader)

        val qrImage = ImageView(this).apply {
            layoutParams = LinearLayout.LayoutParams(360, 360).apply {
                gravity = Gravity.CENTER_HORIZONTAL
                setMargins(0, 14, 0, 14)
            }
        }
        managerCard.addView(qrImage)

        val codeDisplay = TextView(this).apply {
            text = "Tap below to generate pairing code"
            textSize = 17f
            setTextColor(Color.parseColor("#B3541E"))
            typeface = android.graphics.Typeface.DEFAULT_BOLD
            gravity = Gravity.CENTER
            setPadding(0, 4, 0, 14)
        }
        managerCard.addView(codeDisplay)

        val genBtn = Button(this).apply {
            text = "Generate Manager Pairing Code"
            textSize = 14f
            typeface = android.graphics.Typeface.DEFAULT_BOLD
            setTextColor(Color.WHITE)
            background = KavachTheme.rounded(this@PairingActivity, Color.parseColor("#B3541E"), 10f)
            setPadding(20, 16, 20, 16)
            isAllCaps = false
            setOnClickListener {
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
        }
        managerCard.addView(genBtn)
        root.addView(managerCard, cardLp)

        // Emoji verification fingerprint
        val fingerprintView = TextView(this).apply {
            text = "Shield Verification Fingerprint:\n(pair after both sides seal)"
            textSize = 13f
            setTextColor(Color.parseColor("#1B5E20"))
            background = KavachTheme.rounded(this@PairingActivity, Color.parseColor("#E8F5E9"), 12f, Color.parseColor("#A5D6A7"), 1f)
            setPadding(20, 14, 20, 14)
            gravity = Gravity.CENTER
        }
        root.addView(fingerprintView, cardLp)

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
        val seniorCard = LinearLayout(this).apply {
            orientation = LinearLayout.VERTICAL
            background = KavachTheme.rounded(this@PairingActivity, Color.WHITE, 14f, Color.parseColor("#E0D7C7"), 1f)
            setPadding(24, 20, 24, 20)
        }
        val seniorHeader = TextView(this).apply {
            text = "2. Senior: Enter 6-digit Pairing Code"
            textSize = 15f
            setTextColor(Color.parseColor("#212121"))
            typeface = android.graphics.Typeface.DEFAULT_BOLD
            gravity = Gravity.CENTER_HORIZONTAL
            setPadding(0, 0, 0, 12)
        }
        seniorCard.addView(seniorHeader)

        val codeInput = EditText(this).apply {
            hint = "e.g. AB12CD"
            textSize = 18f
            gravity = Gravity.CENTER
            background = KavachTheme.rounded(this@PairingActivity, Color.parseColor("#F5F5F5"), 10f, Color.parseColor("#BDBDBD"), 1f)
            setPadding(20, 16, 20, 16)
        }
        seniorCard.addView(codeInput)

        val pairSeniorBtn = Button(this).apply {
            text = "Seal Shield with Manager"
            textSize = 14f
            typeface = android.graphics.Typeface.DEFAULT_BOLD
            setTextColor(Color.WHITE)
            background = KavachTheme.rounded(this@PairingActivity, Color.parseColor("#2E7D32"), 10f)
            setPadding(20, 16, 20, 16)
            isAllCaps = false
            layoutParams = LinearLayout.LayoutParams(LinearLayout.LayoutParams.MATCH_PARENT, LinearLayout.LayoutParams.WRAP_CONTENT).apply {
                setMargins(0, 14, 0, 0)
            }
            setOnClickListener {
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
        }
        seniorCard.addView(pairSeniorBtn)
        root.addView(seniorCard, cardLp)

        setContentView(scroll)
    }
}
