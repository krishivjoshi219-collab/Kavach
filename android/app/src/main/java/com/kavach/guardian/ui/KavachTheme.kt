package com.kavach.guardian.ui

import android.content.Context
import android.graphics.Color
import android.graphics.Typeface
import android.graphics.drawable.GradientDrawable
import android.view.Gravity
import android.widget.Button
import android.widget.LinearLayout
import android.widget.TextView

/**
 * World-Class Production Design System for Kavach.
 * Eliminates vibe-coded clunkiness; delivers Apple / Linear level craftsmanship.
 */
object KavachTheme {

    // --- Senior Sanctuary Palette (Warm, High-Legibility, Dignified) ---
    val SENIOR_BG = Color.parseColor("#FBF9F5")        // Soft Alabaster Cream
    val SENIOR_SURFACE = Color.parseColor("#FFFFFF")   // Pure White Card
    val SENIOR_BORDER = Color.parseColor("#EAE6DF")    // Subtle Warm Border
    val SENIOR_TEXT = Color.parseColor("#1C1917")      // Deep Stone 900
    val SENIOR_MUTED = Color.parseColor("#78716C")     // Warm Stone 500
    val SENIOR_GREEN = Color.parseColor("#15803D")     // Emerald 700
    val SENIOR_GREEN_BG = Color.parseColor("#DCFCE7")  // Emerald 100
    val SENIOR_AMBER = Color.parseColor("#B45309")     // Warm Amber 700
    val SENIOR_AMBER_BG = Color.parseColor("#FEF3C7")  // Amber 100
    val SENIOR_RED = Color.parseColor("#B91C1C")       // Terracotta 700
    val SENIOR_RED_BG = Color.parseColor("#FEE2E2")    // Terracotta 100

    // --- Guardian Command Center Palette (Obsidian / Precision Dark) ---
    val DARK_BG = Color.parseColor("#090A0C")          // True Obsidian
    val DARK_SURFACE = Color.parseColor("#13151A")     // Slate Charcoal Surface
    val DARK_SURFACE_ELEVATED = Color.parseColor("#1A1D24") // Elevated Card
    val DARK_BORDER = Color.parseColor("#22262F")      // 1px Slate Border
    val DARK_TEXT = Color.parseColor("#F8FAFC")        // Slate 50
    val DARK_MUTED = Color.parseColor("#94A3B8")       // Slate 400
    val EMERALD_PRO = Color.parseColor("#10B981")      // Emerald Glow
    val EMERALD_PRO_BG = Color.parseColor("#064E3B")   // Deep Emerald Surface
    val GOLD_VIP = Color.parseColor("#F59E0B")         // Amber / Gold Accent
    val GOLD_VIP_BG = Color.parseColor("#451A03")      // Deep Amber Surface
    val DANGER_RED = Color.parseColor("#EF4444")       // Crisp Alert Red
    val DANGER_RED_BG = Color.parseColor("#3B1010")    // Deep Crimson Surface

    fun dp(context: Context, value: Float): Int {
        return (value * context.resources.displayMetrics.density).toInt()
    }

    fun rounded(
        context: Context,
        bgColor: Int,
        radiusDp: Float = 16f,
        strokeColor: Int = Color.TRANSPARENT,
        strokeWidthDp: Float = 0f
    ): GradientDrawable {
        return GradientDrawable().apply {
            shape = GradientDrawable.RECTANGLE
            cornerRadius = radiusDp * context.resources.displayMetrics.density
            setColor(bgColor)
            if (strokeWidthDp > 0) {
                setStroke((strokeWidthDp * context.resources.displayMetrics.density).toInt(), strokeColor)
            }
        }
    }

    fun card(
        context: Context,
        isDark: Boolean = false,
        radiusDp: Float = 16f,
        paddingDp: Int = 20
    ): LinearLayout {
        return LinearLayout(context).apply {
            orientation = LinearLayout.VERTICAL
            background = if (isDark) {
                rounded(context, DARK_SURFACE, radiusDp, DARK_BORDER, 1f)
            } else {
                rounded(context, SENIOR_SURFACE, radiusDp, SENIOR_BORDER, 1f)
            }
            val p = dp(context, paddingDp.toFloat())
            setPadding(p, p, p, p)
        }
    }

