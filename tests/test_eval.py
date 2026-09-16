"""Kavach eval: 10 scam scripts must be caught, 5 legit calls must stay clear."""
import uuid

from agent import models, protocols

SID = "demo-senior"

# (channel, who-claim, what-asked, pressure) — each must end SCAM or SUSPICIOUS
SCAM_SCRIPTS = [
    ("phone call", "HDFC bank officer",
     "My account is frozen, they want my OTP to unblock it",
     "Yes, police complaint will be filed today itself"),
    ("WhatsApp message", "RBI cyber cell",
     "Click the link to update KYC or account closes",
     "They said do it within 2 hours"),
    ("phone call", "electricity department",
     "Pay the pending bill tonight via the QR code they sent",
     "Power cut at midnight if I delay"),
    ("SMS", "unknown number",
     "I won a lottery, pay a small processing fee to claim",
     "Offer ends today"),
    ("phone call", "police crime branch",
     "My son is in custody, transfer bail money right now",
     "Do not hang up, do not tell anyone"),
    ("phone call", "bank manager",
     "Install AnyDesk so they can see my screen and help",
     "Hurry, the fraud is happening now"),
    ("message", "insurance company",
     "Share PAN and Aadhaar to release my policy bonus",
     "Last date is today"),
    ("phone call", "gas agency",
     "Pay a safety inspection fee over UPI collect request",
     "Connection will be cut tomorrow"),
    ("WhatsApp", "my grandson (voice sounded odd)",
     "He needs gift cards for an emergency, keep it secret",
     "Begged me not to tell his parents"),
    ("phone call", "income tax office",
     "A refund is waiting, confirm debit card and CVV",
     "Account will be seized otherwise"),
]

# Each must end LIKELY_SAFE or UNCERTAIN — never SCAM
LEGIT_CALLS = [
    ("phone call", "my daughter Priya", "She just said hello and asked about lunch", "No"),
    ("visit", "neighbor Shanti", "She returned my container and chatted", "No"),
    ("phone call", "Dr. Rao's clinic", "They reminded me of Tuesday's appointment", "No"),
    ("message", "my son", "He sent photos of the grandchildren", "No"),
    ("phone call", "HDFC bank", "They wished me on my birthday, asked for nothing", "No"),
]


def _walk(script):
    sess = f"eval-{uuid.uuid4().hex[:8]}"
    models.ensure_seed(SID)
    protocols.start_debrief(sess, SID)
    for answer in script:
        out = protocols.debrief_turn(sess, answer)
    return out


def test_scam_scripts_caught():
    missed = []
    for i, script in enumerate(SCAM_SCRIPTS):
        out = _walk(script)
        if out.get("verdict") not in ("SCAM", "SUSPICIOUS"):
            missed.append((i, out.get("verdict")))
    assert not missed, f"scam scripts missed: {missed}"


def test_legit_calls_stay_clear():
    flagged = []
    for i, script in enumerate(LEGIT_CALLS):
        out = _walk(script)
        if out.get("verdict") == "SCAM":
            flagged.append((i, script[1]))
    assert not flagged, f"legit calls flagged SCAM: {flagged}"


def test_verdicts_always_cite_evidence():
    out = _walk(SCAM_SCRIPTS[0])
    cards = {c["type"]: c for c in out["cards"]}
    assert "verdict" in cards and "•" in cards["verdict"]["body"]
    assert "guidance" in cards


def test_protocol_never_skips_stages():
    sess = f"eval-{uuid.uuid4().hex[:8]}"
    models.ensure_seed(SID)
    stages = [protocols.start_debrief(sess, SID)["stage"]]
    for a in ["call", "bank", "otp", "yes urgent"]:
        stages.append(protocols.debrief_turn(sess, a).get("stage"))
    assert stages == ["channel", "who", "what", "pressure", "verdict"], stages
