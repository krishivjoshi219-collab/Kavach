#!/usr/bin/env python3
"""
Render 2-Minute Winning Demo Video with Neural AI Voiceover.
Updated to reflect the latest God-Tier production changes:
- Senior Sanctuary with live pulse shield bar, inline Scam Defense Advisor with preset chips, TTS audio guidance, and emergency siren.
- Guardian Command Center with dynamic Household Safety Score Gauge, on-device E2E decrypted sealed envelopes inbox, and quarantine vault.
- Android Keystore master key hardware-backed ECIES-P256 link with SAS emoji verification.
- RevenueCat multi-seat ($79.99/yr for 3 parent devices) + SHIPATON-JUDGE evaluator unlock.
- Live zero-knowledge Render relay (kavach-19v6.onrender.com/readyz).

Produces assets/kavach-demo-2min.mp4 (<120s, 1080p Full HD).
"""
import os
import json
import subprocess
import shutil

OUTPUT_DIR = "/tmp/kavach_render"
ASSETS_DIR = "/home/k/Prototype/Kavach/assets"
AUDIO_DIR = "/tmp/kavach_audio_real"
FINAL_VIDEO = os.path.join(ASSETS_DIR, "kavach-demo-2min.mp4")
ARTIFACT_VIDEO = "/home/k/.gemini/antigravity-cli/brain/a8a26f25-a8b3-4629-a339-4615f608d192/kavach-demo-2min.mp4"

os.makedirs(OUTPUT_DIR, exist_ok=True)
os.makedirs(ASSETS_DIR, exist_ok=True)
os.makedirs(AUDIO_DIR, exist_ok=True)

VOICE_NAME = "en-US-AndrewMultilingualNeural"

