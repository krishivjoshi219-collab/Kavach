package com.kavach.guardian.sms

import android.content.BroadcastReceiver
import android.content.Context
import android.content.Intent
import android.provider.Telephony

class SmsReceiver : BroadcastReceiver() {

    override fun onReceive(context: Context, intent: Intent) {
        if (intent.action != Telephony.Sms.Intents.SMS_RECEIVED_ACTION) return

        val messages = Telephony.Sms.Intents.getMessagesFromIntent(intent) ?: return

        for (msg in messages) {
            val body = msg.messageBody ?: continue
            val sender = msg.displayOriginatingAddress ?: "unknown"
            SmsHandler.handleSms(context, sender, body, demo = false)
        }
    }
}
