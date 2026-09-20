package com.kavach.guardian.screen

/** On-device port of the server red-flag engine. Same rules, weights, thresholds. */
object RuleEngine {

    data class Hit(val code: String, val label: String, val weight: Int, val example: String)
    data class Verdict(val verdict: String, val confidence: Double, val reasons: List<String>)

    private data class Rule(val code: String, val label: String, val patterns: List<String>,
                            val weight: Int)

    private val RULES = listOf(
        Rule("OTP_ASK", "Asked for OTP / password / PIN",
            listOf("otp", "ओटीपी", "one-time", "one time", "password", "पासवर्ड", "pin", "पिन", "cvv", "expir"), 3),
        Rule("THREAT", "Threats — freeze, arrest, legal action",
            listOf("froze", "frozen", "block", "arrest", "गिरफ्तार", "police", "पुलिस", "fir", "cbi", "court", "कोर्ट", "legal action",
                "jail", "digital arrest", "seiz", "closed", "suspended"), 3),
        Rule("URGENCY", "Artificial urgency",
            listOf("immediately", "तुरंत", "right now", "urgent", "hurry", "at once",
                "last warning", "last chance", "today itself", "tonight", "don't hang", "don't disconnect", "do not hang"), 2),
        Rule("IMPERSONATION", "Claims to be bank / police / government",
            listOf("bank", "बैंक", "reserve bank", "rbi", "cbi", "cyber cell", "crime branch", "income tax",
                "electricity", "bijli", "बिजली", "gas agency", "insurance"), 2),
        Rule("PAYMENT_EXTORT", "Demands money",
            listOf("gift card", "google play", "voucher", "wire", "western union", "crypto",
                "bitcoin", "usdt", "upi collect", "upi request", "collect request",
                "qr code", "क्यूआर", "processing fee", "refundable", "deposit", "fine", "paise", "पैसा"), 3),
        Rule("REMOTE_ACCESS", "Asks to install a screen-sharing app",
            listOf("anydesk", "teamviewer", "rustdesk", "screen shar", "remote access",
                "install", "share.*screen", "give.*access"), 3),
        Rule("KYC_PRIZE", "KYC update / prize lure with a link",
            listOf("kyc", "केवाईसी", "lottery", "लॉटरी", "prize", "इनाम", "reward points", "lucky draw", "click",
                "link", "whatsapp", "apk"), 2),
        Rule("ID_HARVEST", "Fishes for ID numbers",
            listOf("aadhaar", "aadhar", "आधार", "pan card", "pan number", "account number",
                "debit card", "credit card", "date of birth", "dob", "maiden"), 2),
    )

    /** Short tokens need word-boundary matching: bare contains() overmatches
     * ("pin" in "shopping", "otp" in "photography", "link" in "linked"). */
    private val WORD_TOKENS = setOf("otp", "pin", "upi", "kyc", "link", "apk")

    private fun matches(low: String, pattern: String): Boolean {
        return if (pattern in WORD_TOKENS) {
            Regex("\\b${Regex.escape(pattern)}\\b").containsMatchIn(low)
        } else {
            low.contains(pattern)
        }
    }

    fun extract(text: String): List<Hit> {
        val low = text.lowercase()
        return RULES.mapNotNull { r ->
            val found = r.patterns.firstOrNull { matches(low, it) }
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

    /** Dynamic path: judge with a fetched rule pack (regex patterns, same
     *  thresholds). Baked-in judge() above stays the offline fallback. */
    fun judgeWithPack(text: String, pack: List<com.kavach.guardian.net.RulePack.PackRule>,
                      knownContact: Boolean = false): Verdict {
        val hits = pack.mapNotNull { r ->
            try {
                val m = Regex(r.pattern, RegexOption.IGNORE_CASE).find(text)
                if (m != null) Hit(r.code, r.label, r.weight, m.value.take(24)) else null
            } catch (_: Exception) {
                null // a bad pack pattern never breaks judging; baked-in covers
            }
        }
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
}
