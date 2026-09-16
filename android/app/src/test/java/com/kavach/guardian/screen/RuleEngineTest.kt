package com.kavach.guardian.screen

import org.junit.Assert.assertEquals
import org.junit.Assert.assertFalse
import org.junit.Assert.assertTrue
import org.junit.Test

class RuleEngineTest {

    @Test
    fun testOtpThreatVerdictIsScam() {
        val scamText = "Your bank account has been frozen! Immediately share your OTP or police will arrest you."
        val verdict = RuleEngine.judge(scamText)
        assertEquals("SCAM", verdict.verdict)
        assertTrue(verdict.confidence >= 0.8)
        assertTrue(verdict.reasons.isNotEmpty())
    }

    @Test
    fun testSafeContactVerdictIsLikelySafe() {
        val normalText = "Hi dad, when are you coming home for dinner?"
        val verdict = RuleEngine.judge(normalText, knownContact = true)
        assertEquals("LIKELY_SAFE", verdict.verdict)
    }

    @Test
    fun testSuspiciousUrgency() {
        val suspiciousText = "Kindly click this link to update your KYC today itself."
        val verdict = RuleEngine.judge(suspiciousText)
        assertTrue(verdict.verdict in listOf("SUSPICIOUS", "UNCERTAIN"))
    }

    @Test
    fun testNumberHashingDeterministicAndSalted() {
        val hid = "test_household_123"
        val phone = "+919876543210"
        val h1 = RuleEngine.hashNumber(hid, phone)
        val h2 = RuleEngine.hashNumber(hid, phone)
        assertEquals(64, h1.length)
        assertEquals(h1, h2)

        // Different household must yield different hash
        val hOther = RuleEngine.hashNumber("other_household", phone)
        assertFalse(h1 == hOther)
    }
}
