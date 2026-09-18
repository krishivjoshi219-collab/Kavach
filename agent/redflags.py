"""Deterministic scam-signal extraction + verdict logic.

Rule-based on purpose: the verdict must be explainable (every reason cited)
and testable without an LLM. An LLM may rephrase, never overrule.
"""
from __future__ import annotations

import re

# code, human label, patterns, weight, what-it-means + what-to-do
RULES: list[tuple[str, str, list[str], int, str]] = [
    ("OTP_ASK",
     "Asked for OTP / password / PIN",
     r"\botp\b|ओटीपी|one[- ]time|password|पासवर्ड|\bpin\b|पिन|\bcvv\b|expir\w* date",
     3, "No real bank or official ever asks for your OTP or PIN. Never share it."),
    ("THREAT",
     "Threats — freeze, arrest, legal action",
     (
     r"froze|frozen|block\w*|arrest|गिरफ्तार|police|पुलिस|fir|court|कोर्ट|legal action|jail|digital arrest|"
     r"account (will be |is )?(closed|blocked|suspended)"
     ),
     3, "Threats are the pressure tactic. Real officials send written notices, not threats."),
    ("URGENCY",
     "Artificial urgency — act now or else",
     (
      r"immediately|तुरंत|right now|within \d+ (minutes|hours)|urgent|hurry|at once|"
      r"last (warning|chance)|today itself|tonight|don't (hang|cut|disconnect)"
     ),
     2, "Scammers rush you so you cannot think or check with family."),
    ("IMPERSONATION",
     "Claims to be bank / police / government",
     (
     r"\bbank\b|बैंक|reserve bank|rbi|cyber ?cell|crime branch|income tax|cbi|"
     r"electricity|बिजली|bijli|gas agency|insurance (officer|company)"
     ),
     2, "Anyone can *claim* to be your bank. The safe move: hang up, call the printed number."),
    ("PAYMENT_EXTORT",
     "Demands money — gift cards, wire, crypto, instant transfer",
     (
     r"gift ?card|google play|voucher|wire|western union|crypto|bitcoin|usdt|"
     r"\bupi (collect|request)\b|\bcollect request\b|यूपीआई|qr ?code|क्यूआर|"
     r"processing fee|refundable deposit|pay .* fine|पैसा|paise"
     ),
     3, "Officials never collect fines over gift cards, QR codes, or instant transfers."),
    ("REMOTE_ACCESS",
     "Asks to install a screen-sharing app",
     (
     r"anydesk|teamviewer|rustdesk|screen ?shar|remote access|install .* app|"
     r"give.*access.*phone|share.*screen"
     ),
     3, "Screen-sharing apps hand them your phone. Never install one for a stranger."),
    ("KYC_PRIZE",
     "KYC update / prize / lottery lure with a link",
     (
     r"\bkyc\b|केवाईसी|update.*(account|pan|aadhaar)|lottery|लॉटरी|prize|इनाम|reward points|lucky draw|"
     r"click.*\blink\b|sms.*\blink\b|whatsapp.*\blink\b|\bapk\b"
     ),
     2, "Links in surprise messages install theft apps. Never tap them."),
    ("ID_HARVEST",
     "Fishes for ID numbers",
     (
     r"aadhaar|aadhar|आधार|pan ?(card|number)|account number|debit ?card|credit ?card|"
     r"date of birth|\bdob\b|mother'?s maiden"
     ),
     2, "ID numbers plus OTP is all a thief needs. Share neither."),
]

SAFE_PHRASES = [
    r"my (daughter|son|doctor|neighbor|neighbour) (called|came|visited)",
    r"i (took|had) my (medicines|medicine|breakfast|lunch|dinner|walk)",
    r"just (wanted to |want to )?say (hello|hi)|good (morning|evening|night)",
]


def extract_signals(text: str) -> list[dict]:
    low = text.lower()
    hits: list[dict] = []
    for code, label, pat, weight, meaning in RULES:
        # finditer + group(0): full matched text even when the pattern
        # contains groups (findall would return group tuples like ('','')).
        found = sorted({m.group(0) for m in re.finditer(pat, low) if m.group(0)})
        if found:
            hits.append({"code": code, "label": label, "weight": weight,
                         "examples": found[:4], "meaning": meaning})
    return hits


def score_verdict(signals: list[dict], transcript: str,
                  known_contact: bool = False) -> tuple[str, float, list[str]]:
    """Returns (verdict, confidence 0..1, cited reasons)."""
    score = sum(s["weight"] for s in signals)
    codes = {s["code"] for s in signals}
    reasons = [f"{s['label']} (e.g. “{s['examples'][0]}”)" for s in signals]

    if known_contact and score == 0:
        return ("LIKELY_SAFE", 0.8,
                ["Caller matches a saved safe contact and nothing suspicious was asked."])
    if score >= 5 or ({"OTP_ASK", "THREAT"} & codes and score >= 4):
        conf = min(0.95, 0.65 + 0.05 * score)
        return ("SCAM", conf, reasons)
    if score >= 3:
        return ("SUSPICIOUS", 0.6, reasons)
    if signals:
        return ("UNCERTAIN", 0.45, reasons)
    low = transcript.lower()
    if any(re.search(p, low) for p in SAFE_PHRASES):
        return ("LIKELY_SAFE", 0.7, ["Nothing was asked for; sounds like a routine family call."])
    return ("UNCERTAIN", 0.4,
            ["Not enough detail yet — one or two more answers will settle it."])


GUIDANCE = {
    "SCAM": ["Hang up right now — it is safe to simply disconnect.",
             "Do not share any OTP, PIN, or code with anyone, ever.",
             "Do not tap links or install any app they mentioned.",
             "Call your family, then call the number printed on your bank card."],
    "SUSPICIOUS": ["Do not share codes or install anything yet.",
                   "Hang up and call the official number yourself.",
                   "Tell a family member what happened."],
    "UNCERTAIN": ["Do not share codes or tap links while unsure.",
                  "Ask one family member to listen in before continuing.",
                  "I have saved everything so far — nothing is lost."],
    "LIKELY_SAFE": ["This looks fine — but if they later ask for codes or money, stop and tell me."],
}
