package com.kavach.guardian.crypto

import java.security.MessageDigest

/** Signal-style safety numbers: derived from BOTH public keys, never hardcoded. */
object SasFingerprint {
    private val EMOJIS = listOf(
        "🛡️", "🔑", "🌟", "🔔", "🐘", "🔥", "🌙", "⚡", "🍀", "🎯",
        "🐬", "🦁", "🌊", "🔒", "💛", "🚨", "📱", "🌈", "⭐", "🎵",
        "🍎", "🚀", "🐢", "🦋", "🌻", "🍩", "⚽", "🎲", "📚", "💎",
        "🌍", "🔆"
    )

    fun of(managerPubB64: String, seniorPubB64: String): String {
        val md = MessageDigest.getInstance("SHA-256")
        val digest = md.digest((managerPubB64 + "|" + seniorPubB64).toByteArray())
        return (0 until 5).joinToString(" ") { i ->
            EMOJIS[(digest[i].toInt() and 0xFF) % EMOJIS.size]
        }
    }

    fun fridgeCode(): String {
        val chars = "ABCDEFGHJKMNPQRSTUVWXYZ23456789"
        val r = java.security.SecureRandom()
        fun grp() = (0 until 4).map { chars[r.nextInt(chars.length)] }.joinToString("")
        return "KVCH-${grp()}-${grp()}"
    }
}
