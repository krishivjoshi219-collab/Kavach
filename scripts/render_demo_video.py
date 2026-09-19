#!/usr/bin/env python3
"""
Render 2-Minute Winning Demo Video with Neural AI Voiceover.
Produces assets/kavach-demo-2min.mp4 (<120 seconds, 1080p Full HD).
"""
import os
import sys
import json
import subprocess
import glob

OUTPUT_DIR = "/tmp/kavach_render"
ASSETS_DIR = "/home/k/Prototype/Kavach/assets"
AUDIO_DIR = "/tmp/kavach_audio_real"
FINAL_VIDEO = os.path.join(ASSETS_DIR, "kavach-demo-2min.mp4")

os.makedirs(OUTPUT_DIR, exist_ok=True)
os.makedirs(ASSETS_DIR, exist_ok=True)

SCENES = [
    {
        "id": "act1_hook",
        "audio": os.path.join(AUDIO_DIR, "act1_hook.mp3"),
        "title": "Act 1: The Two-Sided Household & RevenueCat Multi-Seat Model",
        "caption": "Elder fraud steals $10B+ every year. The victims are our parents, but the ones who worry and pay are adult children.",
        "html": """
        <div class="container">
            <div class="top-nav">
                <div class="logo">🛡️ Kavach</div>
                <div class="badge-rc">REVENUECAT SHIPATON 2026 • NEXT GEN AWARD</div>
                <div class="badge-e2e">E2E ENCRYPTED (GOOGLE TINK ECIES)</div>
            </div>
            
            <div class="split-view">
                <!-- Left Phone: Senior Sanctuary -->
                <div class="phone-frame senior-phone">
                    <div class="phone-notch"></div>
                    <div class="senior-header">
                        <div class="namaste">Namaste 🙏</div>
                        <div class="sub-greeting">Aapka phone surakshit hai • Your phone is safe</div>
                    </div>
                    <div class="senior-card-green">
                        <div class="pill-green">SHIELD ACTIVE</div>
                        <div class="card-title-green">Guarding Calls & Messages</div>
                        <div class="card-desc-green">Scams and fake bank calls are quietly blocked before ringing. Zero panic.</div>
                    </div>
                    <div class="senior-card-amber">
                        <div class="row">
                            <span class="icon">❓</span>
                            <div>
                                <div class="card-title-amber">Ask Kavach / Something Feels Wrong</div>
                                <div class="card-desc-amber">Tap if someone asks for money or OTP.</div>
                            </div>
                        </div>
                    </div>
                    <div class="senior-footer">
                        <span>🔒 Private to your phone • Never uploaded to cloud</span>
                    </div>
                </div>

                <!-- Center Vs / Bridge Banner -->
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
                    <div class="pro-card">
                        <div class="row-between">
                            <span class="badge-pro">REVENUECAT FAMILY PRO</span>
                            <span class="seat-count">2 of 3 Parent Seats Active</span>
                        </div>
                        <div class="pro-title">Household Protection Plan</div>
                        <div class="pro-desc">End-to-end encrypted fraud shield. Covers Dad (Pixel 8) and Mom (Galaxy S22).</div>
                    </div>
                    <div class="fleet-section-title">PROTECTED PARENT DEVICES</div>
                    <div class="device-card">
                        <div class="row-between">
                            <span class="device-name">Dad (Pixel 8)</span>
                            <span class="badge-active">ACTIVE</span>
                        </div>
                        <div class="device-desc">Incoming call screening active • Battery 82% • 0 threats</div>
                    </div>
                    <div class="device-card">
                        <div class="row-between">
                            <span class="device-name">Mom (Galaxy S22)</span>
                            <span class="badge-alert">1 ALERT</span>
                        </div>
                        <div class="device-desc">1 fake bank SMS quarantined at 11:40 AM • Phone kept silent</div>
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
        "caption": "We eliminated confusing mode switchers. On first launch, each phone selects its sovereign role once.",
        "html": """
        <div class="container">
            <div class="top-nav">
                <div class="logo">🛡️ Kavach</div>
                <div class="badge-rc">NO 'SWITCH TO MANAGER' CONFUSION</div>
                <div class="badge-e2e">ROLE ROUTING PERSISTENCE</div>
            </div>
            
            <div class="split-view">
                <!-- Left: First Launch Role Selection -->
                <div class="card-panel">
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

                <!-- Right Phone: Senior Sanctuary Full Display -->
                <div class="phone-frame senior-phone" style="width: 440px;">
                    <div class="phone-notch"></div>
                    <div class="senior-header">
                        <div class="namaste">Namaste 🙏</div>
                        <div class="sub-greeting">Aapka phone surakshit hai • Your phone is safe</div>
                    </div>
                    <div class="senior-card-green">
                        <div class="pill-green">SHIELD ACTIVE</div>
                        <div class="card-title-green">Guarding Your Calls & Messages</div>
                        <div class="card-desc-green">Scams and fake bank calls are quietly blocked before ringing. You don't need to do anything.</div>
                    </div>
                    <div class="senior-card-amber">
                        <div class="row">
                            <span class="icon">❓</span>
                            <div>
                                <div class="card-title-amber">1-Tap Scam Defense Advisor</div>
                                <div class="card-desc-amber">"RUKO! Never Give OTP" • "Electricity Cut Threat is FAKE" • "Digital Arrest is a Fraud"</div>
                            </div>
                        </div>
                    </div>
                    <div class="senior-card-red">
                        <div class="row">
                            <span class="icon">🚨</span>
                            <div>
                                <div class="card-title-red">Emergency Family Siren</div>
                                <div class="card-desc-red">Instantly interrupts scam pressure and alerts your adult children.</div>
                            </div>
                        </div>
                    </div>
                </div>
            </div>

            <div class="caption-bar">
                <div class="caption-text">🎙️ "We eliminated confusing mode switchers. On first launch, each phone selects its sovereign role once. For parents, Kavach is a peaceful sanctuary: high-contrast, large touch targets, and warm Hindi and English reassurance. No technical jargon, no false alarms."</div>
            </div>
        </div>
        """
    },
    {
        "id": "act3_e2e",
        "audio": os.path.join(AUDIO_DIR, "act3_e2e.mp3"),
        "title": "Act 3: Extensive E2E Cryptographic Linking (Google Tink ECIES)",
        "caption": "Google Tink ECIES-P256 hybrid encryption backed by Android Keystore hardware with mutual 6-emoji SAS fingerprint.",
        "html": """
        <div class="container">
            <div class="top-nav">
                <div class="logo">🛡️ Kavach</div>
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
                            <div>• <b>Keystore:</b> AndroidKeystore AES-256-GCM Master Key (TEE / StrongBox)</div>
                            <div>• <b>Cryptosystem:</b> Google Tink ECIES (P-256 + HKDF-SHA256 + AES-128-GCM)</div>
                            <div>• <b>Relay Guarantee:</b> Server relay holds ciphertext envelopes only. Never sees plaintext.</div>
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
                <div class="caption-text">🎙️ "On the adult child command console, the link to parents' devices is protected by Google Tink ECIES-P256 hybrid encryption backed by Android Keystore hardware. Both devices share a mutual six-emoji verification fingerprint. The server relay holds only encrypted ciphertext envelopes, never listening to calls or reading personal messages."</div>
            </div>
        </div>
        """
    },
    {
        "id": "act4_attack",
        "audio": os.path.join(AUDIO_DIR, "act4_attack.mp3"),
        "title": "Act 4: On-Device Scam Lab & Threat Quarantine",
        "caption": "To test defense without waiting for an actual criminal, Kavach includes an on-device Scam Defense Lab.",
        "html": """
        <div class="container">
            <div class="top-nav">
                <div class="logo">🛡️ Kavach</div>
                <div class="badge-alert">ON-DEVICE SCAM DEFENSE LAB</div>
                <div class="badge-active">REAL RULE ENGINE HEURISTICS</div>
            </div>
            
            <div class="split-view">
                <!-- Left Phone: ScamLabActivity -->
                <div class="phone-frame guardian-phone" style="width: 480px; padding: 20px;">
                    <div class="phone-notch dark-notch"></div>
                    <div style="text-align: center; margin-bottom: 12px;">
                        <div style="font-size: 18px; font-weight: 800; color: white;">Scam Defense Lab 🧪</div>
                        <div style="font-size: 11px; color: #94A3B8; margin-top: 2px;">On-Device RuleEngine & Threat Quarantine</div>
                    </div>

                    <div style="background: #7F1D1D; border: 1.5px solid #EF4444; border-radius: 12px; padding: 12px; text-align: center; font-size: 12px; font-weight: 800; color: white; margin-bottom: 12px;">
                        🔴 SIMULATE LIVE ATTACK
                    </div>

                    <div style="background: #1C1917; border: 1px solid #EF4444; border-radius: 12px; padding: 14px; margin-bottom: 12px;">
                        <div style="font-size: 13px; font-weight: 800; color: #EF4444;">🔴 LIVE ATTACK INTERCEPTED:</div>
                        <div style="font-size: 11px; color: #E2E8F0; margin-top: 6px; line-height: 1.5;">
                            • <b>Verdict:</b> SCAM (Confidence: 95%)<br>
                            • <b>Senior Screen:</b> 100% QUIET (SMS never buzzed)<br>
                            • <b>Quarantined:</b> Stored in encrypted vault<br>
                            • <b>E2E Forwarded:</b> Sealed alert sent to guardian<br>
                            • <b>Sender Hash:</b> <code>sha256(hid+num)</code> auto-learned
                        </div>
                    </div>

                    <div style="font-size: 10px; font-weight: bold; color: #64748B; margin-bottom: 6px;">BUILT-IN TEST VECTORS:</div>
                    <div style="background: #13151A; border: 1px solid #22262F; border-radius: 10px; padding: 10px; margin-bottom: 6px;">
                        <div style="font-size: 12px; font-weight: bold; color: white;">1. Fake Bank / Account Frozen</div>
                        <div style="font-size: 10px; color: #94A3B8;">Sender: +91-98XXX-BANK1 • OTP Demand (+3)</div>
                    </div>
                    <div style="background: #13151A; border: 1px solid #22262F; border-radius: 10px; padding: 10px;">
                        <div style="font-size: 12px; font-weight: bold; color: white;">2. Electricity Disconnection APK</div>
                        <div style="font-size: 10px; color: #94A3B8;">Sender: +91-91XXX-POWER • APK Link (+2)</div>
                    </div>
                </div>

                <!-- Right Phone: Guardian Alert & 1-Tap Block -->
                <div class="phone-frame guardian-phone" style="width: 500px;">
                    <div class="phone-notch dark-notch"></div>
                    <div class="threat-alert-card">
                        <div class="badge-alert" style="display: inline-block;">🔴 SCAM INTERCEPTED & QUARANTINED</div>
                        <div class="threat-lure">
                            "Dear Customer, your bank account has been frozen due to suspicious activity. Share OTP ****** or police will arrest you."
                        </div>
                        <div class="red-flags-box">
                            <b>RULE ENGINE THREAT BREAKDOWN:</b><br>
                            • OTP demand (weight: +3)<br>
                            • Artificial freeze urgency (weight: +3)<br>
                            • Police threat (weight: +2)<br>
                            <b>OTP Masked:</b> <span style="background: #000; padding: 2px 8px; border-radius: 4px; color: #FCA5A5;">******</span>
                        </div>
                        <div class="btn-block-hash">
                            🛡️ Block Sender Hash for Household
                        </div>
                    </div>

                    <div class="prering-action-card">
                        <div class="row-between">
                            <span style="color: #F8FAFC; font-weight: bold; font-size: 14px;">Household Security Result:</span>
                            <span class="badge-active">PROTECTED</span>
                        </div>
                        <div style="font-size: 13px; color: #94A3B8; margin-top: 6px;">
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
        "caption": "One paying adult child subscription covers 3 parent devices. Unlock Pro with promo SHIPATON-JUDGE.",
        "html": """
        <div class="container">
            <div class="top-nav">
                <div class="logo">🛡️ Kavach</div>
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
                            <div class="val-title">Live SDK & Webhooks</div>
                            <div class="val-desc">Android app listens to Purchases SDK callbacks. Server handles EXPIRATION, RENEWAL, and PRODUCT_CHANGE via RevenueCat webhooks.</div>
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

                    <div class="judge-eval-box">
                        <div style="font-size: 13px; font-weight: bold; color: #F59E0B;">⚖️ RevenueCat Shipaton Judge Evaluation</div>
                        <div style="font-size: 11px; color: #FDE68A; margin-top: 2px;">Evaluate full Pro features in TEST MODE:</div>
                        <div class="row" style="margin-top: 8px;">
                            <div class="fake-input">SHIPATON-JUDGE</div>
                            <div class="btn-unlock-pro">Unlock Pro ✓</div>
                        </div>
                    </div>

                    <div class="status-pill-gold">
                        ✨ PRO FAMILY SHIELD ACTIVE (3 Parent Seats)
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
        "caption": "Adult children can remotely dispatch encrypted whisper warnings and trigger the emergency siren via our live zero-knowledge Render relay.",
        "html": """
        <div class="container">
            <div class="top-nav">
                <div class="logo">🛡️ Kavach</div>
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
                        <div class="tool-desc">Signed emergency alarm interrupts high-pressure coercion in progress and alerts guardians.</div>
                    </div>
                    <div class="tool-card">
                        <div class="tool-icon">🔒</div>
                        <div class="tool-title">Zero-Knowledge Relay</div>
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
    margin-bottom: 20px;
}
.namaste {
    font-size: 32px;
    font-weight: 800;
    color: #1C1917;
}
.sub-greeting {
    font-size: 14px;
    color: #78716C;
    margin-top: 4px;
}
.senior-card-green {
    background: #DCFCE7;
    border: 1.5px solid #86EFAC;
    border-radius: 20px;
    padding: 24px;
    text-align: center;
    margin-bottom: 16px;
}
.pill-green {
    background: #15803D;
    color: white;
    font-size: 11px;
    font-weight: 800;
    display: inline-block;
    padding: 4px 12px;
    border-radius: 12px;
    margin-bottom: 8px;
}
.card-title-green {
    font-size: 18px;
    font-weight: 800;
    color: #15803D;
}
.card-desc-green {
    font-size: 13px;
    color: #166534;
    margin-top: 6px;
    line-height: 1.35;
}
.senior-card-amber {
    background: #FEF3C7;
    border: 1.5px solid #FDE68A;
    border-radius: 18px;
    padding: 18px;
    margin-bottom: 16px;
}
.card-title-amber {
    font-size: 15px;
    font-weight: 800;
    color: #92400E;
}
.card-desc-amber {
    font-size: 12px;
    color: #B45309;
    margin-top: 3px;
}
.senior-card-red {
    background: #FEE2E2;
    border: 1.5px solid #FCA5A5;
    border-radius: 18px;
    padding: 18px;
    margin-bottom: 16px;
}
.card-title-red {
    font-size: 15px;
    font-weight: 800;
    color: #991B1B;
}
.card-desc-red {
    font-size: 12px;
    color: #B91C1C;
    margin-top: 3px;
}
.senior-footer {
    margin-top: auto;
    text-align: center;
    font-size: 11px;
    color: #A8A29E;
}
.guardian-header {
    display: flex;
    align-items: center;
    justify-content: space-between;
    margin-bottom: 16px;
}
.guardian-title {
    font-size: 17px;
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
    padding: 6px 12px;
    border-radius: 8px;
}
.pro-card {
    background: #13151A;
    border: 1.5px solid #10B981;
    border-radius: 18px;
    padding: 18px;
    margin-bottom: 16px;
}
.badge-pro {
    background: #064E3B;
    color: #34D399;
    font-size: 10px;
    font-weight: 800;
    padding: 3px 8px;
    border-radius: 6px;
}
.seat-count {
    color: #A7F3D0;
    font-size: 11px;
    font-weight: 700;
}
.pro-title {
    font-size: 15px;
    font-weight: 800;
    color: #F8FAFC;
    margin-top: 8px;
}
.pro-desc {
    font-size: 12px;
    color: #94A3B8;
    margin-top: 4px;
    line-height: 1.3;
}
.fleet-section-title {
    font-size: 10px;
    font-weight: 800;
    letter-spacing: 0.5px;
    color: #64748B;
    margin: 8px 0;
}
.device-card {
    background: #13151A;
    border: 1px solid #22262F;
    border-radius: 14px;
    padding: 14px;
    margin-bottom: 10px;
}
.device-name {
    font-size: 14px;
    font-weight: 700;
    color: #F8FAFC;
}
.device-desc {
    font-size: 11px;
    color: #94A3B8;
    margin-top: 4px;
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
.threat-alert-card {
    background: #3B1010;
    border: 2px solid #EF4444;
    border-radius: 18px;
    padding: 20px;
    margin-bottom: 16px;
}
.threat-lure {
    font-size: 15px;
    font-weight: bold;
    color: white;
    margin: 12px 0 10px 0;
    line-height: 1.35;
}
.red-flags-box {
    background: rgba(0, 0, 0, 0.4);
    border-radius: 10px;
    padding: 12px;
    font-size: 12px;
    color: #FCA5A5;
    line-height: 1.5;
    margin-bottom: 14px;
}
.btn-block-hash {
    background: #DC2626;
    color: white;
    font-weight: 800;
    font-size: 14px;
    text-align: center;
    padding: 12px;
    border-radius: 10px;
}
.prering-action-card {
    background: #13151A;
    border: 1px solid #22262F;
    border-radius: 16px;
    padding: 18px;
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
    padding: 16px;
    margin-bottom: 12px;
}
.active-plan {
    background: #064E3B;
    border: 2px solid #10B981;
}
.judge-eval-box {
    background: #2C2416;
    border: 1px solid #F59E0B;
    border-radius: 14px;
    padding: 14px;
    margin-bottom: 12px;
}
.fake-input {
    background: #1E1E1E;
    color: white;
    font-weight: bold;
    font-size: 13px;
    padding: 10px 14px;
    border-radius: 8px;
    border: 1px solid #424242;
    flex: 1;
}
.btn-unlock-pro {
    background: #F59E0B;
    color: black;
    font-weight: 800;
    font-size: 12px;
    padding: 10px 14px;
    border-radius: 8px;
    margin-left: 8px;
}
.status-pill-gold {
    background: #1E1E1E;
    color: #FCD34D;
    font-size: 12px;
    font-weight: 800;
    text-align: center;
    padding: 10px;
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
        "-tune", "stillimage",
        "-c:a", "aac",
        "-b:a", "192k",
        "-pix_fmt", "yuv420p",
        out_clip
    ]
    subprocess.run(cmd, check=True, stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)

def main():
    print("=== KAVACH 2-MINUTE WINNING DEMO RENDERER ===")
    clips = []
    
    for i, s in enumerate(SCENES, 1):
        print(f"\n[Scene {i}/6] Rendering {s['id']}...")
        html_path = os.path.join(OUTPUT_DIR, f"{s['id']}.html")
        png_path = os.path.join(OUTPUT_DIR, f"{s['id']}.png")
        clip_path = os.path.join(OUTPUT_DIR, f"{s['id']}.mp4")
        
        render_scene_html(s, html_path)
        capture_screenshot(html_path, png_path)
        print(f"  ✓ Screenshot ready: {png_path}")
        
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
    
    # Probe final video
    probe = subprocess.check_output([
        "ffprobe", "-i", FINAL_VIDEO,
        "-show_entries", "format=duration,size,bit_rate",
        "-v", "quiet", "-of", "json"
    ])
    meta = json.loads(probe)["format"]
    dur = float(meta["duration"])
    size_mb = int(meta["size"]) / (1024 * 1024)
    
    print("\n==========================================")
    print("🎉 MASTER 2-MINUTE DEMO VIDEO GENERATED!")
    print(f"Location: {FINAL_VIDEO}")
    print(f"Duration: {dur:.2f}s ({int(dur // 60)}m {int(dur % 60)}s)")
    print(f"File Size: {size_mb:.2f} MB")
    print(f"Resolution: 1920x1080 Full HD (30 FPS)")
    print("==========================================")

if __name__ == "__main__":
    main()
