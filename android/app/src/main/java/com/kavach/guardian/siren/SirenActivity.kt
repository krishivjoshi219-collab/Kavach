package com.kavach.guardian.siren

import android.app.KeyguardManager
import android.content.Context
import android.content.Intent
import android.graphics.Color
import android.media.AudioAttributes
import android.media.Ringtone
import android.media.RingtoneManager
import android.net.Uri
import android.os.Build
import android.os.Bundle
import android.os.Handler
import android.os.Looper
import android.os.VibrationEffect
import android.os.Vibrator
import android.os.VibratorManager
import android.view.Gravity
import android.view.WindowManager
import android.widget.Button
import android.widget.LinearLayout
import android.widget.TextView
import androidx.appcompat.app.AppCompatActivity

class SirenActivity : AppCompatActivity() {

    private var ringtone: Ringtone? = null
    private var vibrator: Vibrator? = null
    private var detailView: TextView? = null
    private val sirenLoop = Handler(Looper.getMainLooper())
    private val reblare = object : Runnable {
        override fun run() {
            try {
                if (ringtone?.isPlaying != true) ringtone?.play()
            } catch (_: Exception) {}
            sirenLoop.postDelayed(this, 4000)
        }
    }

    override fun onCreate(savedInstanceState: Bundle?) {
        super.onCreate(savedInstanceState)

        // Wake screen and show on lockscreen
        if (Build.VERSION.SDK_INT >= Build.VERSION_CODES.O_MR1) {
            setShowWhenLocked(true)
            setTurnScreenOn(true)
            val keyguardManager = getSystemService(Context.KEYGUARD_SERVICE) as? KeyguardManager
            keyguardManager?.requestDismissKeyguard(this, null)
        } else {
            @Suppress("DEPRECATION")
            window.addFlags(
                WindowManager.LayoutParams.FLAG_SHOW_WHEN_LOCKED or
                WindowManager.LayoutParams.FLAG_TURN_SCREEN_ON or
                WindowManager.LayoutParams.FLAG_KEEP_SCREEN_ON
            )
        }

        val reason = intent.getStringExtra("reason") ?: "POTENTIAL SCAM DETECTED"

        startSiren()

        // Build accessible, high-contrast emergency UI
        val root = LinearLayout(this).apply {
            orientation = LinearLayout.VERTICAL
            setBackgroundColor(Color.parseColor("#8A0000")) // Urgent red
            gravity = Gravity.CENTER
            setPadding(48, 64, 48, 64)
        }

        val titleView = TextView(this).apply {
            text = "⚠️ SCAM ALERT ⚠️"
            textSize = 32f
            setTextColor(Color.WHITE)
            gravity = Gravity.CENTER
            typeface = android.graphics.Typeface.DEFAULT_BOLD
        }
        root.addView(titleView)

        val warningView = TextView(this).apply {
            text = "RUKO! HANG UP NOW!\nOTP, PIN, paise — kuch mat do."
            textSize = 25f
            setTextColor(Color.parseColor("#FFFF00")) // High-contrast yellow
            gravity = Gravity.CENTER
            setPadding(0, 32, 0, 32)
        }
        root.addView(warningView)

        val detailView = TextView(this).apply {
            text = reason
            textSize = 16f
            setTextColor(Color.WHITE)
            gravity = Gravity.CENTER
            setPadding(0, 0, 0, 48)
        }
        this.detailView = detailView
        root.addView(detailView)

        val callFamilyBtn = Button(this).apply {
            text = "📞 Call Family Manager"
            textSize = 18f
            setBackgroundColor(Color.WHITE)
            setTextColor(Color.BLACK)
            setOnClickListener {
                stopSiren()
                val callIntent = Intent(Intent.ACTION_DIAL)
                startActivity(callIntent)
            }
        }
        val lpBtn = LinearLayout.LayoutParams(
            LinearLayout.LayoutParams.MATCH_PARENT,
            LinearLayout.LayoutParams.WRAP_CONTENT
        ).apply { setMargins(0, 16, 0, 16) }
        root.addView(callFamilyBtn, lpBtn)

        val dismissBtn = Button(this).apply {
            text = "🛡️ I Am Safe / Stop Siren"
            textSize = 18f
            setBackgroundColor(Color.parseColor("#333333"))
            setTextColor(Color.WHITE)
            setOnClickListener {
                stopSiren()
                finish()
            }
        }
        root.addView(dismissBtn, lpBtn)

        setContentView(root)
    }

    override fun onNewIntent(intent: Intent) {
        super.onNewIntent(intent)
        // singleTask reuse (Scam Lab back-to-back runs): refresh the reason
        // and restart the alarm instead of showing a stale first-run screen.
        setIntent(intent)
        detailView?.text = intent.getStringExtra("reason") ?: "POTENTIAL SCAM DETECTED"
        stopSiren()
        startSiren()
    }

    private fun startSiren() {
        try {
            val alertUri: Uri = RingtoneManager.getDefaultUri(RingtoneManager.TYPE_ALARM)
                ?: RingtoneManager.getDefaultUri(RingtoneManager.TYPE_NOTIFICATION)
            ringtone = RingtoneManager.getRingtone(applicationContext, alertUri)?.apply {
                audioAttributes = AudioAttributes.Builder()
                    .setUsage(AudioAttributes.USAGE_ALARM)
                    .setContentType(AudioAttributes.CONTENT_TYPE_SONIFICATION)
                    .build()
                play()
            }
            // Ringtone.play() is one-shot: re-blare every 4s until dismissed,
            // or the "siren" dies after a single chime mid-demo.
            sirenLoop.removeCallbacks(reblare)
            sirenLoop.postDelayed(reblare, 4000)
        } catch (_: Exception) {}

        try {
            vibrator = if (Build.VERSION.SDK_INT >= Build.VERSION_CODES.S) {
                val vm = getSystemService(Context.VIBRATOR_MANAGER_SERVICE) as VibratorManager
                vm.defaultVibrator
            } else {
                @Suppress("DEPRECATION")
                getSystemService(Context.VIBRATOR_SERVICE) as Vibrator
            }

            val pattern = longArrayOf(0, 500, 200, 500, 200, 500)
            if (Build.VERSION.SDK_INT >= Build.VERSION_CODES.O) {
                vibrator?.vibrate(VibrationEffect.createWaveform(pattern, 0))
            } else {
                @Suppress("DEPRECATION")
                vibrator?.vibrate(pattern, 0)
            }
        } catch (_: Exception) {}
    }

    private fun stopSiren() {
        sirenLoop.removeCallbacks(reblare)
        try {
            ringtone?.stop()
        } catch (_: Exception) {}
        ringtone = null
        try {
            vibrator?.cancel()
        } catch (_: Exception) {}
        vibrator = null
    }

    override fun onDestroy() {
        stopSiren()
        super.onDestroy()
    }
}
