package com.kavach.guardian.ui

import android.content.Context
import android.graphics.Color
import android.graphics.drawable.GradientDrawable
import android.widget.Button
import android.widget.TextView

/** God-tier design system tokens and programmatic UI builders. */
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

    // Guardian Dark tokens
    const val DARK_BG = "#121417"
    const val DARK_SURFACE = "#1C2026"
    const val DARK_BORDER = "#2C3440"

    fun c(hex: String): Int = Color.parseColor(hex)

    const val TITLE_SP = 30f
    const val BODY_SP = 20f
    const val SMALL_SP = 15f
    const val BTN_SP = 18f
    const val PAD = 40

    fun rounded(context: Context, bgColor: Int, radiusDp: Float = 16f, strokeColor: Int = Color.TRANSPARENT, strokeWidthDp: Float = 0f): GradientDrawable {
        return GradientDrawable().apply {
            shape = GradientDrawable.RECTANGLE
            cornerRadius = radiusDp * context.resources.displayMetrics.density
            setColor(bgColor)
            if (strokeWidthDp > 0) {
                setStroke((strokeWidthDp * context.resources.displayMetrics.density).toInt(), strokeColor)
            }
        }
    }

    fun pill(context: Context, text: String, textColor: Int, bgColor: Int, textSizeSp: Float = 11f): TextView {
        return TextView(context).apply {
            this.text = text
            textSize = textSizeSp
            typeface = android.graphics.Typeface.DEFAULT_BOLD
            setTextColor(textColor)
            background = rounded(context, bgColor, 20f)
            setPadding(24, 8, 24, 8)
        }
    }

    fun styledButton(context: Context, text: String, bgColor: Int, textColor: Int = Color.WHITE, radiusDp: Float = 12f, onClick: () -> Unit): Button {
        return Button(context).apply {
            this.text = text
            textSize = 15f
            typeface = android.graphics.Typeface.DEFAULT_BOLD
            setTextColor(textColor)
            background = rounded(context, bgColor, radiusDp)
            setPadding(24, 28, 24, 28)
            isAllCaps = false
            setOnClickListener { onClick() }
        }
    }
}