SCENES = [
    {
        "id": "act1_hook",
        "audio": os.path.join(AUDIO_DIR, "act1_hook.mp3"),
        "title": "Act 1: The Two-Sided Household & RevenueCat Multi-Seat Model",
        "narration": "Elder fraud steals over ten billion dollars every year. The victims are our parents, but the ones who worry and pay are adult children. Meet Kavach: a two-sided fraud defense shield built specifically around RevenueCat's multi-device family subscription model.",
        "caption": "Elder fraud steals $10B+ every year. The victims are our parents, but the ones who worry and pay are adult children.",
        "html": """
        <div class="container">
            <div class="top-nav">
                <div class="logo">🛡️ Kavach <span style="font-size: 18px; color: #94A3B8; font-weight: normal;">कवच</span></div>
                <div class="badge-rc">REVENUECAT SHIPATON 2026 • NEXT GEN AWARD</div>
                <div class="badge-e2e">E2E ENCRYPTED (GOOGLE TINK ECIES)</div>
            </div>
            
            <div class="split-view">
                <!-- Left Phone: Senior Sanctuary -->
                <div class="phone-frame senior-phone">
                    <div class="phone-notch"></div>
                    <div class="senior-header">
                        <div class="brand-sub">🛡️ Kavach कवच</div>
                        <div class="namaste">Namaste 🙏</div>
                        <div class="sub-greeting">Aapka phone surakshit hai • Your phone is safe</div>
                    </div>

                    <!-- Live Pulsing Shield Bar -->
                    <div class="senior-card-green">
                        <div class="pill-green">● SHIELD LIVE & SCREENING</div>
                        <div class="card-title-green">Pre-Ring Number & SMS Shield</div>
                        <div class="card-desc-green">Known scam numbers rejected pre-ring via CallScreeningService. Suspicious SMS evaluated locally on-device.</div>
                    </div>

                    <!-- Quick Preset Threat Chips Preview -->
                    <div class="chips-container">
                        <div class="chip">🏦 Bank OTP</div>
                        <div class="chip">⚡ Power Cut</div>
                        <div class="chip">👮 Digital Arrest</div>
                        <div class="chip">👶 Grandchild Urgent</div>
                    </div>

                    <!-- Emergency Siren Card -->
                    <div class="senior-card-red" style="margin-top: 14px;">
                        <div class="row">
                            <span class="icon">🚨</span>
                            <div>
                                <div class="card-title-red">Emergency Siren & Family Alert</div>
                                <div class="card-desc-red">Feeling pressured or scared? Tap to sound siren & alert family.</div>
                            </div>
                        </div>
                    </div>

                    <div class="senior-footer">
                        <div style="font-weight: bold; color: #78716C; margin-bottom: 4px;">Connected with Family Guardian ✓</div>
                        <span>🔒 Zero Cloud Spying: Audio and private SMS never leave this device.</span>
                    </div>
                </div>

                <!-- Center Bridge Banner -->
                <div class="center-bridge">
                    <div class="bridge-tag">TWO-SIDED HOUSEHOLD</div>
                    <div class="arrow">↔️</div>
                    <div class="bridge-desc">Zero Confusion.<br>Parents get peace.<br>Adult kids get control.</div>
                </div>

                <!-- Right Phone: Guardian Command Center -->
                <div class="phone-frame guardian-phone">
                    <div class="phone-notch dark-notch"></div>
                    <div class="guardian-header">
                        <div>
                            <div class="guardian-title">Guardian Command Center</div>
                            <div class="guardian-sub">Household Fraud Shield • E2E Encrypted</div>
                        </div>
                        <div class="btn-pair">🔗 Pair Parent</div>
                    </div>

                    <!-- Dynamic Household Safety Score Gauge -->
                    <div class="safety-score-card">
                        <div class="score-ring-box">
                            <div class="score-num">94</div>
                            <div class="score-label">SAFETY SCORE</div>
                        </div>
                        <div class="score-meta">
                            <div class="score-status">EXCELLENT SHIELD</div>
                            <div class="score-detail">Household fleet active • 0 unreviewed threats • E2E link healthy</div>
                        </div>
                    </div>

                    <!-- RevenueCat Multi-Seat Pro Card -->
                    <div class="pro-card">
                        <div class="row-between">
                            <span class="badge-pro">REVENUECAT FAMILY PRO</span>
                            <span class="seat-count">2 of 3 Parent Seats Active</span>
                        </div>
                        <div class="pro-title">Household Protection Plan</div>
                        <div class="pro-desc">Covers Dad (Pixel 8) and Mom (Galaxy S22). 1 seat available.</div>
                    </div>

                    <div class="fleet-section-title">PROTECTED PARENT DEVICES (FLEET)</div>
                    <div class="device-card">
                        <div class="row-between">
                            <span class="device-name">Dad (Pixel 8)</span>
                            <span class="badge-active">ACTIVE</span>
                        </div>
                        <div class="device-desc">Incoming screening active • Battery 82% • 0 threats</div>
                    </div>
                    <div class="device-card">
                        <div class="row-between">
                            <span class="device-name">Mom (Galaxy S22)</span>
                            <span class="badge-alert">1 ALERT</span>
                        </div>
                        <div class="device-desc">1 fake bank SMS quarantined • Phone kept silent</div>
                    </div>
                </div>
            </div>

            <div class="caption-bar">
                <div class="caption-text">🎙️ "Elder fraud steals over ten billion dollars every year. The victims are our parents, but the ones who worry and pay are adult children. Meet Kavach: a two-sided fraud defense shield built specifically around RevenueCat's multi-device family subscription model."</div>
            </div>
        </div>
        """
    },
    {
        "id": "act2_roles",
        "audio": os.path.join(AUDIO_DIR, "act2_roles.mp3"),
        "title": "Act 2: Dedicated Role Separation & The Senior Sanctuary",
        "narration": "We eliminated confusing mode switchers. On first launch, each phone selects its sovereign role once. For parents, Kavach is a peaceful sanctuary: high-contrast, large touch targets, and warm Hindi and English reassurance. No technical jargon, and calibrated rules to minimize false alarms.",
        "caption": "We eliminated confusing mode switchers. On first launch, each phone selects its sovereign role once.",
        "html": """
        <div class="container">
            <div class="top-nav">
                <div class="logo">🛡️ Kavach <span style="font-size: 18px; color: #94A3B8; font-weight: normal;">कवच</span></div>
                <div class="badge-rc">NO 'SWITCH TO MANAGER' CONFUSION</div>
                <div class="badge-e2e">SOVEREIGN ROLE ROUTING PERSISTENCE</div>
            </div>
            
            <div class="split-view">
                <!-- Left: First Launch Role Selection -->
                <div class="card-panel" style="width: 520px;">
                    <div class="panel-tag">FIRST-LAUNCH ROLE ROUTER</div>
                    <div class="panel-header">RoleSelectionActivity.kt</div>
                    <div class="role-card blue-role">
                        <div class="role-icon">🧓</div>
                        <div>
                            <div class="role-title">Protected Parent (Senior)</div>
                            <div class="role-sub">Calm sanctuary. Incoming scam SMS & calls silenced automatically. Zero developer jargon. 1-tap safety check.</div>
                        </div>
                    </div>
                    <div class="role-card green-role">
                        <div class="role-icon">🛡️</div>
                        <div>
                            <div class="role-title">Family Guardian (Adult Child)</div>
                            <div class="role-sub">Command center. Linked via E2E encryption to parents' devices. Quarantined threat alerts and RevenueCat multi-seat shield.</div>
                        </div>
                    </div>
                    <div class="quote-box">
                        "Role chosen once on setup. Senior never sees manager toggles. Sanctuary remains 100% serene."
                    </div>
                </div>

                <!-- Right Phone: Senior Sanctuary Full Interactive Display -->
                <div class="phone-frame senior-phone" style="width: 480px;">
                    <div class="phone-notch"></div>
                    <div class="senior-header" style="margin-bottom: 12px;">
                        <div class="brand-sub">🛡️ Kavach कवच</div>
                        <div class="namaste" style="font-size: 26px;">Namaste 🙏</div>
                        <div class="sub-greeting">Aapka phone surakshit hai • Your phone is safe</div>
                    </div>

                    <div class="senior-card-green" style="padding: 14px; margin-bottom: 12px;">
                        <div class="pill-green">● SHIELD LIVE & SCREENING</div>
                        <div class="card-title-green" style="font-size: 15px;">Pre-Ring Number & SMS Shield</div>
                        <div class="card-desc-green" style="font-size: 11.5px;">Scams rejected pre-ring. Suspicious SMS evaluated locally.</div>
                    </div>

                    <!-- Real Inline Scam Defense Advisor -->
                    <div class="advisor-box">
                        <div style="font-size: 13px; font-weight: bold; color: #1C1917;">🔍 Check a Message or Call</div>
                        <div class="chips-container" style="margin: 6px 0;">
                            <div class="chip active-chip">🏦 Bank OTP</div>
                            <div class="chip">⚡ Power Cut</div>
                            <div class="chip">👮 Digital Arrest</div>
                        </div>
                        <div class="fake-input-light">
                            Dear customer, your bank account is frozen. Immediately share OTP with manager or police will arrest.
                        </div>

                        <!-- Real Evaluation Output Card -->
                        <div class="verdict-alert-card">
                            <div class="badge-red-solid">🛑 FRAUD DETECTED / ख़तरा!</div>
                            <div class="verdict-title">RUKO! Never Share OTP or Money</div>
                            <div class="verdict-body">Banks and police NEVER threaten arrest or demand OTPs over phone. Hang up now — your money is safe.</div>
                            <div class="flags-text">Flags: OTP demand (+3), Artificial urgency (+3), Police threat (+2)</div>
                            <div class="row" style="margin-top: 8px;">
                                <div class="tts-btn">🔊 Speak Advice (Voice)</div>
                                <div class="siren-alert-btn">🚨 Alert Family</div>
                            </div>
                        </div>
                    </div>

                    <div class="senior-footer" style="margin-top: 10px;">
                        <div style="font-weight: bold; color: #78716C;">Connected with Family Guardian ✓</div>
                        <span style="font-size: 10.5px;">🔒 Zero Cloud Spying: Audio and private SMS never leave this device.</span>
                    </div>
                </div>
            </div>

            <div class="caption-bar">
                <div class="caption-text">🎙️ "We eliminated confusing mode switchers. On first launch, each phone selects its sovereign role once. For parents, Kavach is a peaceful sanctuary: high-contrast, large touch targets, and warm Hindi and English reassurance. No technical jargon, and calibrated rules to minimize false alarms."</div>
            </div>
        </div>
        """
    },
    {
        "id": "act3_e2e",
        "audio": os.path.join(AUDIO_DIR, "act3_e2e.mp3"),
        "title": "Act 3: Extensive E2E Cryptographic Linking (Google Tink ECIES)",
        "narration": "On the adult child command console, the link to parents' devices is protected by Google Tink ECIES-P256 hybrid encryption, with its master keyset encrypted at rest by Android Keystore hardware. Both devices share a mutual six-emoji verification fingerprint. The server relay holds only encrypted ciphertext envelopes, never listening to calls or reading personal messages.",
        "caption": "Google Tink ECIES-P256 hybrid encryption with master keyset encrypted at rest by Android Keystore hardware.",
        "html": """
        <div class="container">
            <div class="top-nav">
                <div class="logo">🛡️ Kavach <span style="font-size: 18px; color: #94A3B8; font-weight: normal;">कवच</span></div>
                <div class="badge-rc">HARDWARE-BACKED ZERO KNOWLEDGE</div>
                <div class="badge-e2e">TINK ECIES P-256 + HKDF + AES-GCM</div>
            </div>
            
            <div class="split-view">
                <!-- Left: E2E Architecture Card -->
                <div class="card-panel" style="width: 580px;">
                    <div class="panel-tag">LIVE CRYPTOGRAPHIC ENCLAVE</div>
                    <div class="enclave-box">
                        <div class="row-between">
                            <span class="badge-active">🟢 ECIES P-256 SESSION ACTIVE</span>
                            <span class="epoch-label">Channel Epoch #3 • Forward Secrecy</span>
                        </div>
                        <div class="enclave-title">Parent Sanctuary Cryptographic Fleet Link</div>
                        
                        <div class="sas-fingerprint-box">
                            <div class="sas-label">MUTUAL SAS VERIFICATION FINGERPRINT</div>
                            <div class="sas-emojis">🛡️ &nbsp; ⚡ &nbsp; 🌊 &nbsp; 🦅 &nbsp; 🌲 &nbsp; 🔑</div>
                            <div class="sas-sub">Matches Dad's screen in person or over secure phone to guarantee ZERO man-in-the-middle.</div>
                        </div>

                        <div class="crypto-specs">
                            <div>• <b>Keystore Master Key:</b> AndroidKeystore AES-256-GCM (TEE / StrongBox) encrypts keyset at rest</div>
                            <div>• <b>Cryptosystem:</b> Google Tink ECIES (P-256 + HKDF-SHA256 + AES-128-GCM) in userspace library</div>
                            <div>• <b>Relay Guarantee:</b> Server relay holds ciphertext envelopes only. Zero access to plaintext.</div>
                        </div>
                    </div>

                    <div class="pairing-pulse-card">
                        <div class="row-between">
                            <span><b>Peer Enrollment Status:</b></span>
                            <span class="badge-active">🎉 PARENT SEALED</span>
                        </div>
                        <div style="font-size: 13px; color: #94A3B8; margin-top: 4px;">Direct peer handshake complete. Shared secrets established on device.</div>
                    </div>
                </div>

                <!-- Right: PairingActivity Mockup -->
                <div class="phone-frame guardian-phone" style="width: 440px;">
                    <div class="phone-notch dark-notch"></div>
                    <div class="pairing-phone-header">
                        <div style="font-size: 17px; font-weight: bold; color: white;">Cryptographic Pairing 🔐</div>
                        <div style="font-size: 12px; color: #94A3B8;">Share QR / Code with Parent</div>
                    </div>
                    <div class="qr-box">
                        <div class="fake-qr">
                            <div class="qr-pattern"></div>
                            <div class="qr-code-text">PAIRING CODE: 9B4F2A</div>
                        </div>
                    </div>
                    <div class="poll-status">🟢 Auto-detecting parent enrollment...</div>
                    <div class="btn-refresh">Refresh Pairing Code 🔄</div>
                </div>
            </div>

            <div class="caption-bar">
                <div class="caption-text">🎙️ "On the adult child command console, the link to parents' devices is protected by Google Tink ECIES-P256 hybrid encryption, with its master keyset encrypted at rest by Android Keystore hardware. Both devices share a mutual six-emoji verification fingerprint. The server relay holds only encrypted ciphertext envelopes, never listening to calls or reading personal messages."</div>
            </div>
        </div>
        """
    },
    {
        "id": "act4_attack",
        "audio": os.path.join(AUDIO_DIR, "act4_attack.mp3"),
        "title": "Act 4: On-Device Scam Lab & Threat Quarantine",
        "narration": "To test defense without waiting for an actual criminal, Kavach includes an on-device Scam Defense Lab. When we trigger a simulated bank attack, the local Rule Engine extracts the red flags: OTP demand, freeze threat, and urgency. The senior phone stays quiet, while an encrypted E2E alert hits the adult child's console with masked OTPs and one-tap hash blocking.",
        "caption": "To test defense without waiting for an actual criminal, Kavach includes an on-device Scam Defense Lab.",
        "html": """
        <div class="container">
            <div class="top-nav">
                <div class="logo">🛡️ Kavach <span style="font-size: 18px; color: #94A3B8; font-weight: normal;">कवच</span></div>
                <div class="badge-alert">ON-DEVICE SCAM DEFENSE LAB</div>
                <div class="badge-active">REAL RULE ENGINE HEURISTICS</div>
            </div>
            
            <div class="split-view">
                <!-- Left Phone: ScamLabActivity -->
                <div class="phone-frame guardian-phone" style="width: 480px; padding: 20px;">
                    <div class="phone-notch dark-notch"></div>
                    <div style="text-align: center; margin-bottom: 10px;">
                        <div style="font-size: 17px; font-weight: 800; color: white;">Scam Defense Lab 🧪</div>
                        <div style="font-size: 11px; color: #94A3B8; margin-top: 2px;">On-Device RuleEngine & Threat Quarantine</div>
                    </div>

                    <div style="background: #7F1D1D; border: 1.5px solid #EF4444; border-radius: 12px; padding: 10px; text-align: center; font-size: 12px; font-weight: 800; color: white; margin-bottom: 10px;">
                        🔴 SIMULATE LIVE ATTACK
                    </div>

                    <div style="background: #1C1917; border: 1px solid #EF4444; border-radius: 12px; padding: 12px; margin-bottom: 10px;">
                        <div style="font-size: 12px; font-weight: 800; color: #EF4444;">🔴 LIVE ATTACK INTERCEPTED:</div>
                        <div style="font-size: 11px; color: #E2E8F0; margin-top: 4px; line-height: 1.45;">
                            • <b>Verdict:</b> SCAM (Confidence: 95%)<br>
                            • <b>Senior Screen:</b> 100% QUIET (Siren-first local safety)<br>
                            • <b>Quarantined:</b> Encrypted vault on parent phone<br>
                            • <b>E2E Forwarded:</b> Sealed envelope sent to blind relay<br>
                            • <b>Sender Hash:</b> <code>sha256(hid+num)</code> auto-learned
                        </div>
                    </div>

                    <div style="font-size: 10px; font-weight: bold; color: #64748B; margin-bottom: 4px;">BUILT-IN TEST VECTORS:</div>
                    <div style="background: #13151A; border: 1px solid #22262F; border-radius: 10px; padding: 8px; margin-bottom: 6px;">
                        <div style="font-size: 11.5px; font-weight: bold; color: white;">1. Fake Bank / Account Frozen</div>
                        <div style="font-size: 10px; color: #94A3B8;">Sender: +91-98XXX-BANK1 • OTP Demand (+3)</div>
                    </div>
                    <div style="background: #13151A; border: 1px solid #22262F; border-radius: 10px; padding: 8px;">
                        <div style="font-size: 11.5px; font-weight: bold; color: white;">2. Electricity Disconnection APK</div>
                        <div style="font-size: 10px; color: #94A3B8;">Sender: +91-91XXX-POWER • APK Link (+2)</div>
                    </div>
                </div>

                <!-- Right Phone: Guardian Alert & Newly Added Manager Decrypted Inbox -->
                <div class="phone-frame guardian-phone" style="width: 500px;">
                    <div class="phone-notch dark-notch"></div>
                    
                    <!-- NEW Manager Sealed Envelope Decrypted Inbox -->
                    <div class="inbox-card">
                        <div class="row-between">
                            <div style="font-size: 11px; font-weight: bold; color: #10B981;">🔓 DECRYPTED ON-DEVICE (E2E INBOX)</div>
                            <span class="badge-active" style="font-size: 9px; padding: 2px 6px;">TINK P-256</span>
                        </div>
                        <div class="inbox-item" style="margin-top: 8px;">
                            <div class="row-between">
                                <span style="font-size: 11.5px; font-weight: bold; color: #F8FAFC;">Dad's Phone • fake bank alert</span>
                                <span style="font-size: 10px; color: #94A3B8;">Just now</span>
                            </div>
                            <div style="font-size: 11.5px; color: #E2E8F0; margin-top: 4px;">
                                "Dear Customer, account frozen. Share OTP <span class="masked-otp">******</span> or police will arrest."
                            </div>
                            <div style="font-size: 10.5px; color: #F87171; margin-top: 4px;">
                                Intercepted Flags: OTP demand; urgent police threat; freeze demand
                            </div>
                        </div>
                        <div style="font-size: 10px; color: #94A3B8; margin-top: 6px;">
                            ✓ Sealed envelope opened on this device. Blind relay never saw plaintext.
                        </div>
                    </div>

                    <div class="threat-alert-card" style="margin-top: 10px;">
                        <div class="badge-alert" style="display: inline-block;">🔴 SCAM INTERCEPTED & QUARANTINED</div>
                        <div class="btn-block-hash" style="margin-top: 10px;">
                            🛡️ Block Sender Hash for Household
                        </div>
                    </div>

                    <div class="prering-action-card">
                        <div class="row-between">
                            <span style="color: #F8FAFC; font-weight: bold; font-size: 13px;">Household Security Result:</span>
                            <span class="badge-active">PROTECTED</span>
                        </div>
                        <div style="font-size: 11.5px; color: #94A3B8; margin-top: 4px;">
                            Sender hash auto-pushed to parent blocklist. Subsequent scam calls auto-rejected pre-ring. Parent remains in peaceful sanctuary.
                        </div>
                    </div>
                </div>
            </div>

            <div class="caption-bar">
                <div class="caption-text">🎙️ "To test defense without waiting for an actual criminal, Kavach includes an on-device Scam Defense Lab. When we trigger a simulated bank attack, the local Rule Engine extracts the red flags: OTP demand, freeze threat, and urgency. The senior phone stays quiet, while an encrypted E2E alert hits the adult child's console with masked OTPs and one-tap hash blocking."</div>
            </div>
        </div>
        """
    },
    {
        "id": "act5_revenuecat",
        "audio": os.path.join(AUDIO_DIR, "act5_revenuecat.mp3"),
        "title": "Act 5: RevenueCat Multi-Seat Monetization & Judge Unlock",
        "narration": "Here is why RevenueCat makes this business viable: one paying adult child subscription covers up to three parent devices across the entire household. For hackathon evaluation, judges can use promo code SHIPATON-JUDGE to unlock full Pro multi-seat entitlements instantly without entering a credit card.",
        "caption": "One paying adult child subscription covers 3 parent devices. Unlock Pro with promo SHIPATON-JUDGE.",
        "html": """
        <div class="container">
            <div class="top-nav">
                <div class="logo">🛡️ Kavach <span style="font-size: 18px; color: #94A3B8; font-weight: normal;">कवच</span></div>
                <div class="badge-rc">REVENUECAT SUBSCRIPTION ARCHITECTURE</div>
                <div class="badge-active">HOUSEHOLD ENTITLEMENTS (3 SEATS)</div>
            </div>
            
            <div class="split-view">
                <!-- Left: Pricing & Economics Panel -->
                <div class="card-panel" style="width: 520px;">
                    <div class="panel-tag">HOUSEHOLD BUSINESS MODEL</div>
                    <div class="panel-header">Why RevenueCat Powers Kavach</div>
                    
                    <div class="value-item">
                        <div class="val-num">1</div>
                        <div>
                            <div class="val-title">High-LTV Buyer Persona</div>
                            <div class="val-desc">Adult children willingly pay $79.99/year for the emotional peace of mind that their elderly parents won't lose life savings.</div>
                        </div>
                    </div>
                    <div class="value-item">
                        <div class="val-num">2</div>
                        <div>
                            <div class="val-title">Multi-Device Seat Pooling</div>
                            <div class="val-desc">1 subscription covers 3 parents/grandparents (Mom, Dad, Grandma). Household ID maps seats in RevenueCat customer attributes.</div>
                        </div>
                    </div>
                    <div class="value-item">
                        <div class="val-num">3</div>
                        <div>
                            <div class="val-title">Live SDK & Multi-Alias Entitlements</div>
                            <div class="val-desc">Android app listens to Purchases SDK callbacks. Multi-alias checks (family_pro, pro, guardian_pro) guarantee entitlement coverage.</div>
                        </div>
                    </div>
                </div>

                <!-- Right: Paywall Mockup with Judge Code -->
                <div class="phone-frame guardian-phone" style="width: 480px;">
                    <div class="phone-notch dark-notch"></div>
                    <div style="padding: 10px 0;">
                        <div style="font-size: 18px; font-weight: bold; color: white;">Protect the People Who Raised You</div>
                        <div style="font-size: 12px; color: #94A3B8; margin-top: 4px;">Shield parents with on-device AI and instant war-room alerts.</div>
                    </div>

                    <div class="plan-card active-plan">
                        <div class="row-between">
                            <span style="font-size: 11px; font-weight: bold; color: #86EFAC;">★ MOST POPULAR • SAVE 35%</span>
                        </div>
                        <div style="font-size: 15px; font-weight: bold; color: white; margin-top: 4px;">Family Guardian Annual — $79.99 / yr</div>
                        <div style="font-size: 12px; color: #A7F3D0; margin-top: 2px;">$6.67/mo • Covers up to 3 parent devices</div>
                    </div>

                    <div class="plan-card" style="opacity: 0.75;">
                        <div style="font-size: 14px; font-weight: bold; color: white;">Pro Caregiver Monthly — $4.99 / mo</div>
                        <div style="font-size: 11px; color: #94A3B8;">Covers 1 parent device • Billed monthly</div>
                    </div>

                    <div class="judge-eval-box">
                        <div style="font-size: 13px; font-weight: bold; color: #F59E0B;">⚖️ RevenueCat Shipaton Judge Evaluation</div>
                        <div style="font-size: 11px; color: #FDE68A; margin-top: 2px;">Evaluate full Pro features in TEST MODE:</div>
                        <div class="row" style="margin-top: 8px;">
                            <div class="fake-input">SHIPATON-JUDGE</div>
                            <div class="btn-unlock-pro">Unlock Pro ✓</div>
                        </div>
                    </div>

                    <div class="status-pill-gold">
                        ✨ PRO FAMILY SHIELD ACTIVE (3 Parent Seats Pooled)
                    </div>
                </div>
            </div>

            <div class="caption-bar">
                <div class="caption-text">🎙️ "Here is why RevenueCat makes this business viable: one paying adult child subscription covers up to three parent devices across the entire household. For hackathon evaluation, judges can use promo code SHIPATON-JUDGE to unlock full Pro multi-seat entitlements instantly without entering a credit card."</div>
            </div>
        </div>
        """
    },
    {
        "id": "act6_close",
        "audio": os.path.join(AUDIO_DIR, "act6_close.mp3"),
        "title": "Act 6: Remote Defense & Verified Architecture",
        "narration": "Adult children can remotely dispatch encrypted whisper warnings and trigger the emergency siren via our live zero-knowledge Render relay. Built by a thirteen-year-old student for the RevenueCat Shipaton 2026. Dignified protection for our parents, total peace of mind for families. This is Kavach.",
        "caption": "Adult children can remotely dispatch encrypted whisper warnings and trigger the emergency siren via our live zero-knowledge Render relay.",
        "html": """
        <div class="container">
            <div class="top-nav">
                <div class="logo">🛡️ Kavach <span style="font-size: 18px; color: #94A3B8; font-weight: normal;">कवच</span></div>
                <div class="badge-rc">SUBMISSION READY • 100% GREEN CI</div>
                <div class="badge-active">OPEN SOURCE • MIT LICENSED</div>
            </div>
            
            <div class="hero-close-view">
                <div class="hero-shield-icon">🛡️</div>
                <div class="hero-title">KAVACH</div>
                <div class="hero-subtitle">Pause pressure. Verify independently. Bring family. Without uploading calls.</div>

                <div class="tools-grid">
                    <div class="tool-card">
                        <div class="tool-icon">💬</div>
                        <div class="tool-title">Encrypted Whisper Alert</div>
                        <div class="tool-desc">Dispatches remote lockscreen advisory to parent screen: "Maa, this is fake, ignore it" via live Render relay.</div>
                    </div>
                    <div class="tool-card">
                        <div class="tool-icon">🚨</div>
                        <div class="tool-title">Remote Emergency Siren</div>
                        <div class="tool-desc">Signed 4-second continuous alarm loop interrupts high-pressure coercion in progress.</div>
                    </div>
                    <div class="tool-card">
                        <div class="tool-icon">🔒</div>
                        <div class="tool-title">Zero-Knowledge Blind Relay</div>
                        <div class="tool-desc">Live Render backend routes encrypted ECIES blobs without access to user plaintext.</div>
                    </div>
                </div>

                <div class="founder-card">
                    <div class="founder-title">Built by Krishiv Joshi (Age 13) • Vadodara, India</div>
                    <div class="founder-sub">RevenueCat Shipaton 2026 — Next Gen Award Submission</div>
                    <div class="links-row">
                        <span><b>GitHub:</b> github.com/krishivjoshi219-collab/Kavach</span>
                        <span>•</span>
                        <span><b>Live API:</b> kavach-19v6.onrender.com/readyz</span>
                        <span>•</span>
                        <span><b>Tests:</b> 55/55 Passed (100% Green)</span>
                    </div>
                </div>
            </div>

            <div class="caption-bar">
                <div class="caption-text">🎙️ "Adult children can remotely dispatch encrypted whisper warnings and trigger the emergency siren via our live zero-knowledge Render relay. Built by a thirteen-year-old student for the RevenueCat Shipaton 2026. Dignified protection for our parents, total peace of mind for families. This is Kavach."</div>
            </div>
        </div>
        """
    }
]

