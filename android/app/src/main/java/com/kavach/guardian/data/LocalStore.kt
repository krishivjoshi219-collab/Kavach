package com.kavach.guardian.data

import android.content.Context
import org.json.JSONArray
import org.json.JSONObject
import java.io.File

/** Private on-device store with thread-safe O(1) in-memory caching. Plaintext here never leaves except as ciphertext. */
class LocalStore(context: Context) {
    private val dir = File(context.filesDir, "kavach").apply { mkdirs() }
    private val fileLock = Any()

    // O(1) in-memory fast caches for high-frequency call screening
    private val blockedCache = java.util.concurrent.ConcurrentHashMap.newKeySet<String>()
    private val communityAllowCache = java.util.concurrent.ConcurrentHashMap.newKeySet<String>()

    init {
        synchronized(fileLock) {
            val arr = readList("blocklist")
            for (i in 0 until arr.length()) {
                val h = arr.getJSONObject(i).optString("h")
                if (h.isNotEmpty()) blockedCache.add(h)
            }
            val allowArr = readList("community_allow")
            for (i in 0 until allowArr.length()) {
                val h = allowArr.getJSONObject(i).optString("h")
                if (h.isNotEmpty()) communityAllowCache.add(h)
            }
        }
    }

    private fun readList(name: String): JSONArray {
        val f = File(dir, "$name.json")
        return if (f.exists()) JSONArray(f.readText()) else JSONArray()
    }

    private fun writeList(name: String, arr: JSONArray) {
        synchronized(fileLock) {
            File(dir, "$name.json").writeText(arr.toString())
        }
    }

    fun addBlockedHash(hash: String, label: String) {
        if (hash.isEmpty()) return
        blockedCache.add(hash)
        synchronized(fileLock) {
            val arr = readList("blocklist")
            for (i in 0 until arr.length()) {
                if (arr.getJSONObject(i).optString("h") == hash) return
            }
            arr.put(JSONObject().put("h", hash).put("label", label).put("ts", System.currentTimeMillis()))
            writeList("blocklist", arr)
        }
    }

    fun removeBlockedHash(hash: String) {
        if (hash.isEmpty()) return
        blockedCache.remove(hash)
        synchronized(fileLock) {
            val arr = readList("blocklist")
            val kept = JSONArray()
            for (i in 0 until arr.length()) {
                if (arr.getJSONObject(i).optString("h") != hash) kept.put(arr.getJSONObject(i))
            }
            writeList("blocklist", kept)
        }
    }

    fun isBlockedHash(hash: String): Boolean {
        if (hash.isEmpty()) return false
        return blockedCache.contains(hash)
    }

    fun blockedHashes(): List<String> = blockedCache.toList()

    fun logIncident(verdict: String, channel: String, summary: String) {
        logIncident(verdict, channel, summary, "")
    }

    /** Sender-hash-aware log: FamilyActivity blocks the exact hash that
     *  screening matches. Older entries without "h" fall back to no-op block. */
    fun logIncident(verdict: String, channel: String, summary: String, senderHash: String) {
        val arr = readList("incidents")
        arr.put(JSONObject().put("verdict", verdict).put("channel", channel)
            .put("summary", summary).put("h", senderHash).put("ts", System.currentTimeMillis()))
        while (arr.length() > 100) arr.remove(0)
        writeList("incidents", arr)
    }

    fun incidents(): JSONArray = readList("incidents")

    fun putString(key: String, value: String) {
        val f = File(dir, "kv_$key.txt")
        f.writeText(value)
    }

    fun getString(key: String): String? {
        val f = File(dir, "kv_$key.txt")
        return if (f.exists()) f.readText() else null
    }

    // --- True E2E peer state: public key of the other side + epoch ---

    fun putPeerPub(b64: String) = putString("peer_pub_b64", b64)

    fun getPeerPub(): String? = getString("peer_pub_b64")

    fun clearPeer() {
        File(dir, "kv_peer_pub_b64.txt").delete()
    }

    fun putEpoch(e: Int) = putString("epoch", e.toString())

    fun getEpoch(): Int = getString("epoch")?.toIntOrNull() ?: 0

    fun putFridgeCode(code: String) = putString("fridge_code", code)

    fun getFridgeCode(): String? = getString("fridge_code")

    // --- Consent cache: E2E forwarding needs lent forward_sms; revoke stops it.
    // Default allow (first run / offline) so the demo shield never goes silent;
    // an explicit "0" (fetched from /api/v1/consent or senior revoke) stops
    // forwarding while quarantine + siren stay fully on-device.

    fun putForwardSmsConsent(allowed: Boolean) =
        putString("consent_forward_sms", if (allowed) "1" else "0")

    fun forwardSmsAllowed(): Boolean = getString("consent_forward_sms") != "0"

    /** Merge sibling-device household blocks (server is source of truth). */
    fun syncHouseholdBlocklist(entries: List<Pair<String, String>>) {
        synchronized(fileLock) {
            val arr = readList("blocklist")
            val known = mutableSetOf<String>()
            for (i in 0 until arr.length()) known.add(arr.getJSONObject(i).optString("h"))
            var changed = false
            for ((h, label) in entries) {
                if (h.length != 64 || h in known) continue
                arr.put(JSONObject().put("h", h).put("label", label)
                    .put("ts", System.currentTimeMillis()))
                known.add(h)
                blockedCache.add(h)
                changed = true
            }
            if (changed) writeList("blocklist", arr)
        }
    }

    // --- Quarantine inbox: scam SMS kept in private app storage locally ---
    // Note: plain JSON in the app sandbox (not encrypted-at-rest). Full bodies
    // never leave except as Tink ECIES ciphertext to the paired manager.

    fun quarantineAdd(senderHash: String, verdict: String, summary: String) {
        val arr = readList("quarantine")
        arr.put(JSONObject().put("h", senderHash).put("verdict", verdict)
            .put("summary", summary).put("ts", System.currentTimeMillis()))
        while (arr.length() > 200) arr.remove(0)
        writeList("quarantine", arr)
    }

    fun quarantine(): JSONArray = readList("quarantine")

    // --- Community shield: cached threat-feed hashes, manager-sovereign ---

    fun syncCommunity(entries: List<Triple<String, Int, String>>) {
        val arr = JSONArray()
        for ((h, reports, cat) in entries) {
            arr.put(JSONObject().put("h", h).put("reports", reports)
                .put("cat", cat).put("ts", System.currentTimeMillis()))
        }
        writeList("community", arr)
    }

    fun communityHashes(): Map<String, Int> {
        val arr = readList("community")
        val out = LinkedHashMap<String, Int>()
        for (i in 0 until arr.length()) {
            val o = arr.getJSONObject(i)
            out[o.optString("h")] = o.optInt("reports")
        }
        return out
    }

    fun communityAllowOverride(hash: String) {
        if (hash.isEmpty()) return
        communityAllowCache.add(hash)
        synchronized(fileLock) {
            val arr = readList("community_allow")
            for (i in 0 until arr.length()) {
                if (arr.getJSONObject(i).optString("h") == hash) return
            }
            arr.put(JSONObject().put("h", hash).put("ts", System.currentTimeMillis()))
            writeList("community_allow", arr)
        }
    }

    fun isCommunityAllowed(hash: String): Boolean {
        if (hash.isEmpty()) return false
        return communityAllowCache.contains(hash)
    }

    fun clearCommunity() {
        writeList("community", JSONArray())
    }
}
