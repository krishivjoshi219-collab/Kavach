package com.kavach.guardian.screen

import android.content.Intent
import android.net.Uri
import android.os.Build
import android.telecom.Call
import android.telecom.CallScreeningService
import androidx.annotation.RequiresApi
import com.kavach.guardian.KavachApp
import com.kavach.guardian.siren.SirenActivity

@RequiresApi(Build.VERSION_CODES.Q)
class KavachScreeningService : CallScreeningService() {

    override fun onScreenCall(callDetails: Call.Details) {
        val app = application as? KavachApp
        val store = app?.store
        val handle: Uri? = callDetails.handle
        val number = handle?.schemeSpecificPart ?: ""
        val householdId = store?.getString("household_id") ?: "default"

        val numberHash = if (number.isNotBlank()) {
            RuleEngine.hashNumber(householdId, number)
        } else ""

        val isBlocked = numberHash.isNotEmpty() && (store?.isBlockedHash(numberHash) == true)

        if (isBlocked) {
            val response = CallResponse.Builder()
                .setDisallowCall(true)
                .setRejectCall(true)
                .setSkipCallLog(true)
                .setSkipNotification(true)
                .build()
            respondToCall(callDetails, response)

            store?.logIncident("BLOCKED_CALL", "call", "Blocked call from blacklisted hash: ${numberHash.take(8)}...")

            // Launch siren/alert activity
            val sirenIntent = Intent(this, SirenActivity::class.java).apply {
                flags = Intent.FLAG_ACTIVITY_NEW_TASK or Intent.FLAG_ACTIVITY_CLEAR_TOP
                putExtra("reason", "Blocked suspicious scam caller")
                putExtra("caller_hash", numberHash)
            }
            startActivity(sirenIntent)
        } else {
            val response = CallResponse.Builder()
                .setDisallowCall(false)
                .setRejectCall(false)
                .setSkipCallLog(false)
                .setSkipNotification(false)
                .build()
            respondToCall(callDetails, response)
        }
    }
}