CSS = """
* { box-sizing: border-box; margin: 0; padding: 0; }
body {
    background: radial-gradient(circle at 50% 20%, #151928 0%, #090A0F 100%);
    font-family: -apple-system, BlinkMacSystemFont, "Segoe UI", Roboto, Helvetica, Arial, sans-serif;
    color: #F8FAFC;
    width: 1920px;
    height: 1080px;
    overflow: hidden;
}
.container {
    width: 1920px;
    height: 1080px;
    padding: 36px 60px 40px 60px;
    display: flex;
    flex-direction: column;
    justify-content: space-between;
}
.top-nav {
    display: flex;
    align-items: center;
    justify-content: space-between;
    height: 56px;
    border-bottom: 1px solid rgba(255, 255, 255, 0.08);
    padding-bottom: 16px;
}
.logo {
    font-size: 28px;
    font-weight: 800;
    letter-spacing: -0.5px;
    display: flex;
    align-items: center;
    gap: 8px;
    color: #FFFFFF;
}
.badge-rc {
    background: linear-gradient(90deg, #E11D48, #BE123C);
    color: white;
    font-size: 12px;
    font-weight: 800;
    padding: 6px 14px;
    border-radius: 20px;
    letter-spacing: 0.5px;
}
.badge-e2e {
    background: rgba(59, 130, 246, 0.15);
    border: 1px solid #3B82F6;
    color: #93C5FD;
    font-size: 12px;
    font-weight: 700;
    padding: 6px 14px;
    border-radius: 20px;
}
.badge-alert {
    background: rgba(239, 68, 68, 0.2);
    border: 1px solid #EF4444;
    color: #FCA5A5;
    font-size: 12px;
    font-weight: 800;
    padding: 6px 14px;
    border-radius: 20px;
}
.badge-active {
    background: rgba(16, 185, 129, 0.2);
    border: 1px solid #10B981;
    color: #6EE7B7;
    font-size: 12px;
    font-weight: 800;
    padding: 6px 14px;
    border-radius: 20px;
}
.split-view {
    display: flex;
    align-items: center;
    justify-content: center;
    gap: 40px;
    height: 820px;
}
.phone-frame {
    border-radius: 36px;
    box-shadow: 0 25px 60px -10px rgba(0, 0, 0, 0.8), 0 0 0 1px rgba(255, 255, 255, 0.1);
    display: flex;
    flex-direction: column;
    padding: 24px;
    height: 780px;
    position: relative;
}
.senior-phone {
    background: #FBF9F5;
    width: 440px;
    border: 8px solid #E2E8F0;
    color: #1C1917;
}
.guardian-phone {
    background: #090A0C;
    width: 440px;
    border: 8px solid #1E293B;
    color: #F8FAFC;
}
.phone-notch {
    width: 120px;
    height: 18px;
    background: #E2E8F0;
    border-radius: 0 0 12px 12px;
    margin: -24px auto 16px auto;
}
.dark-notch {
    background: #1E293B;
}
.senior-header {
    text-align: center;
    margin-bottom: 16px;
}
.brand-sub {
    font-size: 13px;
    font-weight: bold;
    color: #78716C;
    margin-bottom: 2px;
}
.namaste {
    font-size: 28px;
    font-weight: 800;
    color: #1C1917;
}
.sub-greeting {
    font-size: 13px;
    color: #78716C;
    margin-top: 3px;
}
.senior-card-green {
    background: #DCFCE7;
    border: 1.5px solid #86EFAC;
    border-radius: 18px;
    padding: 18px;
    text-align: center;
    margin-bottom: 14px;
}
.pill-green {
    background: #15803D;
    color: white;
    font-size: 10.5px;
    font-weight: 800;
    display: inline-block;
    padding: 4px 12px;
    border-radius: 12px;
    margin-bottom: 6px;
    letter-spacing: 0.5px;
}
.card-title-green {
    font-size: 16px;
    font-weight: 800;
    color: #15803D;
}
.card-desc-green {
    font-size: 12px;
    color: #166534;
    margin-top: 4px;
    line-height: 1.35;
}
.chips-container {
    display: flex;
    gap: 6px;
    flex-wrap: wrap;
    justify-content: center;
}
.chip {
    background: #FEF3C7;
    border: 1px solid #FDE68A;
    color: #78350F;
    font-size: 11px;
    font-weight: 700;
    padding: 5px 10px;
    border-radius: 8px;
}
.active-chip {
    background: #FDE68A;
    border-color: #F59E0B;
}
.senior-card-red {
    background: #FEE2E2;
    border: 1.5px solid #FCA5A5;
    border-radius: 16px;
    padding: 14px;
}
.card-title-red {
    font-size: 14px;
    font-weight: 800;
    color: #991B1B;
}
.card-desc-red {
    font-size: 11.5px;
    color: #B91C1C;
    margin-top: 2px;
    line-height: 1.3;
}
.senior-footer {
    margin-top: auto;
    text-align: center;
    font-size: 11px;
    color: #A8A29E;
    line-height: 1.4;
}
.guardian-header {
    display: flex;
    align-items: center;
    justify-content: space-between;
    margin-bottom: 14px;
}
.guardian-title {
    font-size: 16px;
    font-weight: 800;
    color: #F8FAFC;
}
.guardian-sub {
    font-size: 11px;
    color: #94A3B8;
}
.btn-pair {
    background: #10B981;
    color: black;
    font-size: 11px;
    font-weight: 800;
    padding: 5px 10px;
    border-radius: 8px;
}
.safety-score-card {
    background: #13151A;
    border: 1.5px solid #10B981;
    border-radius: 16px;
    padding: 14px;
    display: flex;
    align-items: center;
    gap: 14px;
    margin-bottom: 12px;
}
.score-ring-box {
    width: 64px;
    height: 64px;
    border-radius: 32px;
    border: 3px solid #10B981;
    display: flex;
    flex-direction: column;
    align-items: center;
    justify-content: center;
    background: #064E3B;
    flex-shrink: 0;
}
.score-num {
    font-size: 20px;
    font-weight: 900;
    color: white;
}
.score-label {
    font-size: 7px;
    font-weight: 800;
    color: #6EE7B7;
    letter-spacing: 0.5px;
}
.score-meta {
    flex: 1;
}
.score-status {
    font-size: 12px;
    font-weight: 800;
    color: #10B981;
}
.score-detail {
    font-size: 11px;
    color: #94A3B8;
    margin-top: 2px;
    line-height: 1.3;
}
.pro-card {
    background: #13151A;
    border: 1px solid #22262F;
    border-radius: 16px;
    padding: 14px;
    margin-bottom: 12px;
}
.badge-pro {
    background: #064E3B;
    color: #34D399;
    font-size: 9.5px;
    font-weight: 800;
    padding: 2px 7px;
    border-radius: 6px;
}
.seat-count {
    color: #A7F3D0;
    font-size: 11px;
    font-weight: 700;
}
.pro-title {
    font-size: 14px;
    font-weight: 800;
    color: #F8FAFC;
    margin-top: 6px;
}
.pro-desc {
    font-size: 11.5px;
    color: #94A3B8;
    margin-top: 3px;
    line-height: 1.3;
}
.fleet-section-title {
    font-size: 10px;
    font-weight: 800;
    letter-spacing: 0.5px;
    color: #64748B;
    margin: 6px 0;
}
.device-card {
    background: #13151A;
    border: 1px solid #22262F;
    border-radius: 12px;
    padding: 12px;
    margin-bottom: 8px;
}
.device-name {
    font-size: 13px;
    font-weight: 700;
    color: #F8FAFC;
}
.device-desc {
    font-size: 10.5px;
    color: #94A3B8;
    margin-top: 3px;
}
.center-bridge {
    display: flex;
    flex-direction: column;
    align-items: center;
    justify-content: center;
    gap: 12px;
    text-align: center;
    width: 220px;
}
.bridge-tag {
    background: rgba(255, 255, 255, 0.08);
    font-size: 10px;
    font-weight: 800;
    letter-spacing: 1px;
    padding: 4px 10px;
    border-radius: 12px;
    color: #CBD5E1;
}
.arrow {
    font-size: 36px;
}
.bridge-desc {
    font-size: 13px;
    color: #94A3B8;
    line-height: 1.4;
}
.card-panel {
    background: rgba(19, 21, 26, 0.85);
    border: 1px solid rgba(255, 255, 255, 0.1);
    border-radius: 24px;
    padding: 32px;
    display: flex;
    flex-direction: column;
    gap: 16px;
    box-shadow: 0 20px 40px rgba(0, 0, 0, 0.5);
}
.panel-tag {
    font-size: 11px;
    font-weight: 800;
    letter-spacing: 1px;
    color: #38BDF8;
}
.panel-header {
    font-size: 22px;
    font-weight: 800;
    color: white;
}
.role-card {
    display: flex;
    align-items: center;
    gap: 16px;
    padding: 20px;
    border-radius: 18px;
}
.blue-role {
    background: #172554;
    border: 1.5px solid #3B82F6;
}
.green-role {
    background: #064E3B;
    border: 1.5px solid #10B981;
}
.role-icon {
    font-size: 36px;
}
.role-title {
    font-size: 16px;
    font-weight: 800;
    color: white;
}
.role-sub {
    font-size: 12px;
    color: #CBD5E1;
    margin-top: 4px;
    line-height: 1.35;
}
.quote-box {
    background: rgba(0, 0, 0, 0.3);
    border-left: 3px solid #F59E0B;
    padding: 12px 16px;
    font-size: 13px;
    color: #FDE68A;
    border-radius: 4px;
    font-style: italic;
}
.advisor-box {
    background: #FFFFFF;
    border: 1.5px solid #EAE6DF;
    border-radius: 16px;
    padding: 14px;
}
.fake-input-light {
    background: #F5F2EB;
    border: 1px solid #E7E3DA;
    border-radius: 8px;
    padding: 8px 10px;
    font-size: 11.5px;
    color: #1C1917;
    margin-bottom: 10px;
    line-height: 1.35;
}
.verdict-alert-card {
    background: #FEE2E2;
    border: 1.5px solid #FCA5A5;
    border-radius: 12px;
    padding: 12px;
}
.badge-red-solid {
    background: #B91C1C;
    color: white;
    font-size: 9.5px;
    font-weight: 800;
    padding: 3px 8px;
    border-radius: 6px;
    display: inline-block;
}
.verdict-title {
    font-size: 13.5px;
    font-weight: 800;
    color: #B91C1C;
    margin-top: 6px;
}
.verdict-body {
    font-size: 11px;
    color: #7F1D1D;
    margin-top: 3px;
    line-height: 1.3;
}
.flags-text {
    font-size: 10px;
    color: #991B1B;
    font-weight: 700;
    margin-top: 6px;
}
.tts-btn {
    background: #991B1B;
    color: white;
    font-size: 10.5px;
    font-weight: 800;
    padding: 6px 10px;
    border-radius: 6px;
    text-align: center;
    flex: 1;
}
.siren-alert-btn {
    background: #DC2626;
    color: white;
    font-size: 10.5px;
    font-weight: 800;
    padding: 6px 10px;
    border-radius: 6px;
    text-align: center;
    flex: 1;
}
.enclave-box {
    background: #0F172A;
    border: 1.5px solid #38BDF8;
    border-radius: 18px;
    padding: 22px;
}
.enclave-title {
    font-size: 16px;
    font-weight: 800;
    color: white;
    margin: 10px 0 14px 0;
}
.sas-fingerprint-box {
    background: #1E293B;
    border: 1px solid #475569;
    border-radius: 14px;
    padding: 16px;
    text-align: center;
    margin-bottom: 14px;
}
.sas-label {
    font-size: 10px;
    font-weight: 800;
    letter-spacing: 0.5px;
    color: #94A3B8;
}
.sas-emojis {
    font-size: 28px;
    margin: 8px 0;
    letter-spacing: 4px;
}
.sas-sub {
    font-size: 11px;
    color: #64748B;
}
.crypto-specs {
    font-size: 12px;
    color: #94A3B8;
    line-height: 1.6;
}
.pairing-pulse-card {
    background: #13151A;
    border: 1px solid #22262F;
    border-radius: 14px;
    padding: 18px;
}
.pairing-phone-header {
    text-align: center;
    margin-bottom: 14px;
}
.qr-box {
    display: flex;
    justify-content: center;
    margin-bottom: 16px;
}
.fake-qr {
    background: white;
    padding: 16px;
    border-radius: 16px;
    text-align: center;
}
.qr-pattern {
    width: 180px;
    height: 180px;
    background: repeating-conic-gradient(#000 0% 25%, #fff 0% 50%) 50% / 20px 20px;
    border-radius: 8px;
}
.qr-code-text {
    font-size: 14px;
    font-weight: 900;
    color: black;
    margin-top: 10px;
    letter-spacing: 1px;
}
.poll-status {
    font-size: 12px;
    color: #6EE7B7;
    text-align: center;
    font-weight: bold;
    margin-bottom: 12px;
}
.btn-refresh {
    background: #10B981;
    color: black;
    font-weight: 800;
    font-size: 13px;
    text-align: center;
    padding: 12px;
    border-radius: 10px;
}
.inbox-card {
    background: #13151A;
    border: 1px solid #22262F;
    border-radius: 14px;
    padding: 12px;
    margin-bottom: 10px;
}
.inbox-item {
    background: #1A1D24;
    border: 1px solid #2B303C;
    border-radius: 10px;
    padding: 10px;
}
.masked-otp {
    background: #000;
    color: #FCA5A5;
    padding: 2px 6px;
    border-radius: 4px;
    font-weight: bold;
}
.threat-alert-card {
    background: #3B1010;
    border: 2px solid #EF4444;
    border-radius: 14px;
    padding: 14px;
    margin-bottom: 10px;
}
.btn-block-hash {
    background: #DC2626;
    color: white;
    font-weight: 800;
    font-size: 12px;
    text-align: center;
    padding: 10px;
    border-radius: 8px;
}
.prering-action-card {
    background: #13151A;
    border: 1px solid #22262F;
    border-radius: 14px;
    padding: 12px;
}
.value-item {
    display: flex;
    gap: 16px;
    align-items: flex-start;
    margin-bottom: 16px;
}
.val-num {
    background: #3B82F6;
    color: white;
    font-size: 14px;
    font-weight: 900;
    width: 28px;
    height: 28px;
    border-radius: 14px;
    display: flex;
    align-items: center;
    justify-content: center;
    flex-shrink: 0;
}
.val-title {
    font-size: 15px;
    font-weight: 800;
    color: white;
}
.val-desc {
    font-size: 12px;
    color: #94A3B8;
    margin-top: 3px;
    line-height: 1.4;
}
.plan-card {
    background: #1E293B;
    border: 1.5px solid #475569;
    border-radius: 14px;
    padding: 14px;
    margin-bottom: 10px;
}
.active-plan {
    background: #064E3B;
    border: 2px solid #10B981;
}
.judge-eval-box {
    background: #2C2416;
    border: 1px solid #F59E0B;
    border-radius: 14px;
    padding: 12px;
    margin-bottom: 10px;
}
.fake-input {
    background: #1E1E1E;
    color: white;
    font-weight: bold;
    font-size: 13px;
    padding: 8px 12px;
    border-radius: 8px;
    border: 1px solid #424242;
    flex: 1;
}
.btn-unlock-pro {
    background: #F59E0B;
    color: black;
    font-weight: 800;
    font-size: 12px;
    padding: 8px 12px;
    border-radius: 8px;
    margin-left: 8px;
}
.status-pill-gold {
    background: #1E1E1E;
    color: #FCD34D;
    font-size: 11.5px;
    font-weight: 800;
    text-align: center;
    padding: 8px;
    border-radius: 20px;
    border: 1px solid #F59E0B;
}
.hero-close-view {
    display: flex;
    flex-direction: column;
    align-items: center;
    justify-content: center;
    text-align: center;
    height: 820px;
    gap: 20px;
}
.hero-shield-icon {
    font-size: 64px;
}
.hero-title {
    font-size: 48px;
    font-weight: 900;
    letter-spacing: -1px;
    color: white;
}
.hero-subtitle {
    font-size: 18px;
    color: #94A3B8;
    max-width: 800px;
}
.tools-grid {
    display: flex;
    gap: 20px;
    margin: 16px 0;
}
.tool-card {
    background: #13151A;
    border: 1px solid #22262F;
    border-radius: 18px;
    padding: 20px;
    width: 320px;
    text-align: left;
}
.tool-icon {
    font-size: 28px;
    margin-bottom: 8px;
}
.tool-title {
    font-size: 16px;
    font-weight: 800;
    color: white;
}
.tool-desc {
    font-size: 12px;
    color: #94A3B8;
    margin-top: 4px;
    line-height: 1.4;
}
.founder-card {
    background: rgba(255, 255, 255, 0.05);
    border: 1px solid rgba(255, 255, 255, 0.1);
    border-radius: 18px;
    padding: 16px 36px;
}
.founder-title {
    font-size: 16px;
    font-weight: 800;
    color: #FCD34D;
}
.founder-sub {
    font-size: 13px;
    color: #CBD5E1;
    margin-top: 2px;
}
.links-row {
    display: flex;
    gap: 12px;
    font-size: 12px;
    color: #94A3B8;
    margin-top: 8px;
    justify-content: center;
}
.caption-bar {
    height: 70px;
    background: rgba(15, 23, 42, 0.85);
    border: 1px solid rgba(255, 255, 255, 0.12);
    border-radius: 16px;
    display: flex;
    align-items: center;
    padding: 0 28px;
    box-shadow: 0 10px 30px rgba(0, 0, 0, 0.5);
}
.caption-text {
    font-size: 14px;
    color: #F8FAFC;
    line-height: 1.4;
}
.row { display: flex; align-items: center; gap: 10px; }
.row-between { display: flex; align-items: center; justify-content: space-between; }
"""

