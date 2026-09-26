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
        // Enable debug logging for testing and configure RevenueCat SDK
        Purchases.logLevel = LogLevel.DEBUG
        Purchases.configure(
            PurchasesConfiguration.Builder(this, BuildConfig.REVENUECAT_KEY).build()
        )
    }
}
