plugins {
    id("com.android.application")
    id("org.jetbrains.kotlin.android")
}

android {
    namespace = "com.kavach.guardian"
    compileSdk = 34

    defaultConfig {
        applicationId = "com.kavach.guardian"
        minSdk = 29
        targetSdk = 34
        versionCode = 1
        versionName = "0.1.0"
        // RevenueCat public SDK key (injected via GitHub Secrets or environment variable).
        val revenueCatKey = System.getenv("REVENUECAT_KEY")
            ?.takeIf { it.isNotBlank() }
            ?: (project.findProperty("REVENUECAT_KEY") as? String)?.takeIf { it.isNotBlank() }
            ?: "test_REPLACE_ME"
        buildConfigField("String", "REVENUECAT_KEY", "\"$revenueCatKey\"")
        buildConfigField("String", "KAVACH_API", "\"https://kavach-19v6.onrender.com\"")
        // Role preset: dual (chooser) by default; flavors override.
        buildConfigField("String", "APP_ROLE", "\"dual\"")
    }

    // Next Gen demo clarity: two installable APKs from one codebase.
    // senior  → com.kavach.guardian.senior  (Kavach Senior, boots to sanctuary)
    // manager → com.kavach.guardian.manager (Kavach Family, boots to war-room)
    flavorDimensions += "role"
    productFlavors {
        create("senior") {
            dimension = "role"
            applicationIdSuffix = ".senior"
            versionNameSuffix = "-senior"
            buildConfigField("String", "APP_ROLE", "\"senior\"")
            resValue("string", "app_name", "Kavach Senior")
        }
        create("manager") {
            dimension = "role"
            applicationIdSuffix = ".manager"
            versionNameSuffix = "-manager"
            buildConfigField("String", "APP_ROLE", "\"guardian\"")
            resValue("string", "app_name", "Kavach Family")
        }
    }

    buildTypes {
        release {
            isMinifyEnabled = false
        }
    }
    compileOptions {
        sourceCompatibility = JavaVersion.VERSION_17
        targetCompatibility = JavaVersion.VERSION_17
    }
    kotlinOptions {
        jvmTarget = "17"
    }
    buildFeatures {
        buildConfig = true
    }
}

dependencies {
    implementation("androidx.core:core-ktx:1.13.1")
    implementation("androidx.appcompat:appcompat:1.7.0")
    implementation("androidx.activity:activity-ktx:1.9.2")
    implementation("androidx.lifecycle:lifecycle-runtime-ktx:2.8.6")
    // World-class audited crypto (ECIES hybrid). Never home-rolled.
    implementation("com.google.crypto.tink:tink-android:1.23.0")
    // Pairing QR codes.
    implementation("com.journeyapps:zxing-android-embedded:4.3.0")
    // Monetization (RevenueCat SDK v10.23.2)
    implementation("com.revenuecat.purchases:purchases:10.23.2")
    implementation("com.revenuecat.purchases:purchases-ui:10.23.2")

    // Unit tests
    testImplementation("junit:junit:4.13.2")
}

