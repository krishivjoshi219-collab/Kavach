#!/usr/bin/env python3
"""
Kavach Studio Demo Video Renderer — Cinematic Apple & Google Keynote Caliber
Features:
- Smooth Continuous Motion Choreography & Dynamic Camera Glide between scenes
- True Mirror Glass Floor Reflections on all devices (mathematically multiplied alpha)
- Apple Keynote Floating Glass Feature Callout Cards with staggered ease-out cascades
- Vector Badges & 100% Font-Safe Unicode Rendering (zero glyph boxes)
- Tactile Touch Ripple Animation on "Unlock Pro" with Expanding Golden Ring
- Glowing Animated Cryptographic Bus Packet Stream
- Integrated Master Soundtrack (Ambient Electronic Tech Pad + Sub-Bass Groove + 7 Timed UI SFX + ElevenLabs Narration)
- Cinematic Fade-In & Fade-Out
"""

import math
import os
import subprocess
import sys

from PIL import Image, ImageDraw, ImageFilter, ImageFont, ImageMath

W, H = 1920, 1080
FPS = 30
DURATION = 96.04
TOTAL_FRAMES = int(DURATION * FPS)

ASSETS_DIR = "/home/k/Prototype/Kavach/assets/demo_screens"
AUDIO_PATH = "/home/k/Prototype/Kavach-demo-final/narration_cinematic_master.wav"
OUTPUT_PATH = "/home/k/Prototype/Kavach-demo-final/kavach-studio-master.mp4"
REPO_OUTPUT_PATH = "/home/k/Prototype/Kavach/assets/kavach-demo-2min.mp4"

# Load Fonts
FONT_BOLD = "/usr/share/fonts/truetype/liberation/LiberationSans-Bold.ttf"
FONT_REG = "/usr/share/fonts/truetype/liberation/LiberationSans-Regular.ttf"
FONT_DEV = "/usr/share/fonts/truetype/noto/NotoSansDevanagari-Bold.ttf"

font_logo = ImageFont.truetype(FONT_BOLD, 26)
font_dev = ImageFont.truetype(FONT_DEV, 24)
font_sub = ImageFont.truetype(FONT_REG, 15)
font_badge = ImageFont.truetype(FONT_BOLD, 13)
font_label = ImageFont.truetype(FONT_BOLD, 16)
font_caption = ImageFont.truetype(FONT_BOLD, 21)
font_caption_act = ImageFont.truetype(FONT_BOLD, 14)
font_chip_title = ImageFont.truetype(FONT_BOLD, 15)
font_chip_sub = ImageFont.truetype(FONT_REG, 14)

PW, PH = 440, 782
bezel = 10
total_pw = PW + bezel * 2
total_ph = PH + bezel * 2

# Easing utilities
def clamp(val, min_v=0.0, max_v=1.0):
    return max(min_v, min(max_v, val))

def ease_in_out_cubic(x):
    x = clamp(x)
    if x < 0.5:
        return 4.0 * x * x * x
    else:
        return 1.0 - math.pow(-2.0 * x + 2.0, 3) / 2.0

def ease_out_cubic(x):
    x = clamp(x)
    return 1.0 - math.pow(1.0 - x, 3)

def ease_out_back(x):
    x = clamp(x)
    c1 = 1.70158
    c3 = c1 + 1
    return 1.0 + c3 * math.pow(x - 1.0, 3) + c1 * math.pow(x - 1.0, 2)

# Floor reflection height & mask
refl_h = 150
refl_mask = Image.new("L", (total_pw, refl_h), 0)
rm_draw = ImageDraw.Draw(refl_mask)
for y in range(refl_h):
    alpha = int(140 * (1.0 - (y / refl_h) ** 0.8))
    rm_draw.line([(0, y), (total_pw, y)], fill=alpha)

# Pre-computed Gaussian-blurred shadow template
shadow_w, shadow_h = total_pw + 80, total_ph + 80
shadow_template = Image.new("RGBA", (shadow_w, shadow_h), (0, 0, 0, 0))
s_draw = ImageDraw.Draw(shadow_template)
s_draw.rounded_rectangle([(30, 35), (total_pw + 50, total_ph + 60)], radius=36, fill=(0, 0, 0, 220))
shadow_template = shadow_template.filter(ImageFilter.GaussianBlur(26))

# Screen Mask
screen_mask = Image.new("L", (PW, PH), 0)
mask_draw = ImageDraw.Draw(screen_mask)
mask_draw.rounded_rectangle([(0, 0), (PW, PH)], radius=24, fill=255)

# Load screens
def load_screen(name):
    p = os.path.join(ASSETS_DIR, name)
    return Image.open(p).convert("RGBA").resize((PW, PH), Image.Resampling.LANCZOS)

screen_cache = {
    "senior_idle": load_screen("senior_idle.png"),
    "senior_siren": load_screen("senior_siren.png"),
    "senior_intercepted": load_screen("senior_intercepted.png"),
    "family_home": load_screen("family_home.png"),
    "paywall_top": load_screen("paywall_top.png"),
    "paywall_judge": load_screen("paywall_judge.png"),
    "paywall_active": load_screen("paywall_active.png"),
}

