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

        // Decide from CACHE ONLY: Telecom expects respondToCall in milliseconds.
        // A blocking HTTP sync (15s+ timeouts) on this path would stall the
        // verdict and the system would ring through. Household sync runs AFTER
        // the decision on a throwaway thread, warming the cache for next call.
        val isBlocked = numberHash.isNotEmpty() && (store?.isBlockedHash(numberHash) == true)
        val communityReason = if (!isBlocked && numberHash.isNotEmpty() && store != null) {
            com.kavach.guardian.net.CommunityShield.screenHash(store, numberHash)
        } else null
        val blockedReason = if (isBlocked) "household list" else communityReason

        if (blockedReason != null) {
            val response = CallResponse.Builder()
                .setDisallowCall(true)
                .setRejectCall(true)
                .setSkipCallLog(true)
                .setSkipNotification(true)
                .build()
            respondToCall(callDetails, response)

            store?.logIncident("BLOCKED_CALL", "call", "Blocked call from blacklisted hash: ${numberHash.take(8)}... ($blockedReason)")

            // Launch siren/alert activity
            val sirenIntent = Intent(this, SirenActivity::class.java).apply {
                flags = Intent.FLAG_ACTIVITY_NEW_TASK or Intent.FLAG_ACTIVITY_CLEAR_TOP
                putExtra("reason", "Blocked suspicious scam caller ($blockedReason)")
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

        // Post-decision warmup: pull sibling-device household blocks so the NEXT
        // call benefits. Never touches this verdict. Fire-and-forget.
        if (numberHash.isNotEmpty() && store != null) {
            val hid = householdId
            val st = store
            Thread {
                try {
                    val client = com.kavach.guardian.net.RelayClient(
                        com.kavach.guardian.BuildConfig.KAVACH_API)
                    com.kavach.guardian.net.CommunityShield.syncHousehold(client, st, hid)
                } catch (_: Exception) {}
            }.start()
        }
    }
}
