package com.kavach.guardian

import android.app.Application
import com.google.crypto.tink.hybrid.HybridConfig
import com.kavach.guardian.data.LocalStore
import com.revenuecat.purchases.LogLevel
import com.revenuecat.purchases.Purchases
import com.revenuecat.purchases.PurchasesConfiguration

class KavachApp : Application() {
    lateinit var store: LocalStore
        private set

    override fun onCreate() {
        super.onCreate()
        HybridConfig.register()
        store = LocalStore(this)
        // RevenueCat: configure only with a real public SDK key. In TEST MODE
        // (no key injected) skip configure so the app never crash-loops at
        // cold start; PaywallActivity already gates on Purchases.isConfigured.
        Purchases.logLevel = if (BuildConfig.DEBUG) LogLevel.DEBUG else LogLevel.WARN
        val key = BuildConfig.REVENUECAT_KEY
        if (key.isNotBlank() && key != "test_REPLACE_ME") {
            try {
                Purchases.configure(
                    PurchasesConfiguration.Builder(this, key).build()
                )
            } catch (_: Exception) {
                // Stay in TEST MODE: backend promo + sandbox reconcile path.
            }
        }
    }
}
