package com.kavach.guardian.net

import org.junit.Assert.assertEquals
import org.junit.Assert.assertNull
import org.junit.Test

class CommunityShieldTest {

    @Test
    fun testHouseholdListWins() {
        assertEquals("household list",
            CommunityShield.decide(localBlocked = true, communityReports = 9, overridden = false))
    }

    @Test
    fun testCommunityBlocksAtThreshold() {
        assertEquals("community shield (3 households)",
            CommunityShield.decide(localBlocked = false, communityReports = 3, overridden = false))
    }

    @Test
    fun testBelowThresholdAllows() {
        assertNull(CommunityShield.decide(localBlocked = false, communityReports = 2,
            overridden = false))
        assertNull(CommunityShield.decide(localBlocked = false, communityReports = null,
            overridden = false))
    }

    @Test
    fun testManagerOverrideBeatsCommunity() {
        assertNull(CommunityShield.decide(localBlocked = false, communityReports = 25,
            overridden = true))
    }
}
