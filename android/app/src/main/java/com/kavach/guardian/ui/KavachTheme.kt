package com.kavach.guardian.ui

import android.graphics.Color

/** God-tier senior-first tokens. One source of truth for all activities. */
object KavachTheme {
    const val BG = "#FAF6EC"
    const val INK = "#2B2118"
    const val MUTED = "#8A7660"
    const val ACCENT = "#E26A1B"
    const val ACCENT_DEEP = "#9A3D0C"
    const val GREEN = "#1F7A4D"
    const val GREEN_BG = "#E6F4EC"
    const val RED = "#8A0000"
    const val RED_BRIGHT = "#C62828"
    const val CARD = "#FFFFFF"
    const val LINE = "#E8DCC3"

    fun c(hex: String): Int = Color.parseColor(hex)

    const val TITLE_SP = 30f
    const val BODY_SP = 20f
    const val SMALL_SP = 15f
    const val BTN_SP = 21f
    const val PAD = 40
}
