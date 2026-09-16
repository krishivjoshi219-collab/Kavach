package com.kavach.guardian.screen

/** On-device port of the server red-flag engine. Same rules, weights, thresholds. */
object RuleEngine {

    data class Hit(val code: String, val label: String, val weight: Int, val example: String)
    data class Verdict(val verdict: String, val confidence: Double, val reasons: List<String>)

    private data class Rule(val code: String, val label: String, val patterns: List<String>,
                            val weight: Int)

    private val RULES = listOf(
        Rule("OTP_ASK", "Asked for OTP / password / PIN",
            listOf("otp", "one-time", "one time", "password", "pin", "cvv"), 3),
        Rule("THREAT", "Threats — freeze, arrest, legal action",
            listOf("froze", "frozen", "block", "arrest", "police", "court", "legal action",
                "jail", "digital arrest", "closed", "suspended"), 3),
        Rule("URGENCY", "Artificial urgency",
            listOf("immediately", "right now", "urgent", "hurry", "at once",
                "last warning", "last chance", "today itself", "don't hang"), 2),
        Rule("IMPERSONATION", "Claims to be bank / police / government",
            listOf("bank", "reserve bank", "rbi", "cyber cell", "crime branch", "income tax",
                "electricity", "gas agency", "insurance"), 2),
        Rule("PAYMENT_EXTORT", "Demands money",
            listOf("gift card", "google play", "voucher", "wire", "western union", "crypto",
                "bitcoin", "usdt", "upi", "qr code", "collect request", "processing fee", "fine"), 3),
        Rule("REMOTE_ACCESS", "Asks to install a screen-sharing app",
            listOf("anydesk", "teamviewer", "rustdesk", "screen shar", "remote access",
                "install", "share", "screen"), 3),
        Rule("KYC_PRIZE", "KYC update / prize lure with a link",
            listOf("kyc", "lottery", "prize", "reward points", "lucky draw", "click",
                "link", "whatsapp", "apk"), 2),
        Rule("ID_HARVEST", "Fishes for ID numbers",
            listOf("aadhaar", "aadhar", "pan card", "pan number", "account number",
                "debit card", "credit card", "date of birth"), 2),
    )

    fun extract(text: String): List<Hit> {
        val low = text.lowercase()
        return RULES.mapNotNull { r ->
            val found = r.patterns.firstOrNull { low.contains(it) }
            if (found != null) Hit(r.code, r.label, r.weight, found) else null
        }
    }

    fun judge(text: String, knownContact: Boolean = false): Verdict {
        val hits = extract(text)
        val score = hits.sumOf { it.weight }
        val codes = hits.map { it.code }.toSet()
        val reasons = hits.map { "${it.label} (e.g. “${it.example}”)" }
        if (knownContact && score == 0) {
            return Verdict("LIKELY_SAFE", 0.8,
                listOf("Caller is a saved safe contact; nothing suspicious asked."))
        }
        if (score >= 5 || (setOf("OTP_ASK", "THREAT").intersect(codes).isNotEmpty() && score >= 4)) {
            return Verdict("SCAM", minOf(0.95, 0.65 + 0.05 * score), reasons)
        }
        if (score >= 3) return Verdict("SUSPICIOUS", 0.6, reasons)
        if (hits.isNotEmpty()) return Verdict("UNCERTAIN", 0.45, reasons)
        return Verdict("UNCERTAIN", 0.4,
            listOf("Not enough detail yet — one or two more answers will settle it."))
    }

    /** Household-salted SHA-256 so raw numbers never leave the phone. */
    fun hashNumber(householdId: String, e164: String): String {
        val md = java.security.MessageDigest.getInstance("SHA-256")
        val bytes = md.digest(("kavach|$householdId|${e164.trim()}").toByteArray())
        return bytes.joinToString("") { "%02x".format(it) }
    }
}
