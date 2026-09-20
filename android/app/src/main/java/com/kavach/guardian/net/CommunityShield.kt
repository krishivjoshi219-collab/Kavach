package com.kavach.guardian.net

import com.kavach.guardian.data.LocalStore
import org.json.JSONArray

/** Community shield: one family's block protects all families.
 *
 *  Syncs anonymized sender-hashes (threshold-gated server-side), caches them
 *  for offline screening. Manager stays sovereign: per-hash allow overrides,
 *  Kill Switch wipes everything. Pure decision fn stays testable on JVM.
 */
object CommunityShield {

    data class SyncResult(val ok: Boolean, val count: Int, val note: String)

    /** Pure: null = allow, otherwise human reason. Household list wins. */
    fun decide(localBlocked: Boolean, communityReports: Int?,
               overridden: Boolean): String? {
        if (localBlocked) return "household list"
        if (overridden) return null
        if (communityReports != null && communityReports >= 3) {
            return "community shield ($communityReports households)"
        }
        return null
    }

    fun sync(client: RelayClient, store: LocalStore): SyncResult {
        val resp = try {
            client.fetchThreatFeed()
        } catch (e: Exception) {
            return SyncResult(false, 0, "offline — cached shield kept (${e.message})")
        }
        if (!resp.optBoolean("ok", false)) {
            return SyncResult(false, 0, "bad feed shape — cached shield kept")
        }
        val arr: JSONArray = resp.optJSONArray("entries") ?: JSONArray()
        val entries = mutableListOf<Triple<String, Int, String>>()
        for (i in 0 until arr.length()) {
            val o = arr.getJSONObject(i)
            val h = o.optString("number_hash")
            if (h.length == 64 && h.all { c -> c in '0'..'9' || c in 'a'..'f' }) {
                entries.add(Triple(h, o.optInt("reports"), o.optString("category")))
            }
        }
        store.syncCommunity(entries)
        return SyncResult(true, entries.size, "shield synced: ${entries.size} community hashes")
    }

    /** Screening verdict for a caller hash: household → community → allow. */
    fun screenHash(store: LocalStore, hash: String): String? {
        if (hash.isEmpty()) return null
        if (store.isBlockedHash(hash)) return decide(true, null, false)
        if (store.isCommunityAllowed(hash)) return null
        return decide(false, store.communityHashes()[hash], false)
    }

    /** Household sync: sibling devices share the SAME household list without
     *  waiting for the 3-household community threshold. Best-effort. */
    fun syncHousehold(client: RelayClient, store: LocalStore,
                      householdId: String): SyncResult {
        val arr = try {
            client.householdBlocklist(householdId)
        } catch (e: Exception) {
            return SyncResult(false, 0, "offline — household list kept (${e.message})")
        }
        val entries = mutableListOf<Pair<String, String>>()
        for (i in 0 until arr.length()) {
            val o = arr.getJSONObject(i)
            val h = o.optString("number_hash")
            if (h.length == 64 && h.all { c -> c in '0'..'9' || c in 'a'..'f' }) {
                entries.add(h to o.optString("label"))
            }
        }
        store.syncHouseholdBlocklist(entries)
        return SyncResult(true, entries.size, "household synced: ${entries.size} hashes")
    }
}