# Pre-dim screens for inactive spotlight
dark_overlay = Image.new("RGBA", (PW, PH), (0, 0, 0, 115))
screen_dim_cache = {k: Image.alpha_composite(v, dark_overlay) for k, v in screen_cache.items()}

# Ambient Stage Aura Glows
def make_ambient_glow(center_x, center_y, radius, color):
    glow = Image.new("RGBA", (W, H), (0, 0, 0, 0))
    gdraw = ImageDraw.Draw(glow)
    gdraw.ellipse([(center_x - radius, center_y - radius), (center_x + radius, center_y + radius)], fill=color)
    return glow.filter(ImageFilter.GaussianBlur(95))

# Backdrop Grid & Header
base_canvas = Image.new("RGBA", (W, H), (8, 11, 19, 255))
base_draw = ImageDraw.Draw(base_canvas)
for y in range(0, H, 48):
    base_draw.line([(0, y), (W, y)], fill=(16, 22, 35, 255), width=1)
for x in range(0, W, 48):
    base_draw.line([(x, 0), (x, H)], fill=(16, 22, 35, 255), width=1)

base_draw.rectangle([(0, 0), (W, 76)], fill=(11, 15, 24, 250))
base_draw.line([(0, 76), (W, 76)], fill=(30, 41, 59, 255), width=2)
base_draw.text((40, 22), "Kavach |", fill=(255, 255, 255), font=font_logo)
base_draw.text((155, 22), "कवच", fill=(245, 158, 11), font=font_dev)
base_draw.text((230, 28), "Two-Sided Sovereign Fraud Defense", fill=(148, 163, 184), font=font_sub)

def draw_header_badge(draw_obj, x, y, text, border_col, text_col, bg_col):
    bbox = font_badge.getbbox(text)
    bw, bh = bbox[2] - bbox[0] + 24, bbox[3] - bbox[1] + 14
    draw_obj.rounded_rectangle([(x, y), (x + bw, y + bh)], radius=6, fill=bg_col, outline=border_col, width=1)
    draw_obj.text((x + 12, y + 6), text, fill=text_col, font=font_badge)
    return bw

bx = 1050
bx += draw_header_badge(base_draw, bx, 22, "REVENUECAT SHIPATON 2026 • NEXT GEN", (245, 158, 11), (253, 230, 138), (35, 26, 12)) + 16
draw_header_badge(base_draw, bx, 22, "E2E HARDWARE ENCRYPTED (GOOGLE TINK)", (16, 185, 129), (167, 243, 208), (12, 35, 25))

