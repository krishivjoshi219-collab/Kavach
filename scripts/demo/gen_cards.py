#!/usr/bin/env python3
"""Generate the 6 animated story cards for the 16:9 demo (left panel).

Usage: python3 scripts/demo/gen_cards.py  (writes /tmp/opencode/cards/cardN.png)
Requires: Pillow, Noto Sans fonts (present on stock Ubuntu).
Hinglish lines are Latin transliteration, so plain Noto Sans suffices.
"""
from PIL import Image, ImageDraw, ImageFont

W, H = 1313, 1080
FB = "/usr/share/fonts/truetype/noto/NotoSans-Bold.ttf"
FR = "/usr/share/fonts/truetype/noto/NotoSans-Regular.ttf"


def F(p, s):
    return ImageFont.truetype(p, s)


ACTS = [
    ("ACT 1 - THE HOOK", "11:40 AM.", "Her thumb hovers over the OTP.",
     ["$10B+/yr elder fraud", "FBI IC3 estimates", "Dignity intact"], (255, 217, 138)),
    ("ACT 2 - THE SAVE", "Ruko! OTP mat do.", "Zero buzz. A calm siren rises instead.",
     ["Quarantine vault", "E2E forward", "OTP masked ******"], (255, 120, 120)),
    ("ACT 3 - WAR-ROOM", "Safety Score 100.", "The server sees only noise.",
     ["Tink ECIES-P256", "Hashes only", "SAS fingerprint"], (255, 217, 138)),
    ("ACT 4 - PRE-RING KILL", "Pehli ring se pehle, khatm.",
     "The callback dies before the first ring.",
     ["Block hash", "3-household shield", "Kill Switch"], (255, 120, 120)),
    ("ACT 5 - LEARNS + PAYS", "Learns every morning.",
     "Family Fortress $79.99/yr via RevenueCat.",
     ["Signed rules vN", "Pro $4.99/mo", "TEST MODE judges"], (255, 217, 138)),
    ("ACT 6 - CLOSE", "Aapka Kavach.", "Pause pressure. Verify independently.",
     ["Hindi", "Hinglish", "English"], (255, 217, 138)),
]

for idx, (kick, head, sub, chips, accent) in enumerate(ACTS, 1):
    img = Image.new("RGB", (W, H), (20, 16, 11))
    d = ImageDraw.Draw(img)
    for y in range(0, H, 4):  # warm vertical gradient
        t = y / H
        d.line([(0, y), (W, y)], fill=(int(20 + 30 * t), int(16 + 22 * t), int(11 + 14 * t)))
    # shield-K mascot (pure geometry, no emoji font needed)
    d.polygon([(W - 260, 120), (W - 90, 120), (W - 90, 300),
               (W - 175, 400), (W - 260, 300)], outline=(255, 217, 138))
    d.text((W - 208, 190), "K", font=F(FB, 110), fill=(255, 217, 138))
    d.text((90, 90), kick, font=F(FB, 40), fill=(200, 170, 120))
    d.text((90, 170), head, font=F(FB, 84), fill=accent)
    d.text((90, 300), sub, font=F(FR, 38), fill=(245, 234, 210))
    y = 470
    for c in chips:
        d.rounded_rectangle([90, y, min(W - 90, 90 + 26 * len(c)), y + 84],
                            radius=42, outline=accent, width=3)
        d.text((130, y + 18), c, font=F(FR, 34), fill=(245, 234, 210))
        y += 120
    d.text((90, H - 110), "KAVACH - Next Gen - %d/6" % idx, font=F(FB, 30),
           fill=(140, 120, 95))
    img.save("/tmp/opencode/cards/card%d.png" % idx)
print("CARDS_OK")