    fun badge(
        context: Context,
        text: String,
        textColor: Int,
        bgColor: Int
    ): TextView {
        return TextView(context).apply {
            this.text = text
            textSize = 11f
            typeface = Typeface.DEFAULT_BOLD
            setTextColor(textColor)
            background = rounded(context, bgColor, 12f)
            val px = dp(context, 10f)
            val py = dp(context, 4f)
            setPadding(px, py, px, py)
        }
    }

    fun sectionHeader(
        context: Context,
        title: String,
        isDark: Boolean = false
    ): TextView {
        return TextView(context).apply {
            text = title.uppercase()
            textSize = 11f
            letterSpacing = 0.08f
            typeface = Typeface.DEFAULT_BOLD
            setTextColor(if (isDark) DARK_MUTED else SENIOR_MUTED)
            val pTop = dp(context, 20f)
            val pBot = dp(context, 8f)
            setPadding(0, pTop, 0, pBot)
        }
    }

    fun button(
        context: Context,
        text: String,
        bgColor: Int,
        textColor: Int = Color.WHITE,
        radiusDp: Float = 12f,
        minHeightDp: Float = 50f,
        onClick: () -> Unit
    ): Button {
        return Button(context).apply {
            this.text = text
            textSize = 14f
            typeface = Typeface.DEFAULT_BOLD
            setTextColor(textColor)
            background = rounded(context, bgColor, radiusDp)
            val px = dp(context, 16f)
            val py = dp(context, 12f)
            setPadding(px, py, px, py)
            minHeight = dp(context, minHeightDp)
            isAllCaps = false
            setOnClickListener { onClick() }
        }
    }

    // --- God-tier round 2: verdict language + senior-proof actions ---

    /** Verdict → (accent, soft background). One source so siren, vault,
     *  war-room and lab never disagree on what SCAM red means. */
    fun verdictColors(verdict: String, isDark: Boolean): Pair<Int, Int> {
        return when (verdict) {
            "SCAM" -> if (isDark) DANGER_RED to DANGER_RED_BG
                      else SENIOR_RED to SENIOR_RED_BG
            "SUSPICIOUS" -> if (isDark) GOLD_VIP to GOLD_VIP_BG
                            else SENIOR_AMBER to SENIOR_AMBER_BG
            "LIKELY_SAFE" -> if (isDark) EMERALD_PRO to EMERALD_PRO_BG
                             else SENIOR_GREEN to SENIOR_GREEN_BG
            else -> if (isDark) DARK_MUTED to DARK_SURFACE_ELEVATED
                    else SENIOR_MUTED to SENIOR_BORDER
        }
    }

    /** Senior-proof action: 64dp one-thumb target, 18sp, never all-caps. */
    fun seniorActionButton(
        context: Context,
        text: String,
        bgColor: Int = SENIOR_GREEN,
        textColor: Int = Color.WHITE,
        onClick: () -> Unit
    ): Button {
        return button(context, text, bgColor, textColor,
            radiusDp = 14f, minHeightDp = 64f, onClick = onClick).apply {
            textSize = 18f
        }
    }

    /** Left accent stripe that turns any card into a verdict card. */
    fun accentStripe(context: Context, color: Int, widthDp: Float = 6f): android.view.View {
        return android.view.View(context).apply {
            setBackgroundColor(color)
            layoutParams = LinearLayout.LayoutParams(
                dp(context, widthDp),
                LinearLayout.LayoutParams.MATCH_PARENT
            )
        }
    }

    /** Live shield pill: green pulse dot + status words for the sanctuary. */
    fun shieldPill(context: Context, live: Boolean): TextView {
        return badge(context,
            if (live) "● SHIELD LIVE" else "○ SHIELD PAUSED",
            if (live) SENIOR_GREEN else SENIOR_AMBER,
            if (live) SENIOR_GREEN_BG else SENIOR_AMBER_BG)
    }
}
