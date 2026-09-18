package com.kavach.guardian.net

import org.json.JSONArray
import org.json.JSONObject
import java.io.OutputStreamWriter
import java.net.HttpURLConnection
import java.net.URL
import java.net.URLEncoder

/** Minimal JSON client for the Kavach blind-relay + mobile contract. No extra deps. */
class RelayClient(private val base: String) {

    private fun post(path: String, body: JSONObject): JSONObject {
        val url = URL(base.trimEnd('/') + path)
        val conn = (url.openConnection() as HttpURLConnection).apply {
            requestMethod = "POST"
            doOutput = true
            connectTimeout = 15000
            readTimeout = 20000
            setRequestProperty("Content-Type", "application/json")
        }
        OutputStreamWriter(conn.outputStream, Charsets.UTF_8).use { it.write(body.toString()) }
        val code = conn.responseCode
        val stream = if (code in 200..299) conn.inputStream else conn.errorStream
        val text = stream.bufferedReader(Charsets.UTF_8).use { it.readText() }
        conn.disconnect()
        return JSONObject(text)
    }

    private fun get(path: String, params: Map<String, String>): JSONObject {
        val qs = params.entries.joinToString("&") {
            "${it.key}=${URLEncoder.encode(it.value, "UTF-8")}"
        }
        val url = URL(base.trimEnd('/') + path + "?$qs")
        val conn = (url.openConnection() as HttpURLConnection).apply {
            connectTimeout = 15000
            readTimeout = 20000
        }
        val text = conn.inputStream.bufferedReader(Charsets.UTF_8).use { it.readText() }
        conn.disconnect()
        return JSONObject(text)
    }

    fun createHousehold(): String =
        post("/api/v1/households", JSONObject()).getString("household_id")

    fun pairInit(householdId: String, managerPubB64: String): JSONObject =
        post("/api/v1/pair/init", JSONObject()
            .put("household_id", householdId)
            .put("manager_pubkey", managerPubB64))

    fun pairComplete(code: String, seniorPubB64: String, seniorId: String): JSONObject =
        post("/api/v1/pair/complete", JSONObject()
            .put("pairing_code", code)
            .put("senior_pubkey", seniorPubB64)
            .put("senior_id", seniorId))

    fun pairPeer(householdId: String): JSONObject =
        get("/api/v1/pair/peer", mapOf("household_id" to householdId))

    fun pushBlob(householdId: String, sender: String, nonce: String, cipherB64: String): JSONObject =
        post("/api/v1/sync/push", JSONObject()
            .put("household_id", householdId)
            .put("sender", sender)
            .put("nonce", nonce)
            .put("ciphertext", cipherB64))

    fun pullBlobs(householdId: String, sinceId: Long): JSONArray =
        get("/api/v1/sync/pull",
            mapOf("household_id" to householdId, "since_id" to sinceId.toString()))
            .optJSONArray("blobs") ?: JSONArray()

    fun lookup(householdId: String, numberHash: String): JSONObject =
        post("/api/v1/screen/lookup", JSONObject()
            .put("household_id", householdId)
            .put("number_hash", numberHash))

    fun block(householdId: String, numberHash: String, label: String): JSONObject =
        post("/api/v1/screen/block", JSONObject()
            .put("household_id", householdId)
            .put("number_hash", numberHash)
            .put("label", label)
            .put("action", "block"))

    fun pollCommands(householdId: String, target: String): JSONArray =
        get("/api/v1/device/commands",
            mapOf("household_id" to householdId, "target" to target))
            .optJSONArray("commands") ?: JSONArray()

    fun ackCommand(id: Long): JSONObject =
        post("/api/v1/device/commands/$id/ack", JSONObject())

    fun consent(householdId: String, seniorId: String): JSONObject =
        get("/api/v1/consent", mapOf("household_id" to householdId, "senior_id" to seniorId))

    fun brainAsk(householdId: String, seniorId: String, snippet: String): JSONObject =
        post("/api/v1/brain/ask", JSONObject()
            .put("household_id", householdId)
            .put("senior_id", seniorId)
            .put("snippet", snippet))

    fun revokeConsent(householdId: String, seniorId: String): JSONObject =
        post("/api/v1/consent/revoke?household_id=${URLEncoder.encode(householdId, "UTF-8")}&senior_id=${URLEncoder.encode(seniorId, "UTF-8")}", JSONObject())

    fun sendCommand(householdId: String, seniorId: String, target: String, type: String, payload: String = ""): JSONObject =
        post("/api/v1/device/command", JSONObject()
            .put("household_id", householdId)
            .put("senior_id", seniorId)
            .put("target", target)
            .put("type", type)
            .put("payload_cipher", payload))

    fun setTier(householdId: String, tier: String): JSONObject =
        post("/api/v1/household/tier", JSONObject()
            .put("household_id", householdId)
            .put("tier", tier))

    fun getTier(householdId: String): JSONObject =
        get("/api/v1/household/tier", mapOf("household_id" to householdId))

    fun threatRadar(householdId: String): JSONObject =
        get("/api/v1/threat-radar", mapOf("household_id" to householdId))

    fun fetchPack(): JSONObject =
        get("/api/v1/rules/pack", mapOf())

    fun fetchThreatFeed(): JSONObject =
        get("/api/v1/threat-feed", mapOf())
}