def ensure_audio(scene, force=False):
    audio_path = scene["audio"]
    if force or not os.path.exists(audio_path) or os.path.getsize(audio_path) == 0:
        os.makedirs(os.path.dirname(audio_path), exist_ok=True)
        narration = scene.get("narration", scene.get("caption", ""))
        print(f"  🎙️ Generating Neural Voiceover (+15% rate): {scene['id']}...")
        cmd = [
            "edge-tts",
            "--voice", VOICE_NAME,
            "--rate=+15%",
            "--text", narration,
            "--write-media", audio_path
        ]
        subprocess.run(cmd, check=True)

def render_scene_html(scene, out_html):
    html_content = f"""<!DOCTYPE html>
<html>
<head>
    <meta charset="utf-8">
    <title>{scene['title']}</title>
    <style>{CSS}</style>
</head>
<body>
    {scene['html']}
</body>
</html>"""
    with open(out_html, "w") as f:
        f.write(html_content)

def capture_screenshot(html_file, out_png):
    cmd = [
        "google-chrome",
        "--headless",
        "--disable-gpu",
        "--no-sandbox",
        "--screenshot=" + out_png,
        "--window-size=1920,1080",
        "file://" + html_file
    ]
    subprocess.run(cmd, check=True, stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)

def make_clip(img_file, audio_file, out_clip):
    probe = subprocess.check_output([
        "ffprobe", "-i", audio_file,
        "-show_entries", "format=duration",
        "-v", "quiet", "-of", "json"
    ])
    dur = float(json.loads(probe)["format"]["duration"])
    # Pro video encoding: 1920x1080, 30fps, H.264, AAC 192k audio
    cmd = [
        "ffmpeg", "-y",
        "-loop", "1", "-r", "30", "-i", img_file,
        "-i", audio_file,
        "-t", str(dur),
        "-c:v", "libx264",
        "-preset", "ultrafast",
        "-tune", "stillimage",
        "-c:a", "aac",
        "-b:a", "192k",
        "-pix_fmt", "yuv420p",
        out_clip
    ]
    subprocess.run(cmd, check=True, stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)

