package com.kavach.guardian.sms

import android.content.Context
import android.content.Intent
import android.util.Log
import com.kavach.guardian.BuildConfig
import com.kavach.guardian.KavachApp
import com.kavach.guardian.crypto.ShieldCrypto
import com.kavach.guardian.net.RelayClient
import com.kavach.guardian.screen.RuleEngine
import com.kavach.guardian.siren.SirenActivity
import org.json.JSONObject
import java.security.SecureRandom

/**
 * Single production path for scam SMS: real receiver AND demo trigger share it.
 * - LIKELY_SAFE/UNCERTAIN: silent, nothing leaves the phone.
 * - SCAM/SUSPICIOUS: quarantine locally, E2E-forward full text to manager
 *   (only if peer key exists AND forward_sms consent is lent), dual siren.
 *   Unknown numbers are always screened (conservative: no contact bypass on
 *   SMS — caller-ID spoofs). Siren fires ONLY on scam-like verdicts.
 */
object SmsHandler {
    data class Result(val verdict: String, val forwarded: Boolean, val quarantined: Boolean)

    fun handleSms(context: Context, sender: String, body: String, demo: Boolean = false): Result {
        val app = context.applicationContext as? KavachApp ?: return Result("ERROR", false, false)
        val store = app.store
        // Dynamic rules first (fetched pack, verified); baked-in judge is fallback.
        val pack = com.kavach.guardian.net.RulePack.activePack(store)?.rules
        val verdict = if (pack.isNullOrEmpty()) RuleEngine.judge(body)
                      else RuleEngine.judgeWithPack(body, pack)
        if (verdict.verdict != "SCAM" && verdict.verdict != "SUSPICIOUS") {
            return Result(verdict.verdict, false, false)
        }
        val hid = store.getString("household_id") ?: "default"
        val senderHash = RuleEngine.hashNumber(hid, sender)
        store.logIncident(verdict.verdict, if (demo) "scam_lab_live" else "sms",
            "Scam SMS (${verdict.reasons.joinToString("; ").take(160)})", senderHash)
        store.quarantineAdd(senderHash, verdict.verdict,
            "${if (demo) "[DEMO] " else ""}${verdict.reasons.joinToString("; ").take(200)}")

        // Siren FIRST: local protection never waits on the network. An offline
        // or dead relay must not delay the alarm by 15s+ of HTTP timeouts.
        if (verdict.verdict == "SCAM") soundSiren(context, senderHash, verdict.reasons)

        var forwarded = false
        // Consent gate: an explicit revoke stops E2E forwarding. Offline or
        // never-fetched defaults to allow so protection never goes silent.
        // Runs AFTER the siren so a slow network can never mute the alarm.
        val consentAllowed = try {
            if (!store.forwardSmsAllowed()) {
                false
            } else {
                val seniorId = store.getString("senior_id") ?: "demo-senior"
                val c = RelayClient(BuildConfig.KAVACH_API).consent(hid, seniorId)
                val caps = c.optJSONObject("capabilities")
                val fwd = caps?.optBoolean("forward_sms", true) ?: true
                store.putForwardSmsConsent(fwd)
                fwd
            }
        } catch (_: Exception) {
            store.forwardSmsAllowed()
        }
        if (!consentAllowed) {
            return Result(verdict.verdict, false, true)
        }
        try {
            val peerB64 = store.getPeerPub()
            if (!peerB64.isNullOrEmpty()) {
                val crypto = ShieldCrypto(context, "device")
                val payload = JSONObject()
                    .put("v", 1).put("epoch", store.getEpoch())
                    .put("type", "scam_sms").put("verdict", verdict.verdict)
                    .put("sender_hash", senderHash)
                    .put("body", body.take(1200))
                    .put("reasons", verdict.reasons.joinToString("; ").take(500))
                    .put("ts", System.currentTimeMillis()).toString()
                val cipher = crypto.encryptForTheirKey(
                    ShieldCrypto.b64d(peerB64), payload.toByteArray())
                val nonce = ByteArray(12).also { SecureRandom().nextBytes(it) }
                    .let { ShieldCrypto.b64e(it) }
                val client = RelayClient(BuildConfig.KAVACH_API)
                val res = client.pushBlob(hid, "senior", nonce, ShieldCrypto.b64e(cipher))
                forwarded = res.optBoolean("ok", false)
            }
        } catch (_: Exception) {
            forwarded = false
        }

        return Result(verdict.verdict, forwarded, true)
    }

    private fun soundSiren(context: Context, senderHash: String, reasons: List<String>) {
        try {
            val siren = Intent(context, SirenActivity::class.java).apply {
                flags = Intent.FLAG_ACTIVITY_NEW_TASK or Intent.FLAG_ACTIVITY_CLEAR_TOP
                putExtra("reason", "Scam SMS: ${reasons.firstOrNull() ?: "OTP/threat"}")
                putExtra("caller_hash", senderHash)
            }
            context.startActivity(siren)
        } catch (e: Exception) {
            Log.e("SmsHandler", "siren start failed", e)
        }
    }
}