# Stage glow caches for fast rendering
glow_red_center = make_ambient_glow(480 + total_pw // 2, 120 + total_ph // 2, 280, (239, 68, 68, 42))
glow_green_center = make_ambient_glow(480 + total_pw // 2, 120 + total_ph // 2, 280, (16, 185, 129, 36))
glow_blue_right = make_ambient_glow(980 + total_pw // 2, 120 + total_ph // 2, 280, (59, 130, 246, 38))
glow_gold_right = make_ambient_glow(980 + total_pw // 2, 120 + total_ph // 2, 280, (245, 158, 11, 44))
glow_dual_split = make_ambient_glow(220 + total_pw // 2, 120 + total_ph // 2, 260, (16, 185, 129, 30))

stage_act1_calm = Image.alpha_composite(base_canvas, glow_green_center)
stage_act1_threat = Image.alpha_composite(base_canvas, glow_red_center)
stage_act2_siren = Image.alpha_composite(base_canvas, glow_red_center)
stage_act2_quar = Image.alpha_composite(base_canvas, glow_dual_split)
stage_act3_war = Image.alpha_composite(base_canvas, glow_blue_right)
stage_act5_gold = Image.alpha_composite(base_canvas, glow_gold_right)


def render_phone_object(screen_k, border_col, is_spotlight=True, glare_prog=0.0):
    """
    Renders an ultra-realistic smartphone chassis with bezel, screen, punch-hole camera,
    and a mathematically multiplied mirror floor reflection.
    """
    obj = Image.new("RGBA", (total_pw, total_ph + refl_h), (0, 0, 0, 0))
    odraw = ImageDraw.Draw(obj)
    
    bezel_fill = (22, 26, 36) if is_spotlight else (14, 17, 24)
    cur_border = border_col if is_spotlight else (42, 50, 65)
    b_width = 3 if is_spotlight else 1
    
    # Chassis
    odraw.rounded_rectangle([(0, 0), (total_pw, total_ph)], radius=32, fill=bezel_fill, outline=cur_border, width=b_width)
    if is_spotlight:
        odraw.rounded_rectangle([(2, 2), (total_pw - 2, total_ph - 2)], radius=30, fill=None, outline=(255, 255, 255, 45), width=1)
        
    # Screen
    if not is_spotlight:
        s = screen_dim_cache[screen_k]
    elif 0.0 < glare_prog < 1.0:
        s = screen_cache[screen_k].copy()
        glare_layer = Image.new("RGBA", (PW, PH), (0, 0, 0, 0))
        gdraw = ImageDraw.Draw(glare_layer)
        gx = int(-180 + glare_prog * (PW + 360))
        gdraw.polygon([(gx, 0), (gx + 70, 0), (gx - 130, PH), (gx - 200, PH)], fill=(255, 255, 255, 35))
        s = Image.alpha_composite(s, glare_layer)
    else:
        s = screen_cache[screen_k]
        
    obj.paste(s, (bezel, bezel), screen_mask)
    
    # Punch hole camera
    cam_x = total_pw // 2
    cam_y = bezel + 12
    odraw.ellipse([(cam_x - 5, cam_y - 5), (cam_x + 5, cam_y + 5)], fill=(5, 5, 5, 240), outline=(40, 40, 40), width=1)
    
    # Mirror floor reflection with multiplied alpha (zero rectangular artifact)
    refl_crop = obj.crop((0, total_ph - refl_h, total_pw, total_ph))
    refl_flip = refl_crop.transpose(Image.FLIP_TOP_BOTTOM)
    r_a = refl_flip.split()[3]
    combined_alpha = ImageMath.eval("convert(int(a) * int(b) / 255, 'L')", a=r_a, b=refl_mask)
    refl_flip.putalpha(combined_alpha)
    refl_flip = refl_flip.filter(ImageFilter.GaussianBlur(3))
    
    obj.alpha_composite(refl_flip, (0, total_ph))
    return obj


def get_phone_positions(t):
    """
    Computes continuous coordinates (px) for Left and Right phones with smooth easing.
    Eliminates all abrupt teleportations or sudden hard cuts.
    """
    if t < 20.0:
        # Act 1 & 2a: Left phone centered hero at 480, Right phone offscreen
        left_x = 480
        right_x = 1960
    elif t < 29.0:
        # Transition 20.0 - 20.8s: Left glides 480 -> 220, Right glides 1960 -> 1260
        p = ease_in_out_cubic((t - 20.0) / 0.8)
        left_x = int(480 + (220 - 480) * p)
        right_x = int(1960 + (1260 - 1960) * p)
    elif t < 47.8:
        # Transition 29.0 - 29.8s: Left glides 220 -> -520, Right glides 1260 -> 980
        p = ease_in_out_cubic((t - 29.0) / 0.8)
        left_x = int(220 + (-520 - 220) * p)
        right_x = int(1260 + (980 - 1260) * p)
    elif t < 59.6:
        # Transition 47.8 - 48.6s: Left glides -520 -> 220, Right glides 980 -> 1260
        p = ease_in_out_cubic((t - 47.8) / 0.8)
        left_x = int(-520 + (220 - (-520)) * p)
        right_x = int(980 + (1260 - 980) * p)
    elif t < 85.9:
        # Transition 59.6 - 60.4s: Left glides 220 -> -520, Right glides 1260 -> 980
        p = ease_in_out_cubic((t - 59.6) / 0.8)
        left_x = int(220 + (-520 - 220) * p)
        right_x = int(1260 + (980 - 1260) * p)
    else:
        # Transition 85.9 - 86.7s: Left glides -520 -> 220, Right glides 980 -> 1260
        p = ease_in_out_cubic((t - 85.9) / 0.8)
        left_x = int(-520 + (220 - (-520)) * p)
        right_x = int(980 + (1260 - 980) * p)
        
    return left_x, right_x


def draw_cascading_card(frame, cx, cy, cw, ch, title, desc, col_border, col_sub, col_bg, progress, is_right_side, phone_edge_x):
    """
    Renders a frosted glass feature card with staggered ease-out slide and connecting line.
    """
    if progress <= 0.0:
        return
        
    ease = ease_out_cubic(progress)
    alpha_mul = ease
    
    slide_dist = 30
    if is_right_side:
        cur_cx = cx + int(slide_dist * (1.0 - ease))
    else:
        cur_cx = cx - int(slide_dist * (1.0 - ease))
        
    card = Image.new("RGBA", (cw, ch), (0, 0, 0, 0))
    cdraw = ImageDraw.Draw(card)
    
    bg_a = int(col_bg[3] * alpha_mul)
    border_a = int(255 * alpha_mul)
    
    cdraw.rounded_rectangle([(0, 0), (cw, ch)], radius=16, fill=(col_bg[0], col_bg[1], col_bg[2], bg_a), outline=(col_border[0], col_border[1], col_border[2], border_a), width=2)
    cdraw.text((24, 16), title, fill=(col_border[0], col_border[1], col_border[2], border_a), font=font_chip_title)
    cdraw.text((24, 44), desc, fill=(col_sub[0], col_sub[1], col_sub[2], border_a), font=font_sub)
    
    frame.alpha_composite(card, (cur_cx, cy))
    
    # Connecting lead line & glowing dot
    fdraw = ImageDraw.Draw(frame)
    line_y = cy + ch // 2
    if is_right_side:
        line_start = phone_edge_x + 20
        line_end = cur_cx - 10
        cur_line_len = int((line_end - line_start) * ease)
        if cur_line_len > 0:
            fdraw.line([(line_start, line_y), (line_start + cur_line_len, line_y)], fill=(col_border[0], col_border[1], col_border[2], int(150 * alpha_mul)), width=2)
            dot_x = line_start + cur_line_len
            fdraw.ellipse([(dot_x - 4, line_y - 4), (dot_x + 4, line_y + 4)], fill=(col_border[0], col_border[1], col_border[2], border_a))
    else:
        line_start = cur_cx + cw + 10
        line_end = phone_edge_x - 20
        cur_line_len = int((line_end - line_start) * ease)
        if cur_line_len > 0:
            fdraw.line([(line_start, line_y), (line_start + cur_line_len, line_y)], fill=(col_border[0], col_border[1], col_border[2], int(150 * alpha_mul)), width=2)
            dot_x = line_start + cur_line_len
            fdraw.ellipse([(dot_x - 4, line_y - 4), (dot_x + 4, line_y + 4)], fill=(col_border[0], col_border[1], col_border[2], border_a))


def render_frame(t):
    # Organic floating
    dy = int(math.sin(t * 1.5) * 5)
    phone_y = 120 + dy
    
    left_x, right_x = get_phone_positions(t)

    # Determine Scene Stage Backdrop
    if t < 12.2:
        active_stage = stage_act1_threat if t >= 5.5 else stage_act1_calm
        act_label = "ACT 1: THE CRISIS & TWO-SIDED HOUSEHOLD DEFENSE"
        act_col = (245, 158, 11)
        sub_text = "Eleven forty AM. Your mother's phone lights up: \"Bank account FROZEN. Share OTP now.\""
    elif t < 20.0:
        active_stage = stage_act2_siren
        act_label = "ACT 2: ON-DEVICE SCAM LAB & INSTANT THREAT QUARANTINE"
        act_col = (239, 68, 68)
        sub_text = "Ruko! OTP mat do! Unless Kavach is on her phone. The SMS never buzzes."
    elif t < 29.0:
        active_stage = stage_act2_quar
        act_label = "ACT 2: ON-DEVICE SCAM LAB & INSTANT THREAT QUARANTINE"
        act_col = (16, 185, 129)
        sub_text = "The SMS never buzzes. Silent quarantine on-device. The relay holds only ciphertext."
    elif t < 47.8:
        active_stage = stage_act3_war
        act_label = "ACT 3: THE FAMILY WAR-ROOM & ANDROID KEYSTORE LINK"
        act_col = (59, 130, 246)
        sub_text = "The Family War-Room: Safety Score 100, two devices keystore-sealed. The server sees only noise."
    elif t < 59.6:
        active_stage = stage_act2_quar
        act_label = "ACT 4: PRE-RING CALL TERMINATION & COMMUNITY BLOCKLIST"
        act_col = (16, 185, 129)
        sub_text = "Wahi number calls back - the phone kills it before the first ring. The relay holds only ciphertext."
    elif t < 85.9:
        active_stage = stage_act5_gold
        act_label = "ACT 5: REVENUECAT MULTI-SEAT MONETIZATION & SHIPATON PROMO"
        act_col = (245, 158, 11)
        sub_text = "Kavach learns every morning: signed rules + community shield. Family Fortress $79.99/yr via RevenueCat."
    else:
        active_stage = stage_act5_gold
        act_label = "ACT 6: DIGNIFIED DEFENSE FOR OUR PARENTS"
        act_col = (16, 185, 129)
        sub_text = "Protection for those who cannot verify. Proof for those who can. Kavach - your shield."

    frame = active_stage.copy()
    draw = ImageDraw.Draw(frame)

    # 1. RENDER LEFT PHONE (Mother's Phone) if visible
    if left_x + total_pw > -100 and left_x < W + 100:
        frame.alpha_composite(shadow_template, (left_x - 40, phone_y - 25))
        
        # Screen selection & border
        if t < 12.2:
            s_key = "senior_idle"
            b_col = (239, 68, 68) if t >= 5.5 else (16, 185, 129)
            glare = min(1.0, max(0.0, (t - 5.5) / 1.0)) if t >= 5.5 else 0.0
            is_spot = True
        elif t < 20.0:
            s_key = "senior_siren"
            b_col = (239, 68, 68)
            glare = min(1.0, max(0.0, (t - 12.2) / 1.0))
            is_spot = True
        elif t < 29.0:
            s_key = "senior_intercepted"
            b_col = (16, 185, 129)
            glare = min(1.0, max(0.0, (t - 20.0) / 1.0))
            is_spot = True
        elif t < 47.8:
            s_key = "senior_idle"
            b_col = (16, 185, 129)
            glare = 0.0
            is_spot = False
        elif t < 59.6:
            s_key = "senior_idle"
            b_col = (16, 185, 129)
            glare = min(1.0, max(0.0, (t - 47.8) / 1.0))
            is_spot = True
        elif t < 85.9:
            s_key = "senior_idle"
            b_col = (16, 185, 129)
            glare = 0.0
            is_spot = False
        else:
            s_key = "senior_idle"
            b_col = (16, 185, 129)
            glare = min(1.0, max(0.0, (t - 85.9) / 1.0))
            is_spot = True
            
        p_left = render_phone_object(s_key, b_col, is_spotlight=is_spot, glare_prog=glare)
        frame.alpha_composite(p_left, (left_x, phone_y))
        
        # Phone label
        if -50 < left_x < W:
            draw.text((left_x + 16, phone_y - 32), "MOTHER'S PHONE", fill=(255, 255, 255), font=font_label)
            sub_lbl = "Senior Sanctuary Fortified" if t >= 85.9 else "Senior Sanctuary"
            draw.text((left_x + 220, phone_y - 30), sub_lbl, fill=(148, 163, 184), font=font_sub)

        # Act 1: Dropdown SMS Alert Notification
        if 5.5 <= t < 12.2:
            drop_prog = clamp((t - 5.5) / 0.4)
            drop_y = phone_y + int(110 + 50 * ease_out_back(drop_prog))
            bx = left_x + 30
            sms_box = Image.new("RGBA", (PW - 40, 92), (0, 0, 0, 0))
            sdraw = ImageDraw.Draw(sms_box)
            sdraw.rounded_rectangle([(0, 0), (PW - 40, 92)], radius=12, fill=(28, 14, 18, 245), outline=(239, 68, 68), width=2)
            sdraw.text((16, 12), "ALERT: INCOMING SCAM SMS", fill=(248, 113, 113), font=font_badge)
            sdraw.text((16, 34), "\"Bank account FROZEN. Share OTP now.\"", fill=(255, 255, 255), font=font_caption_act)
            sdraw.text((16, 62), "Sender: +91-98XXX-BANK1", fill=(203, 213, 225), font=font_sub)
            frame.alpha_composite(sms_box, (bx, drop_y))

        # Act 4: Dropdown Call Termination HUD (NO MISSING GLYPH!)
        if 49.0 <= t < 59.6:
            drop_prog = clamp((t - 49.0) / 0.4)
            drop_y = phone_y + int(110 + 50 * ease_out_back(drop_prog))
            cx_call = left_x + 30
            call_box = Image.new("RGBA", (PW - 40, 92), (0, 0, 0, 0))
            cdraw = ImageDraw.Draw(call_box)
            cdraw.rounded_rectangle([(0, 0), (PW - 40, 92)], radius=12, fill=(28, 14, 18, 245), outline=(239, 68, 68), width=2)
            cdraw.text((16, 12), "CALLSCREENING: INCOMING SCAM CALL", fill=(248, 113, 113), font=font_badge)
            
            # Vector Red Circle with sharp white X badge (NO UNICODE GLYPH RELIANCE)
            badge_x, badge_y = 16, 35
            cdraw.ellipse([(badge_x, badge_y), (badge_x + 16, badge_y + 16)], fill=(239, 68, 68))
            cdraw.line([(badge_x + 4, badge_y + 4), (badge_x + 12, badge_y + 12)], fill=(255, 255, 255), width=2)
            cdraw.line([(badge_x + 4, badge_y + 12), (badge_x + 12, badge_y + 4)], fill=(255, 255, 255), width=2)
            
            cdraw.text((badge_x + 24, 34), "TERMINATED PRE-RING (0 RINGS)", fill=(255, 255, 255), font=font_caption_act)
            cdraw.text((16, 62), "Caller: +91-98XXX-BANK1 (Learned Hash)", fill=(203, 213, 225), font=font_sub)
            frame.alpha_composite(call_box, (cx_call, drop_y))

    # 2. RENDER RIGHT PHONE (Child's Console / Paywall) if visible
    if right_x + total_pw > -100 and right_x < W + 100:
        frame.alpha_composite(shadow_template, (right_x - 40, phone_y - 25))
        
        # Screen selection & border
        if t < 29.0:
            s_key = "family_home"
            b_col = (59, 130, 246)
            glare = 0.0
            is_spot = False
        elif t < 47.8:
            s_key = "family_home"
            b_col = (59, 130, 246)
            glare = min(1.0, max(0.0, (t - 29.0) / 1.0))
            is_spot = True
        elif t < 59.6:
            s_key = "senior_intercepted"
            b_col = (59, 130, 246)
            glare = min(1.0, max(0.0, (t - 47.8) / 1.0))
            is_spot = True
        elif t < 85.9:
            if t < 70.0:
                s_key = "paywall_top"
                glare = min(1.0, max(0.0, (t - 59.6) / 1.0))
            elif t < 75.0:
                s_key = "paywall_judge"
                glare = min(1.0, max(0.0, (t - 70.0) / 1.0))
            else:
                s_key = "paywall_active"
                glare = min(1.0, max(0.0, (t - 75.0) / 1.0))
            b_col = (245, 158, 11)
            is_spot = True
        else:
            s_key = "paywall_active"
            b_col = (245, 158, 11)
            glare = min(1.0, max(0.0, (t - 85.9) / 1.0))
            is_spot = True
            
        p_right = render_phone_object(s_key, b_col, is_spotlight=is_spot, glare_prog=glare)
        frame.alpha_composite(p_right, (right_x, phone_y))
        
        # Phone label
        if -50 < right_x < W:
            right_title = "SECURITY AUDIT" if 47.8 <= t < 59.6 else "CHILD'S CONSOLE"
            draw.text((right_x + 16, phone_y - 32), right_title, fill=(255, 255, 255), font=font_label)
            if 47.8 <= t < 59.6:
                r_sub = "Threat Ledger"
            elif 59.6 <= t < 85.9:
                r_sub = "RevenueCat Paywall"
            elif t >= 85.9:
                r_sub = "Pro Family Shield Active"
            else:
                r_sub = "Guardian War-Room"
            draw.text((right_x + 220, phone_y - 30), r_sub, fill=(148, 163, 184), font=font_sub)

        # Act 5: Interactive Tactile Touch on "Unlock Pro" Button
        if 73.5 <= t <= 75.8:
            tap_prog = (t - 73.5) / 2.3
            tx = right_x + bezel + 362
            ty = phone_y + bezel + 665
            
            # Expanding golden ripples
            r1 = int(10 + tap_prog * 36)
            alpha_r1 = int(255 * max(0.0, 1.0 - tap_prog))
            ripple_overlay = Image.new("RGBA", (W, H), (0, 0, 0, 0))
            rdraw = ImageDraw.Draw(ripple_overlay)
            rdraw.ellipse([(tx - r1, ty - r1), (tx + r1, ty + r1)], outline=(255, 215, 0, alpha_r1), width=3)
            rdraw.ellipse([(tx - 6, ty - 6), (tx + 6, ty + 6)], fill=(255, 215, 0, 240))
            frame.alpha_composite(ripple_overlay)

    # 3. FEATURE CARDS & CENTER BRIDGES
    if t < 12.2:
        # Act 1 Cards on right
        cards = [
            ("THREAT INTERCEPTION", "Bank Impersonation Urgency Lure", (239, 68, 68), (254, 202, 202), (15, 21, 33, 240)),
            ("WCAG AAA ACCESSIBILITY", "64dp Touch Targets • Bilingual Hindi/EN", (16, 185, 129), (167, 243, 208), (15, 21, 33, 240)),
            ("SOVEREIGN ZERO-CLOUD", "On-Device Rule Engine • 0 Audio Leaks", (59, 130, 246), (191, 219, 254), (15, 21, 33, 240)),
            ("TWO-SIDED DEFENSE", "Parent Sanctuary <-> Guardian War-Room", (245, 158, 11), (253, 230, 138), (15, 21, 33, 240)),
        ]
        cy = phone_y + 90
        for i, (title, desc, col_border, col_sub, col_bg) in enumerate(cards):
            card_start = 0.3 + i * 0.18
            prog = clamp((t - card_start) / 0.4)
            draw_cascading_card(frame, 1040, cy, 580, 82, title, desc, col_border, col_sub, col_bg, prog, True, left_x + total_pw)
            cy += 120

    elif t < 20.0:
        # Act 2a Siren Cards on right
        siren_cards = [
            ("CRITICAL: LIVE ATTACK", "Urgent Bank Account Frozen Threat", (239, 68, 68), (254, 202, 202), (28, 14, 18, 240)),
            ("SENIOR SIREN ACTIVATED", "Immediate Full-Screen RUKO Alarm", (239, 68, 68), (254, 202, 202), (28, 14, 18, 240)),
            ("64DP AAA TOUCH TARGETS", "WCAG Compliant Massive Touch Targets", (16, 185, 129), (167, 243, 208), (28, 14, 18, 240)),
            ("BILINGUAL AUDIO GUIDANCE", "Clear Spoken Guidance: Hindi & English", (245, 158, 11), (253, 230, 138), (28, 14, 18, 240)),
        ]
        cy = phone_y + 90
        for i, (title, desc, col_border, col_sub, col_bg) in enumerate(siren_cards):
            card_start = 12.2 + i * 0.18
            prog = clamp((t - card_start) / 0.4)
            draw_cascading_card(frame, 1040, cy, 580, 82, title, desc, col_border, col_sub, col_bg, prog, True, left_x + total_pw)
            cy += 120

    elif t < 29.0:
        # Act 2b: Central Bridge Quarantined & Bus Wire
        bridge_prog = clamp((t - 20.0) / 0.6)
        if bridge_prog > 0.0:
            center_x = (left_x + total_pw + right_x) // 2
            bridge_y = phone_y + 240
            bw = 155
            
            b_alpha = int(240 * ease_out_cubic(bridge_prog))
            bridge_card = Image.new("RGBA", (bw * 2, 190), (0, 0, 0, 0))
            bdraw = ImageDraw.Draw(bridge_card)
            bdraw.rounded_rectangle([(0, 0), (bw * 2, 190)], radius=16, fill=(12, 30, 22, b_alpha), outline=(16, 185, 129, b_alpha), width=2)
            bdraw.text((bw - 110, 18), "SHIELD: ATTACK QUARANTINED", fill=(52, 211, 153, b_alpha), font=font_badge)
            items = [
                ("• Verdict: SCAM INTERCEPTED", (52, 211, 153)),
                ("• Senior Screen: 100% QUIET", (52, 211, 153)),
                ("• Encrypted Vault: Stored", (203, 213, 225)),
                ("• Sender Hash: Auto-Learned", (253, 230, 138)),
            ]
            iy = 50
            for txt, col in items:
                bdraw.text((bw - 135, iy), txt, fill=(col[0], col[1], col[2], b_alpha), font=font_sub)
                iy += 28
            frame.alpha_composite(bridge_card, (center_x - bw, bridge_y))
            
            # Connecting bus wire & animated glowing packet
            bus_y = bridge_y + 95
            draw.line([(left_x + total_pw, bus_y), (center_x - bw, bus_y)], fill=(37, 50, 75, 200), width=2)
            draw.line([(center_x + bw, bus_y), (right_x, bus_y)], fill=(37, 50, 75, 200), width=2)
            
            cycle = (t * 1.6) % 2.0
            if cycle < 1.0:
                pkt_x = int(left_x + total_pw + cycle * (center_x - bw - (left_x + total_pw)))
            else:
                pkt_x = int(center_x + bw + (cycle - 1.0) * (right_x - (center_x + bw)))
            draw.ellipse([(pkt_x - 7, bus_y - 7), (pkt_x + 7, bus_y + 7)], fill=(16, 185, 129))
            draw.ellipse([(pkt_x - 3, bus_y - 3), (pkt_x + 3, bus_y + 3)], fill=(255, 255, 255))

    elif t < 47.8:
        # Act 3: War-Room Feature Cards on left
        war_cards = [
            ("SAFETY SCORE 100 INDEX", "Fortified Household • 0 Cloud Leaks", (16, 185, 129), (167, 243, 208), (15, 23, 42, 240)),
            ("ANDROID KEYSTORE ENCLAVE", "Google Tink ECIES-P256 Hardware Sealed", (59, 130, 246), (191, 219, 254), (15, 23, 42, 240)),
            ("MUTUAL SAS VERIFICATION", "6-Emoji Visual Cryptographic Fingerprint", (245, 158, 11), (253, 230, 138), (15, 23, 42, 240)),
            ("MASKED OTP PRIVACY VAULT", "Incoming SMS OTPs Masked on Device", (203, 213, 225), (241, 245, 249), (15, 23, 42, 240)),
        ]
        cy = phone_y + 90
        for i, (title, desc, col_border, col_sub, col_bg) in enumerate(war_cards):
            card_start = 29.5 + i * 0.18
            prog = clamp((t - card_start) / 0.4)
            draw_cascading_card(frame, 320, cy, 580, 82, title, desc, col_border, col_sub, col_bg, prog, False, right_x)
            cy += 120

    elif t < 59.6:
        # Act 4: Screening Pre-Ring Bridge
        bridge_prog = clamp((t - 47.8) / 0.6)
        if bridge_prog > 0.0:
            center_x = (left_x + total_pw + right_x) // 2
            bridge_y = phone_y + 240
            bw = 155
            
            b_alpha = int(240 * ease_out_cubic(bridge_prog))
            bridge_card = Image.new("RGBA", (bw * 2, 190), (0, 0, 0, 0))
            bdraw = ImageDraw.Draw(bridge_card)
            bdraw.rounded_rectangle([(0, 0), (bw * 2, 190)], radius=16, fill=(12, 30, 22, b_alpha), outline=(16, 185, 129, b_alpha), width=2)
            bdraw.text((bw - 110, 18), "SCREENING: PRE-RING DEFENSE", fill=(52, 211, 153, b_alpha), font=font_badge)
            items = [
                ("• CallScreeningService: ACTIVE", (52, 211, 153)),
                ("• Repeat Scammer: KILLED PRE-RING", (248, 113, 113)),
                ("• Senior Ring Disturbance: 0 RINGS", (52, 211, 153)),
                ("• Household Sync: SHA-256 Hash", (253, 230, 138)),
            ]
            iy = 50
            for txt, col in items:
                bdraw.text((bw - 135, iy), txt, fill=(col[0], col[1], col[2], b_alpha), font=font_sub)
                iy += 28
            frame.alpha_composite(bridge_card, (center_x - bw, bridge_y))

    elif t < 85.9:
        # Act 5: RevenueCat Feature Cards on left
        rc_cards = [
            ("REVENUECAT MULTI-SEAT PRO", "1 Subscription Protects 3 Parent Devices", (245, 158, 11), (254, 243, 199), (35, 26, 12, 240)),
            ("FAMILY FORTRESS ANNUAL", "$79.99/yr • 7-Day Free Trial Available", (245, 158, 11), (254, 243, 199), (35, 26, 12, 240)),
            ("SHIPATON JUDGE PROMO", "Code SHIPATON-JUDGE Unlocks Full Pro", (52, 211, 153), (167, 243, 208), (35, 26, 12, 240)),
            ("PRO ENTITLED ACTIVE", "Daily Threat Intel + Signed Rule Updates", (52, 211, 153), (167, 243, 208), (35, 26, 12, 240)),
        ]
        cy = phone_y + 90
        for i, (title, desc, col_border, col_sub, col_bg) in enumerate(rc_cards):
            card_start = 60.0 + i * 0.18
            prog = clamp((t - card_start) / 0.4)
            draw_cascading_card(frame, 320, cy, 580, 82, title, desc, col_border, col_sub, col_bg, prog, False, right_x)
            cy += 120

    else:
        # Act 6: Center Award Presentation Plaque
        plaque_prog = clamp((t - 85.9) / 0.7)
        if plaque_prog > 0.0:
            center_x = (left_x + total_pw + right_x) // 2
            bridge_y = phone_y + 230
            bw = 180
            
            p_alpha = int(245 * ease_out_cubic(plaque_prog))
            plaque = Image.new("RGBA", (bw * 2, 200), (0, 0, 0, 0))
            pdraw = ImageDraw.Draw(plaque)
            pdraw.rounded_rectangle([(0, 0), (bw * 2, 200)], radius=18, fill=(16, 26, 38, p_alpha), outline=(245, 158, 11, p_alpha), width=2)
            pdraw.rounded_rectangle([(bw - 115, 14), (bw + 115, 36)], radius=6, fill=(45, 32, 14, p_alpha), outline=(245, 158, 11, p_alpha), width=1)
            pdraw.text((bw - 98, 18), "KAVACH SHIPATON 2026", fill=(253, 230, 138, p_alpha), font=font_badge)
            pdraw.line([(24, 44), (bw * 2 - 24, 44)], fill=(245, 158, 11, int(180 * (p_alpha / 245))), width=1)
            finale_items = [
                ("• RevenueCat Shipaton 2026 Entry", (254, 243, 199)),
                ("• Award Track: Next Gen Winner", (253, 230, 138)),
                ("• krishivjoshi219-collab/Kavach", (147, 197, 253)),
                ("• Two-Sided Sovereign Fraud Defense", (52, 211, 153)),
            ]
            iy = 56
            for txt, col in finale_items:
                pdraw.text((bw - 150, iy), txt, fill=(col[0], col[1], col[2], p_alpha), font=font_sub)
                iy += 28
            frame.alpha_composite(plaque, (center_x - bw, bridge_y))

    # 4. APPLE KEYNOTE FROSTED GLASS SUBTITLE PILL
    sub_box = [(220, 965), (1700, 1045)]
    draw.rounded_rectangle(sub_box, radius=16, fill=(12, 17, 28, 245), outline=(45, 58, 80), width=1)
    
    # Glowing status dot
    dot_x, dot_y = 248, 1018
    draw.ellipse([(dot_x - 4, dot_y - 4), (dot_x + 4, dot_y + 4)], fill=act_col)
    draw.text((262, 1010), act_label, fill=act_col, font=font_caption_act)
    draw.text((248, 978), sub_text, fill=(255, 255, 255), font=font_caption)

    # 5. HAIRLINE PROGRESS BAR WITH GLOWING TIP
    bar_w = int(W * min(1.0, t / DURATION))
    draw.line([(0, H - 4), (bar_w, H - 4)], fill=(245, 158, 11), width=4)
    if bar_w > 0:
        draw.ellipse([(bar_w - 4, H - 7), (bar_w + 4, H - 1)], fill=(255, 255, 255))

    # 6. CINEMATIC INTRO FADE-IN & OUTRO FADE-OUT
    if t < 0.8:
        fade = 1.0 - (t / 0.8)
        black_layer = Image.new("RGBA", (W, H), (0, 0, 0, int(255 * fade)))
        frame = Image.alpha_composite(frame, black_layer)
    elif t > 94.5:
        fade = min(1.0, (t - 94.5) / 1.54)
        black_layer = Image.new("RGBA", (W, H), (0, 0, 0, int(255 * fade)))
        frame = Image.alpha_composite(frame, black_layer)

    return frame


def main():
    print(f"Starting cinematic studio render: {TOTAL_FRAMES} frames @ {FPS} fps ({DURATION:.2f}s)...")
    
    ffmpeg_cmd = [
        "ffmpeg", "-y",
        "-f", "rawvideo",
        "-vcodec", "rawvideo",
        "-s", f"{W}x{H}",
        "-pix_fmt", "rgba",
        "-r", str(FPS),
        "-i", "-",
        "-i", AUDIO_PATH,
        "-c:v", "libx264",
        "-preset", "fast",
        "-crf", "18",
        "-pix_fmt", "yuv420p",
        "-c:a", "aac",
        "-b:a", "192k",
        "-shortest",
        OUTPUT_PATH
    ]
    
    proc = subprocess.Popen(ffmpeg_cmd, stdin=subprocess.PIPE)
    
    try:
        for f in range(TOTAL_FRAMES):
            t = f / FPS
            img = render_frame(t)
            proc.stdin.write(img.tobytes())
            if f % 150 == 0:
                print(f"Rendered frame {f}/{TOTAL_FRAMES} ({t:.1f}s / {DURATION:.1f}s)...")
        proc.stdin.close()
        proc.wait()
    except Exception as e:
        proc.kill()
        raise e

    if proc.returncode != 0:
        print(f"FFmpeg failed with return code {proc.returncode}")
        sys.exit(1)

    print(f"Render complete! Output: {OUTPUT_PATH}")
    os.makedirs(os.path.dirname(REPO_OUTPUT_PATH), exist_ok=True)
    subprocess.run(["cp", "-f", OUTPUT_PATH, REPO_OUTPUT_PATH], check=True)
    print(f"Copied to repo assets: {REPO_OUTPUT_PATH}")


if __name__ == "__main__":
    main()