def main():
    print("=== KAVACH 2-MINUTE WINNING DEMO RENDERER (GOD-TIER REVISION) ===")
    clips = []
    
    for i, s in enumerate(SCENES, 1):
        print(f"\n[Scene {i}/6] Processing {s['id']}...")
        html_path = os.path.join(OUTPUT_DIR, f"{s['id']}.html")
        png_path = os.path.join(OUTPUT_DIR, f"{s['id']}.png")
        clip_path = os.path.join(OUTPUT_DIR, f"{s['id']}.mp4")
        
        # 1. Ensure voiceover audio clip exists with +15% pacing (<120s limit)
        ensure_audio(s, force=True)
        
        # 2. Render fresh HTML and capture Full HD screenshot
        render_scene_html(s, html_path)
        capture_screenshot(html_path, png_path)
        print(f"  ✓ Screenshot ready: {png_path}")
        
        # 3. Render synchronized video clip
        make_clip(png_path, s['audio'], clip_path)
        print(f"  ✓ Video clip generated: {clip_path}")
        clips.append(clip_path)

    # Concat clips
    print("\n[Concat] Joining 6 acts into final master video...")
    concat_list = os.path.join(OUTPUT_DIR, "concat.txt")
    with open(concat_list, "w") as f:
        for c in clips:
            f.write(f"file '{c}'\n")

    cmd = [
        "ffmpeg", "-y",
        "-f", "concat",
        "-safe", "0",
        "-i", concat_list,
        "-c", "copy",
        FINAL_VIDEO
    ]
    subprocess.run(cmd, check=True, stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)
    
    # Also copy to artifact directory so chat UI & user can directly view it
    try:
        shutil.copyfile(FINAL_VIDEO, ARTIFACT_VIDEO)
        print(f"  ✓ Artifact updated: {ARTIFACT_VIDEO}")
    except Exception as e:
        print(f"  Warning: failed copying artifact: {e}")

    # Probe final video
    probe = subprocess.check_output([
        "ffprobe", "-i", FINAL_VIDEO,
        "-show_entries", "format=duration,size,bit_rate",
        "-v", "quiet", "-of", "json"
    ])
    meta = json.loads(probe)["format"]
    dur = float(meta["duration"])
    size_mb = int(meta["size"]) / (1024 * 1024)
    
    print("\n==================================================")
    print("🎉 MASTER 2-MINUTE DEMO VIDEO GENERATED SUCCESSFULLY!")
    print(f"Location: {FINAL_VIDEO}")
    print(f"Duration: {dur:.2f}s ({int(dur // 60)}m {int(dur % 60)}s)")
    print(f"File Size: {size_mb:.2f} MB")
    print(f"Resolution: 1920x1080 Full HD (30 FPS, H.264 / AAC)")
    print("==================================================")

if __name__ == "__main__":
    main()
