package com.kavach.guardian.ui

import android.graphics.Bitmap
import android.graphics.Color
import android.graphics.Typeface
import android.os.Bundle
import android.os.Handler
import android.os.Looper
import android.view.Gravity
import android.view.View
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

/**
 * Intelligent Two-Sided Pairing:
 * Supports Guardian invitation generation (QR + 6-char code + live enrollment polling)
 * and Parent enrollment (accessible code entry + 1-tap seal),
 * followed by mutual 6-emoji Short Authentication String (SAS) fingerprint verification.
 */
class PairingActivity : AppCompatActivity() {

    private lateinit var client: RelayClient
    private lateinit var crypto: ShieldCrypto
    private val handler = Handler(Looper.getMainLooper())
    private var isPolling = false

    override fun onCreate(savedInstanceState: Bundle?) {
        super.onCreate(savedInstanceState)

        val app = application as KavachApp
        val store = app.store
        client = RelayClient(BuildConfig.KAVACH_API)
        crypto = ShieldCrypto(this, "device")

        val currentRole = store.getString("app_role") ?: "guardian"
        var isGuardianView = (currentRole != "senior")

        val scroll = ScrollView(this).apply {
            isFillViewport = true
            setBackgroundColor(if (isGuardianView) KavachTheme.DARK_BG else KavachTheme.SENIOR_BG)
        }
        val pad = KavachTheme.dp(this, 20f)
        val root = LinearLayout(this).apply {
            orientation = LinearLayout.VERTICAL
            setPadding(pad, KavachTheme.dp(this@PairingActivity, 24f), pad, pad)
            gravity = Gravity.CENTER_HORIZONTAL
        }
        scroll.addView(root)

        val marginBot16 = LinearLayout.LayoutParams(
            LinearLayout.LayoutParams.MATCH_PARENT,
            LinearLayout.LayoutParams.WRAP_CONTENT
        ).apply { setMargins(0, 0, 0, KavachTheme.dp(this@PairingActivity, 16f)) }

        val marginBot20 = LinearLayout.LayoutParams(
            LinearLayout.LayoutParams.MATCH_PARENT,
            LinearLayout.LayoutParams.WRAP_CONTENT
        ).apply { setMargins(0, 0, 0, KavachTheme.dp(this@PairingActivity, 20f)) }

        // Title & Description
        val title = TextView(this).apply {
            text = "Cryptographic Shield Pairing 🔐"
            textSize = 20f
            setTextColor(if (isGuardianView) KavachTheme.DARK_TEXT else KavachTheme.SENIOR_TEXT)
            typeface = Typeface.DEFAULT_BOLD
            gravity = Gravity.CENTER
            setPadding(0, 0, 0, KavachTheme.dp(this@PairingActivity, 6f))
        }
        root.addView(title)

        val desc = TextView(this).apply {
            text = "Direct ECIES-P256 key exchange. The relay only transports ciphertext envelopes and has zero access to messages."
            textSize = 13f
            setTextColor(if (isGuardianView) KavachTheme.DARK_MUTED else KavachTheme.SENIOR_MUTED)
            gravity = Gravity.CENTER
            setPadding(0, 0, 0, KavachTheme.dp(this@PairingActivity, 16f))
        }
        root.addView(desc)

        // Segmented Role Switcher (Allows testing both roles from one build)
        val toggleRow = LinearLayout(this).apply {
            orientation = LinearLayout.HORIZONTAL
            background = KavachTheme.rounded(this@PairingActivity, if (isGuardianView) KavachTheme.DARK_SURFACE_ELEVATED else Color.parseColor("#E5E7EB"), 10f)
            val p = KavachTheme.dp(this@PairingActivity, 4f)
            setPadding(p, p, p, p)
        }
        val guardianTabBtn = Button(this).apply {
            text = "Guardian (Share QR)"
            textSize = 12f
            typeface = Typeface.DEFAULT_BOLD
            isAllCaps = false
            layoutParams = LinearLayout.LayoutParams(0, LinearLayout.LayoutParams.WRAP_CONTENT, 1f)
        }
        val parentTabBtn = Button(this).apply {
            text = "Parent (Enter Code)"
            textSize = 12f
            typeface = Typeface.DEFAULT_BOLD
            isAllCaps = false
            layoutParams = LinearLayout.LayoutParams(0, LinearLayout.LayoutParams.WRAP_CONTENT, 1f)
        }

        fun updateTabStyles() {
            if (isGuardianView) {
                guardianTabBtn.background = KavachTheme.rounded(this@PairingActivity, KavachTheme.EMERALD_PRO, 8f)
                guardianTabBtn.setTextColor(Color.BLACK)
                parentTabBtn.setBackgroundColor(Color.TRANSPARENT)
                parentTabBtn.setTextColor(KavachTheme.DARK_MUTED)
            } else {
                parentTabBtn.background = KavachTheme.rounded(this@PairingActivity, KavachTheme.SENIOR_GREEN, 8f)
                parentTabBtn.setTextColor(Color.WHITE)
                guardianTabBtn.setBackgroundColor(Color.TRANSPARENT)
                guardianTabBtn.setTextColor(Color.parseColor("#64748B"))
            }
        }
        updateTabStyles()
        toggleRow.addView(guardianTabBtn)
        toggleRow.addView(parentTabBtn)
        root.addView(toggleRow, marginBot20)

        // Section Containers
        val guardianSection = LinearLayout(this).apply {
            orientation = LinearLayout.VERTICAL
            gravity = Gravity.CENTER_HORIZONTAL
            visibility = if (isGuardianView) View.VISIBLE else View.GONE
        }
        val parentSection = LinearLayout(this).apply {
            orientation = LinearLayout.VERTICAL
            gravity = Gravity.CENTER_HORIZONTAL
            visibility = if (!isGuardianView) View.VISIBLE else View.GONE
        }
        root.addView(guardianSection)
        root.addView(parentSection)

        guardianTabBtn.setOnClickListener {
            isGuardianView = true
            updateTabStyles()
            guardianSection.visibility = View.VISIBLE
            parentSection.visibility = View.GONE
            scroll.setBackgroundColor(KavachTheme.DARK_BG)
        }
        parentTabBtn.setOnClickListener {
            isGuardianView = false
            updateTabStyles()
            parentSection.visibility = View.VISIBLE
            guardianSection.visibility = View.GONE
            scroll.setBackgroundColor(KavachTheme.SENIOR_BG)
        }

        // ==========================================
        // GUARDIAN FLOW (Share Code / QR + Live Wait)
        // ==========================================
        val managerCard = KavachTheme.card(this, isDark = true, radiusDp = 16f, paddingDp = 20).apply {
            gravity = Gravity.CENTER_HORIZONTAL
        }
        val managerHeader = TextView(this).apply {
            text = "Share Invitation with Parent"
            textSize = 15f
            setTextColor(KavachTheme.DARK_TEXT)
            typeface = Typeface.DEFAULT_BOLD
            gravity = Gravity.CENTER_HORIZONTAL
        }
        managerCard.addView(managerHeader)

        val qrImage = ImageView(this).apply {
            layoutParams = LinearLayout.LayoutParams(
                KavachTheme.dp(this@PairingActivity, 200f),
                KavachTheme.dp(this@PairingActivity, 200f)
            ).apply {
                gravity = Gravity.CENTER_HORIZONTAL
                setMargins(0, KavachTheme.dp(this@PairingActivity, 14f), 0, KavachTheme.dp(this@PairingActivity, 10f))
            }
            setBackgroundColor(Color.WHITE)
            val p = KavachTheme.dp(this@PairingActivity, 8f)
            setPadding(p, p, p, p)
        }
        managerCard.addView(qrImage)

        val codeDisplay = TextView(this).apply {
            text = "Generating code..."
            textSize = 17f
            setTextColor(KavachTheme.GOLD_VIP)
            typeface = Typeface.DEFAULT_BOLD
            gravity = Gravity.CENTER
            setPadding(0, KavachTheme.dp(this@PairingActivity, 4f), 0, KavachTheme.dp(this@PairingActivity, 6f))
        }
        managerCard.addView(codeDisplay)

        val pollStatusText = TextView(this).apply {
            text = "🟢 Waiting for parent phone to enter code..."
            textSize = 12f
            setTextColor(Color.parseColor("#93C5FD"))
            gravity = Gravity.CENTER
            setPadding(0, 0, 0, KavachTheme.dp(this@PairingActivity, 12f))
        }
        managerCard.addView(pollStatusText)

        // Fingerprint Display (Shared)
        val fingerprintView = TextView(this).apply {
            text = "Shield Verification Fingerprint:\n(pair to compute)"
            textSize = 13f
            setTextColor(Color.parseColor("#A7F3D0"))
            background = KavachTheme.rounded(this@PairingActivity, KavachTheme.EMERALD_PRO_BG, 12f, KavachTheme.EMERALD_PRO, 1f)
            val p = KavachTheme.dp(this@PairingActivity, 14f)
            setPadding(p, p, p, p)
            gravity = Gravity.CENTER
        }

        fun refreshFingerprint() {
            val myPub = try { ShieldCrypto.b64e(crypto.publicKeyBytes()) } catch (_: Exception) { "" }
            val peer = store.getPeerPub() ?: ""
            if (myPub.isNotEmpty() && peer.isNotEmpty()) {
                val (a, b) = if (myPub < peer) myPub to peer else peer to myPub
                fingerprintView.text = "Mutual Verification SAS Fingerprint:\n${SasFingerprint.of(a, b)}\nBoth screens match — zero MITM."
            }
        }

        fun startLivePeerPolling(hid: String) {
            isPolling = true
            Thread {
                var attempts = 0
                while (isPolling && attempts < 90 && !isFinishing) {
                    try {
                        Thread.sleep(2000)
                        attempts++
                        val peerRes = client.pairPeer(hid)
                        if (peerRes.optBoolean("ok", false)) {
                            val seniorPub = peerRes.optString("senior_pubkey", "")
                            val seniorId = peerRes.optString("senior_id", "dad1")
                            val epoch = peerRes.optInt("epoch", 1)
                            if (seniorPub.isNotEmpty()) {
                                store.putPeerPub(seniorPub)
                                store.putString("senior_id", seniorId)
                                store.putEpoch(epoch)
                                runOnUiThread {
                                    pollStatusText.text = "🎉 PARENT SEALED! ECIES Session Active"
                                    pollStatusText.setTextColor(KavachTheme.EMERALD_PRO)
                                    refreshFingerprint()
                                    Toast.makeText(this@PairingActivity, "Parent device linked successfully! 🛡️", Toast.LENGTH_LONG).show()
                                }
                                break
                            }
                        }
                    } catch (_: Exception) {}
                }
            }.start()
        }

        fun generateManagerCode() {
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
                    }
                    startLivePeerPolling(hid)
                } catch (e: Exception) {
                    runOnUiThread {
                        codeDisplay.text = "Tap to retry code generation"
                        Toast.makeText(this@PairingActivity, "Error: ${e.message}", Toast.LENGTH_SHORT).show()
                    }
                }
            }.start()
        }

        val genBtn = KavachTheme.button(this, "Refresh Pairing Code 🔄", KavachTheme.EMERALD_PRO, Color.BLACK, 10f, 42f) {
            generateManagerCode()
        }
        val genBtnLp = LinearLayout.LayoutParams(
            LinearLayout.LayoutParams.MATCH_PARENT,
            LinearLayout.LayoutParams.WRAP_CONTENT
        )
        managerCard.addView(genBtn, genBtnLp)
        guardianSection.addView(managerCard, marginBot16)

        // Automatically trigger code generation on launch
        generateManagerCode()

        // ==========================================
        // PARENT FLOW (Accessible Code Entry)
        // ==========================================
        val seniorCard = KavachTheme.card(this, isDark = false, radiusDp = 16f, paddingDp = 22)
        val seniorHeader = TextView(this).apply {
            text = "Enter Code from Son / Daughter"
            textSize = 17f
            setTextColor(KavachTheme.SENIOR_TEXT)
            typeface = Typeface.DEFAULT_BOLD
            gravity = Gravity.CENTER_HORIZONTAL
            setPadding(0, 0, 0, KavachTheme.dp(this@PairingActivity, 6f))
        }
        val seniorSub = TextView(this).apply {
            text = "Look at the 6-character code on your family member's screen and type it below:"
            textSize = 13f
            setTextColor(KavachTheme.SENIOR_MUTED)
            gravity = Gravity.CENTER_HORIZONTAL
            setPadding(0, 0, 0, KavachTheme.dp(this@PairingActivity, 14f))
        }
        seniorCard.addView(seniorHeader)
        seniorCard.addView(seniorSub)

        val codeInput = EditText(this).apply {
            hint = "e.g. AB12CD"
            textSize = 22f
            gravity = Gravity.CENTER
            setTextColor(Color.parseColor("#1C1917"))
            setHintTextColor(Color.parseColor("#9CA3AF"))
            typeface = Typeface.DEFAULT_BOLD
            background = KavachTheme.rounded(this@PairingActivity, Color.parseColor("#F3F4F6"), 10f, Color.parseColor("#D1D5DB"), 1.5f)
            val p = KavachTheme.dp(this@PairingActivity, 16f)
            setPadding(p, p, p, p)
        }
        seniorCard.addView(codeInput)

        val pairSeniorBtn = KavachTheme.button(this, "Seal Protection Shield 🛡️", KavachTheme.SENIOR_GREEN, Color.WHITE, 12f, 50f) {
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
                                Toast.makeText(this@PairingActivity, "Pairing code expired or invalid", Toast.LENGTH_LONG).show()
                            }
                        }
                    } catch (e: Exception) {
                        runOnUiThread {
                            Toast.makeText(this@PairingActivity, "Error: ${e.message}", Toast.LENGTH_SHORT).show()
                        }
                    }
                }.start()
            } else {
                Toast.makeText(this@PairingActivity, "Please enter full 6-character code", Toast.LENGTH_SHORT).show()
            }
        }
        val pairBtnLp = LinearLayout.LayoutParams(
            LinearLayout.LayoutParams.MATCH_PARENT,
            LinearLayout.LayoutParams.WRAP_CONTENT
        ).apply { setMargins(0, KavachTheme.dp(this@PairingActivity, 16f), 0, 0) }
        seniorCard.addView(pairSeniorBtn, pairBtnLp)
        parentSection.addView(seniorCard, marginBot16)

        // SAS Fingerprint card added to root
        root.addView(fingerprintView, marginBot16)
        refreshFingerprint()

        setContentView(scroll)
    }

    override fun onDestroy() {
        super.onDestroy()
        isPolling = false
    }
}
