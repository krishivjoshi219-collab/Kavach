package com.kavach.guardian.data

import android.content.Context
import org.json.JSONArray
import org.json.JSONObject
import java.io.File

/** Private on-device store. Plaintext here never leaves except as ciphertext. */
class LocalStore(context: Context) {
    private val dir = File(context.filesDir, "kavach").apply { mkdirs() }

    private fun readList(name: String): JSONArray {
        val f = File(dir, "$name.json")
        return if (f.exists()) JSONArray(f.readText()) else JSONArray()
    }

    private fun writeList(name: String, arr: JSONArray) {
        File(dir, "$name.json").writeText(arr.toString())
    }

    fun addBlockedHash(hash: String, label: String) {
        val arr = readList("blocklist")
        for (i in 0 until arr.length()) {
            if (arr.getJSONObject(i).optString("h") == hash) return
        }
        arr.put(JSONObject().put("h", hash).put("label", label).put("ts", System.currentTimeMillis()))
        writeList("blocklist", arr)
    }

    fun removeBlockedHash(hash: String) {
        val arr = readList("blocklist")
        val kept = JSONArray()
        for (i in 0 until arr.length()) {
            if (arr.getJSONObject(i).optString("h") != hash) kept.put(arr.getJSONObject(i))
        }
        writeList("blocklist", kept)
    }

    fun isBlockedHash(hash: String): Boolean {
        val arr = readList("blocklist")
        for (i in 0 until arr.length()) {
            if (arr.getJSONObject(i).optString("h") == hash) return true
        }
        return false
    }

    fun blockedHashes(): List<String> {
        val arr = readList("blocklist")
        return List(arr.length()) { arr.getJSONObject(it).optString("h") }
    }

    fun logIncident(verdict: String, channel: String, summary: String) {
        val arr = readList("incidents")
        arr.put(JSONObject().put("verdict", verdict).put("channel", channel)
            .put("summary", summary).put("ts", System.currentTimeMillis()))
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

    // --- Quarantine inbox: scam SMS kept encrypted-at-rest locally ---

    fun quarantineAdd(senderHash: String, verdict: String, summary: String) {
        val arr = readList("quarantine")
        arr.put(JSONObject().put("h", senderHash).put("verdict", verdict)
            .put("summary", summary).put("ts", System.currentTimeMillis()))
        while (arr.length() > 200) arr.remove(0)
        writeList("quarantine", arr)
    }

    fun quarantine(): JSONArray = readList("quarantine")
}
