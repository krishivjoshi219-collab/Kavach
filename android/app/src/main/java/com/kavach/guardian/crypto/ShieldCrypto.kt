package com.kavach.guardian.crypto

import android.content.Context
import android.util.Base64
import com.google.crypto.tink.CleartextKeysetHandle
import com.google.crypto.tink.HybridDecrypt
import com.google.crypto.tink.HybridEncrypt
import com.google.crypto.tink.JsonKeysetReader
import com.google.crypto.tink.JsonKeysetWriter
import com.google.crypto.tink.KeysetHandle
import com.google.crypto.tink.hybrid.HybridKeyTemplates
import com.google.crypto.tink.integration.android.AndroidKeysetManager
import com.google.crypto.tink.integration.android.AndroidKeystore
import java.io.ByteArrayOutputStream

/**
 * World-class, never home-rolled: Google Tink ECIES hybrid encryption.
 * Each side holds its own private keyset (Android Keystore-backed master key);
 * only PUBLIC keysets travel inside QR codes. The server never sees either.
 */
class ShieldCrypto(context: Context, private val tag: String) {

    private val appCtx = context.applicationContext
    private val prefs = appCtx.getSharedPreferences("kavach_crypto_$tag", Context.MODE_PRIVATE)

    private fun masterKeyUri(): String {
        var uri = prefs.getString("master_uri", null)
        if (uri == null) {
            uri = "android-keystore://kavach_master_$tag"
            AndroidKeystore.generateNewAes256GcmKey(uri)
            prefs.edit().putString("master_uri", uri).apply()
        }
        return uri
    }

    private fun manager(): AndroidKeysetManager {
        return AndroidKeysetManager.Builder()
            .withSharedPref(appCtx, "kavach_keyset_$tag", "kavach_pref_$tag")
            .withKeyTemplate(HybridKeyTemplates.ECIES_P256_HKDF_HMAC_SHA256_AES128_GCM)
            .withMasterKeyUri(masterKeyUri())
            .build()
    }

    private fun privateHandle(): KeysetHandle = manager().keysetHandle

    /** Public keyset bytes (safe to embed in QR codes). */
    fun publicKeyBytes(): ByteArray {
        val pub = privateHandle().publicKeysetHandle
        val out = ByteArrayOutputStream()
        CleartextKeysetHandle.write(pub, JsonKeysetWriter.withOutputStream(out))
        return out.toByteArray()
    }

    fun encryptForTheirKey(theirPublicKey: ByteArray, plaintext: ByteArray): ByteArray {
        val pub = CleartextKeysetHandle.read(JsonKeysetReader.withBytes(theirPublicKey))
        val enc: HybridEncrypt = pub.getPrimitive(HybridEncrypt::class.java)
        return enc.encrypt(plaintext, CONTEXT_INFO)
    }

    fun decrypt(ciphertext: ByteArray): ByteArray {
        val dec: HybridDecrypt = privateHandle().getPrimitive(HybridDecrypt::class.java)
        return dec.decrypt(ciphertext, CONTEXT_INFO)
    }

    companion object {
        private val CONTEXT_INFO = "kavach-v1".toByteArray()
        fun b64e(bytes: ByteArray): String = Base64.encodeToString(bytes, Base64.NO_WRAP)
        fun b64d(s: String): ByteArray = Base64.decode(s, Base64.NO_WRAP)
    }
}
