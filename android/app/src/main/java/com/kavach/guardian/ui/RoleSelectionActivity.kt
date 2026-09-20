package com.kavach.guardian.ui

import android.content.Intent
import android.graphics.Color
import android.graphics.Typeface
import android.os.Bundle
import android.view.Gravity
import android.widget.LinearLayout
import android.widget.ScrollView
import android.widget.TextView
import androidx.appcompat.app.AppCompatActivity
import com.kavach.guardian.KavachApp

/**
 * First-Launch Role Selection:
 * Separates the Senior Sanctuary and the Adult Child Command Center into dedicated
 * phone experiences. No confusing mode switches on the senior's screen.
 */
class RoleSelectionActivity : AppCompatActivity() {

    override fun onCreate(savedInstanceState: Bundle?) {
        super.onCreate(savedInstanceState)

        val app = application as KavachApp
        val store = app.store

        // Flavor preset: senior/manager APKs boot straight to their role so the
        // 90-second demo never wastes time on a chooser. Dual (default) keeps it.
        when (com.kavach.guardian.BuildConfig.APP_ROLE) {
            "senior" -> {
                store.putString("app_role", "senior")
                startActivity(Intent(this, SeniorActivity::class.java))
                finish()
                return
            }
            "guardian" -> {
                store.putString("app_role", "guardian")
                startActivity(Intent(this, FamilyActivity::class.java))
                finish()
                return
            }
        }
        // Fast-path for already configured devices
        val existingRole = store.getString("app_role")
        if (existingRole == "senior") {
            startActivity(Intent(this, SeniorActivity::class.java))
            finish()
            return
        } else if (existingRole == "guardian") {
            startActivity(Intent(this, FamilyActivity::class.java))
            finish()
            return
        }

        val scroll = ScrollView(this).apply {
            isFillViewport = true
            setBackgroundColor(KavachTheme.DARK_BG)
        }

        val pad = KavachTheme.dp(this, 24f)
        val root = LinearLayout(this).apply {
            orientation = LinearLayout.VERTICAL
            setPadding(pad, KavachTheme.dp(this@RoleSelectionActivity, 48f), pad, pad)
            gravity = Gravity.CENTER_HORIZONTAL
        }
        scroll.addView(root)

        val logo = TextView(this).apply {
            text = "🛡️"
            textSize = 48f
            gravity = Gravity.CENTER
        }
        root.addView(logo)

        val title = TextView(this).apply {
            text = "Welcome to Kavach"
            textSize = 26f
            typeface = Typeface.DEFAULT_BOLD
            setTextColor(KavachTheme.DARK_TEXT)
            gravity = Gravity.CENTER
            setPadding(0, KavachTheme.dp(this@RoleSelectionActivity, 12f), 0, KavachTheme.dp(this@RoleSelectionActivity, 6f))
        }
        root.addView(title)

        val subtitle = TextView(this).apply {
            text = "Choose how this device will participate in your family's fraud defense shield:"
            textSize = 14f
            setTextColor(KavachTheme.DARK_MUTED)
            gravity = Gravity.CENTER
            setLineSpacing(3f, 1.2f)
            setPadding(0, 0, 0, KavachTheme.dp(this@RoleSelectionActivity, 32f))
        }
        root.addView(subtitle)

        val cardLp = LinearLayout.LayoutParams(
            LinearLayout.LayoutParams.MATCH_PARENT,
            LinearLayout.LayoutParams.WRAP_CONTENT
        ).apply { setMargins(0, 0, 0, KavachTheme.dp(this@RoleSelectionActivity, 20f)) }

        // Role 1: Senior Sanctuary
        val seniorCard = KavachTheme.card(this, isDark = true, radiusDp = 18f, paddingDp = 22).apply {
            isClickable = true
            isFocusable = true
            background = KavachTheme.rounded(this@RoleSelectionActivity, KavachTheme.DARK_SURFACE, 18f, Color.parseColor("#3B82F6"), 1.5f)
            setOnClickListener {
                store.putString("app_role", "senior")
                startActivity(Intent(this@RoleSelectionActivity, SeniorActivity::class.java))
                finish()
            }
        }
        val seniorRow = LinearLayout(this).apply {
            orientation = LinearLayout.HORIZONTAL
            gravity = Gravity.CENTER_VERTICAL
        }
        val seniorIcon = TextView(this).apply {
            text = "🧓"
            textSize = 32f
            setPadding(0, 0, KavachTheme.dp(this@RoleSelectionActivity, 16f), 0)
        }
        val seniorTextCol = LinearLayout(this).apply {
            orientation = LinearLayout.VERTICAL
            layoutParams = LinearLayout.LayoutParams(0, LinearLayout.LayoutParams.WRAP_CONTENT, 1f)
            addView(TextView(this@RoleSelectionActivity).apply {
                text = "Protected Parent (Senior)"
                textSize = 18f
                typeface = Typeface.DEFAULT_BOLD
                setTextColor(KavachTheme.DARK_TEXT)
            })
            addView(TextView(this@RoleSelectionActivity).apply {
                text = "Calm sanctuary. Incoming scam SMS & calls are silenced automatically. Zero developer jargon. 1-tap safety check."
                textSize = 13f
                setTextColor(KavachTheme.DARK_MUTED)
                setLineSpacing(2f, 1.15f)
                setPadding(0, KavachTheme.dp(this@RoleSelectionActivity, 4f), 0, 0)
            })
        }
        seniorRow.addView(seniorIcon)
        seniorRow.addView(seniorTextCol)
        seniorCard.addView(seniorRow)
        root.addView(seniorCard, cardLp)

        // Role 2: Family Guardian / Adult Child
        val guardianCard = KavachTheme.card(this, isDark = true, radiusDp = 18f, paddingDp = 22).apply {
            isClickable = true
            isFocusable = true
            background = KavachTheme.rounded(this@RoleSelectionActivity, KavachTheme.DARK_SURFACE, 18f, KavachTheme.EMERALD_PRO, 1.5f)
            setOnClickListener {
                store.putString("app_role", "guardian")
                startActivity(Intent(this@RoleSelectionActivity, FamilyActivity::class.java))
                finish()
            }
        }
        val guardianRow = LinearLayout(this).apply {
            orientation = LinearLayout.HORIZONTAL
            gravity = Gravity.CENTER_VERTICAL
        }
        val guardianIcon = TextView(this).apply {
            text = "🛡️"
            textSize = 32f
            setPadding(0, 0, KavachTheme.dp(this@RoleSelectionActivity, 16f), 0)
        }
        val guardianTextCol = LinearLayout(this).apply {
            orientation = LinearLayout.VERTICAL
            layoutParams = LinearLayout.LayoutParams(0, LinearLayout.LayoutParams.WRAP_CONTENT, 1f)
            addView(TextView(this@RoleSelectionActivity).apply {
                text = "Family Guardian (Adult Child)"
                textSize = 18f
                typeface = Typeface.DEFAULT_BOLD
                setTextColor(KavachTheme.DARK_TEXT)
            })
            addView(TextView(this@RoleSelectionActivity).apply {
                text = "Command center. Linked via E2E encryption to parents' devices. Real-time quarantined threat alerts, remote defense, and RevenueCat multi-seat shield."
                textSize = 13f
                setTextColor(KavachTheme.DARK_MUTED)
                setLineSpacing(2f, 1.15f)
                setPadding(0, KavachTheme.dp(this@RoleSelectionActivity, 4f), 0, 0)
            })
        }
        guardianRow.addView(guardianIcon)
        guardianRow.addView(guardianTextCol)
        guardianCard.addView(guardianRow)
        root.addView(guardianCard, cardLp)

        val footnote = TextView(this).apply {
            text = "🔒 Zero-Knowledge Architecture: Neither role ever uploads private call audio or personal messages to the cloud."
            textSize = 12f
            setTextColor(Color.parseColor("#64748B"))
            gravity = Gravity.CENTER
            setPadding(0, KavachTheme.dp(this@RoleSelectionActivity, 16f), 0, 0)
        }
        root.addView(footnote)

        setContentView(scroll)
    }
}
