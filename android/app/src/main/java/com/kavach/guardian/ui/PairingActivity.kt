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

        val scroll = ScrollView(this)
        val root = LinearLayout(this).apply {
            orientation = LinearLayout.VERTICAL
            setBackgroundColor(Color.parseColor("#FAF6EC"))
            setPadding(40, 48, 40, 48)
            gravity = Gravity.CENTER_HORIZONTAL
        }
        scroll.addView(root)

        val title = TextView(this).apply {
            text = "🔐 Zero-Knowledge Pairing"
            textSize = 24f
            setTextColor(Color.parseColor("#B3541E"))
            typeface = android.graphics.Typeface.DEFAULT_BOLD
            gravity = Gravity.CENTER
            setPadding(0, 0, 0, 8)
        }
        root.addView(title)

        val desc = TextView(this).apply {
            text = "Keys are exchanged directly via ECIES hybrid crypto.\nThe server only relays encrypted blobs and never sees your messages."
            textSize = 14f
            setTextColor(Color.parseColor("#666666"))
            gravity = Gravity.CENTER
            setPadding(0, 0, 0, 24)
        }
        root.addView(desc)

        // Manager section: Generate pairing code + QR
        val managerHeader = TextView(this).apply {
            text = "1. Manager: Share Code / QR with Senior"
            textSize = 17f
            setTextColor(Color.parseColor("#212121"))
            typeface = android.graphics.Typeface.DEFAULT_BOLD
            setPadding(0, 16, 0, 8)
        }
        root.addView(managerHeader)

        val qrImage = ImageView(this).apply {
            layoutParams = LinearLayout.LayoutParams(400, 400).apply {
                gravity = Gravity.CENTER_HORIZONTAL
                setMargins(0, 16, 0, 16)
            }
        }
        root.addView(qrImage)

        val codeDisplay = TextView(this).apply {
            text = "Tap below to create pairing code"
            textSize = 22f
            setTextColor(Color.parseColor("#B3541E"))
            typeface = android.graphics.Typeface.DEFAULT_BOLD
            gravity = Gravity.CENTER
            setPadding(0, 8, 0, 16)
        }
        root.addView(codeDisplay)

        // Signal-style emoji verification fingerprint (derived, not hardcoded)
        val fingerprintView = TextView(this).apply {
            text = "Shield Verification Fingerprint:\n(pair after both sides seal)"
            textSize = 16f
            setTextColor(Color.parseColor("#1B5E20"))
            setBackgroundColor(Color.parseColor("#E8F5E9"))
            setPadding(24, 16, 24, 16)
            gravity = Gravity.CENTER
        }
        root.addView(fingerprintView)

        fun refreshFingerprint() {
            val myPub = try { ShieldCrypto.b64e(crypto.publicKeyBytes()) } catch (_: Exception) { "" }
            val peer = store.getPeerPub() ?: ""
            if (myPub.isNotEmpty() && peer.isNotEmpty()) {
                // Order-independent: sort so both sides derive the same emojis.
                val (a, b) = if (myPub < peer) myPub to peer else peer to myPub
                fingerprintView.text = "Shield Verification Fingerprint:\n${SasFingerprint.of(a, b)}\nBoth screens must match."
            }
        }
        refreshFingerprint()

        // Fridge recovery code card (random per household, stored on-device)
        var fridge = store.getFridgeCode()
        if (fridge.isNullOrEmpty()) {
            fridge = SasFingerprint.fridgeCode()
            store.putFridgeCode(fridge)
        }
        val fridgeCard = TextView(this).apply {
            text = "🧊 Fridge Recovery Code:\n$fridge\n(Keep a copy on the fridge in case a device is lost)"
            textSize = 13f
            setTextColor(Color.parseColor("#424242"))
            setBackgroundColor(Color.parseColor("#FFF3E0"))
            setPadding(24, 16, 24, 16)
            gravity = Gravity.CENTER
        }
        val cardLp = LinearLayout.LayoutParams(
            LinearLayout.LayoutParams.MATCH_PARENT,
            LinearLayout.LayoutParams.WRAP_CONTENT
        ).apply { setMargins(0, 16, 0, 24) }
        root.addView(fridgeCard, cardLp)

        val genBtn = Button(this).apply {
            text = "Generate Manager Pairing Code"
            textSize = 16f
            setBackgroundColor(Color.parseColor("#B3541E"))
            setTextColor(Color.WHITE)
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
                        // Slim QR: hash of pubkey only (full keys exchange via relay).
                        val pkHash = try {
                            val md = java.security.MessageDigest.getInstance("SHA-256")
                            md.digest(pubB64.toByteArray()).joinToString("") { "%02x".format(it) }.take(12)
                        } catch (_: Exception) { "kavach" }
                        val qrPayload = "kavach://pair?hid=$hid&code=$code&ph=$pkHash"
                        val bitmap: Bitmap = encoder.encodeBitmap(qrPayload, BarcodeFormat.QR_CODE, 400, 400)

                        runOnUiThread {
                            codeDisplay.text = "PAIRING CODE:\n$code"
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
        root.addView(genBtn)

        // Senior section: Enter code
        val seniorHeader = TextView(this).apply {
            text = "2. Senior: Enter 6-digit Pairing Code"
            textSize = 17f
            setTextColor(Color.parseColor("#212121"))
            typeface = android.graphics.Typeface.DEFAULT_BOLD
            setPadding(0, 32, 0, 8)
        }
        root.addView(seniorHeader)

        val codeInput = EditText(this).apply {
            hint = "e.g. AB12CD"
            textSize = 18f
            gravity = Gravity.CENTER
            setBackgroundColor(Color.WHITE)
            setPadding(24, 20, 24, 20)
        }
        root.addView(codeInput)

        val pairSeniorBtn = Button(this).apply {
            text = "Seal Shield with Manager"
            textSize = 16f
            setBackgroundColor(Color.parseColor("#2E7D32"))
            setTextColor(Color.WHITE)
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
                                    // True E2E: senior persists manager pubkey + epoch.
                                    val mgrPub = res.optString("manager_pubkey", "")
                                    if (mgrPub.isNotEmpty()) {
                                        store.putPeerPub(mgrPub)
                                        val myPub = try { ShieldCrypto.b64e(crypto.publicKeyBytes()) } catch (_: Exception) { "" }
                                        if (myPub.isNotEmpty()) {
                                            val (a, b) = if (myPub < mgrPub) myPub to mgrPub else mgrPub to myPub
                                            fingerprintView.text = "Shield Verification Fingerprint:\n${SasFingerprint.of(a, b)}\nBoth screens must match."
                                        }
                                    }
                                    try {
                                        val c = client.consent(returnedHid.ifEmpty { store.getString("household_id") ?: "" }, seniorId)
                                        store.putEpoch(c.optInt("epoch", store.getEpoch()))
                                    } catch (_: Exception) {
                                    }
                                    Toast.makeText(this@PairingActivity, "Shield Sealed Successfully! 🛡️ Manager powers granted (revocable).", Toast.LENGTH_LONG).show()
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
        val btnLp = LinearLayout.LayoutParams(
            LinearLayout.LayoutParams.MATCH_PARENT,
            LinearLayout.LayoutParams.WRAP_CONTENT
        ).apply { setMargins(0, 16, 0, 16) }
        root.addView(pairSeniorBtn, btnLp)

        // Manager: fetch senior key after seal so BOTH sides can encrypt.
        val fetchPeerBtn = Button(this).apply {
            text = "⬇ Manager: Fetch Senior Key"
            textSize = 15f
            setBackgroundColor(Color.parseColor("#37474F"))
            setTextColor(Color.WHITE)
            setOnClickListener {
                Thread {
                    try {
                        val hid = store.getString("household_id") ?: ""
                        val peer = client.pairPeer(hid)
                        val ok = peer.optBoolean("ok", false)
                        val seniorPub = peer.optString("senior_pubkey", "")
                        runOnUiThread {
                            if (ok && seniorPub.isNotEmpty()) {
                                store.putPeerPub(seniorPub)
                                store.putEpoch(peer.optInt("epoch", store.getEpoch()))
                                val myPub = try { ShieldCrypto.b64e(crypto.publicKeyBytes()) } catch (_: Exception) { "" }
                                if (myPub.isNotEmpty()) {
                                    val (a, b) = if (myPub < seniorPub) myPub to seniorPub else seniorPub to myPub
                                    fingerprintView.text = "Shield Verification Fingerprint:\n${SasFingerprint.of(a, b)}\nBoth screens must match."
                                }
                                Toast.makeText(this@PairingActivity, "Senior key sealed. E2E live. 🛡️", Toast.LENGTH_LONG).show()
                            } else {
                                Toast.makeText(this@PairingActivity, "Senior hasn't sealed yet.", Toast.LENGTH_SHORT).show()
                            }
                        }
                    } catch (e: Exception) {
                        runOnUiThread {
                            Toast.makeText(this@PairingActivity, "Error: ${e.message}", Toast.LENGTH_SHORT).show()
                        }
                    }
                }.start()
            }
        }
        root.addView(fetchPeerBtn, btnLp)

        setContentView(scroll)
    }
}
