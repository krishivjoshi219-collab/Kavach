package com.kavach.guardian.net

import android.util.Base64
import com.google.crypto.tink.subtle.Ed25519Verify
import com.kavach.guardian.data.LocalStore
import org.json.JSONArray
import org.json.JSONObject

/** Versioned signed rule packs: the shield learns, offline-first, trust-verified.
 *
 *  Apply rule: signature verifies AND version is newer, else keep baked-in /
 *  last-good rules and say so on the Audit screen. Raw Ed25519 via Tink
 *  subtle (audited, already a dependency) — no new crypto code.
 */
object RulePack {

    data class PackRule(val code: String, val label: String, val pattern: String,
                        val weight: Int, val meaning: String)
    data class ActivePack(val version: Int, val rules: List<PackRule>,
                          val updatedAt: Long, val sigOk: Boolean)
    data class FetchResult(val ok: Boolean, val version: Int, val note: String)

    /** Canonical JSON: sorted keys, no spaces — must match the server's
     *  json.dumps(sort_keys=True, separators=(",",":")) byte-for-byte. */
    fun canonical(v: Any?): String = when (v) {
        null, JSONObject.NULL -> "null"
        is String -> quote(v)
        is Number, is Boolean -> v.toString()
        is JSONObject -> {
            val keys = mutableListOf<String>()
            val it = v.keys()
            while (it.hasNext()) keys.add(it.next())
            keys.sorted().joinToString(",", "{", "}") { k -> quote(k) + ":" + canonical(v.get(k)) }
        }
        is JSONArray -> (0 until v.length()).joinToString(",", "[", "]") { canonical(v.get(it)) }
        else -> quote(v.toString())
    }

    private fun quote(s: String): String {
        val sb = StringBuilder("\"")
        for (c in s) when (c) {
            '"' -> sb.append("\\\"")
            '\\' -> sb.append("\\\\")
            '\n' -> sb.append("\\n")
            '\r' -> sb.append("\\r")
            '\t' -> sb.append("\\t")
            '\b' -> sb.append("\\b")
            else -> if (c < ' ') sb.append(String.format("\\u%04x", c.code)) else sb.append(c)
        }
        return sb.append("\"").toString()
    }

    fun verify(packJson: JSONObject, sigB64: String, pubB64: String): Boolean {
        return try {
            val verifier = Ed25519Verify(Base64.decode(pubB64, Base64.DEFAULT))
            verifier.verify(Base64.decode(sigB64, Base64.DEFAULT),
                canonical(packJson).toByteArray(Charsets.UTF_8))
            true
        } catch (_: Exception) {
            false
        }
    }

    fun parseRules(packJson: JSONObject): List<PackRule> {
        val arr = packJson.optJSONArray("rules") ?: JSONArray()
        return List(arr.length()) {
            val o = arr.getJSONObject(it)
            PackRule(o.optString("code"), o.optString("label"), o.optString("pattern"),
                o.optInt("weight"), o.optString("meaning"))
        }
    }

    fun activePack(store: LocalStore): ActivePack? {
        val raw = store.getString("rules_pack_json") ?: return null
        return try {
            val o = JSONObject(raw)
            ActivePack(o.optInt("pack_version"), parseRules(o),
                store.getString("rules_pack_updated")?.toLongOrNull() ?: 0L,
                store.getString("rules_pack_sig") == "ok")
        } catch (_: Exception) {
            null
        }
    }

    /** Fetch → verify → apply-if-newer. Returns what happened, honestly. */
    fun refresh(client: RelayClient, store: LocalStore): FetchResult {
        val resp = try {
            client.fetchPack()
        } catch (e: Exception) {
            return FetchResult(false, -1, "offline — keeping last-good rules (${e.message})")
        }
        val pack = resp.optJSONObject("pack") ?: return FetchResult(false, -1, "bad pack shape")
        val version = pack.optInt("pack_version", -1)
        val current = store.getString("rules_pack_version")?.toIntOrNull() ?: 0
        if (version <= current) return FetchResult(true, current, "already current (v$current)")
        val ok = verify(pack, resp.optString("signature"), resp.optString("public_key"))
        if (!ok) return FetchResult(false, current, "signature FAILED — pack rejected, last-good kept")
        store.putString("rules_pack_json", pack.toString())
        store.putString("rules_pack_version", version.toString())
        store.putString("rules_pack_updated", System.currentTimeMillis().toString())
        store.putString("rules_pack_sig", "ok")
        return FetchResult(true, version, "rules v$version applied, signature OK")
    }
}
