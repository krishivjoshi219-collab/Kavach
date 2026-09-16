package com.kavach.guardian

import android.app.Application
import com.google.crypto.tink.hybrid.HybridConfig
import com.kavach.guardian.data.LocalStore
import com.revenuecat.purchases.Purchases
import com.revenuecat.purchases.PurchasesConfiguration

class KavachApp : Application() {
    lateinit var store: LocalStore
        private set

    override fun onCreate() {
        super.onCreate()
        HybridConfig.register()
        store = LocalStore(this)
        // RevenueCat test mode for the hackathon; production key via BuildConfig flavors.
        if (BuildConfig.REVENUECAT_KEY != "test_REPLACE_ME") {
            Purchases.configure(PurchasesConfiguration.Builder(this, BuildConfig.REVENUECAT_KEY).build())
        }
    }
}
