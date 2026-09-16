package com.kavach.guardian.sms

import android.content.BroadcastReceiver
import android.content.Context
import android.content.Intent
import android.provider.Telephony
import com.kavach.guardian.KavachApp
import com.kavach.guardian.screen.RuleEngine
import com.kavach.guardian.siren.SirenActivity

class SmsReceiver : BroadcastReceiver() {

    override fun onReceive(context: Context, intent: Intent) {
        if (intent.action != Telephony.Sms.Intents.SMS_RECEIVED_ACTION) return

        val messages = Telephony.Sms.Intents.getMessagesFromIntent(intent) ?: return
        val app = context.applicationContext as? KavachApp ?: return
        val store = app.store

        for (msg in messages) {
            val body = msg.messageBody ?: continue
            val sender = msg.displayOriginatingAddress ?: "unknown"
            val verdict = RuleEngine.judge(body)

            if (verdict.verdict == "SCAM" || verdict.verdict == "SUSPICIOUS") {
                val householdId = store.getString("household_id") ?: "default"
                val senderHash = RuleEngine.hashNumber(householdId, sender)

                store.logIncident(
                    verdict = verdict.verdict,
                    channel = "sms",
                    summary = "Scam SMS detected (${verdict.reasons.joinToString("; ")})"
                )

                // If high confidence scam, sound siren & warn senior
                if (verdict.verdict == "SCAM") {
                    val sirenIntent = Intent(context, SirenActivity::class.java).apply {
                        flags = Intent.FLAG_ACTIVITY_NEW_TASK or Intent.FLAG_ACTIVITY_CLEAR_TOP
                        putExtra("reason", "Scam SMS: ${verdict.reasons.firstOrNull() ?: "Urgent threat or OTP ask"}")
                        putExtra("caller_hash", senderHash)
                    }
                    context.startActivity(sirenIntent)
                }
            }
        }
    }
}
