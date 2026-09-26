#!/usr/bin/env python3
"""
Kavach Cinematic Audio Generator
Synthesizes a bespoke ambient electronic tech soundtrack with sidechain sub-bass groove,
harmonic synth pads, and 7 precisely timed UI sound effects (SFX), then mixes with ElevenLabs narration.
"""

import math
import struct
import subprocess
import wave

AUDIO_IN = "/home/k/Prototype/Kavach-demo-final/narration.mp3"
AUDIO_OUT = "/home/k/Prototype/Kavach-demo-final/narration_cinematic_master.wav"

sample_rate = 44100
duration = 96.04
n_samples = int(sample_rate * duration)

print("Synthesizing ambient tech soundscape and UI SFX...")

# Sound effect trigger times (sec)
sfx_events = [
    (5.5, "sms_ping"),
    (12.2, "siren_alert"),
    (20.0, "vault_lock"),
    (30.0, "keystore_chime"),
    (50.5, "call_reject"),
    (74.2, "tap_click"),
    (75.0, "pro_fanfare"),
]

# Chord progression (80 BPM, 4 beats per bar = 3.0s per bar)
# Dm9 -> Bbmaj7 -> Fmaj9 -> Cadd9
chords = [
    [146.83, 174.61, 220.00, 261.63, 329.63], # Dm9
    [116.54, 174.61, 220.00, 233.08, 349.23], # Bbmaj7
    [174.61, 220.00, 261.63, 329.63, 392.00], # Fmaj9
    [130.81, 164.81, 196.00, 261.63, 293.66], # Cadd9
]

def get_chord_freqs(t):
    bar_idx = int(t / 6.0) % len(chords)
    return chords[bar_idx]

music_buffer = [0.0] * n_samples

for i in range(n_samples):
    t = i / sample_rate
    chord = get_chord_freqs(t)
    
    # Warm pad sound with gentle detune chorus
    pad = 0.0
    for f in chord:
        pad += math.sin(2 * math.pi * f * t) * 0.045
        pad += math.sin(2 * math.pi * f * 1.002 * t) * 0.025
        pad += math.sin(2 * math.pi * (f * 2.0) * t) * 0.018
        
    # Sub-bass root note (octave below)
    root = chord[0] * 0.5
    sub = math.sin(2 * math.pi * root * t) * 0.065
    
    # 80 BPM gentle sidechain pulse (1.333 Hz)
    pulse = 0.75 + 0.25 * math.sin(2 * math.pi * 1.3333 * t)
    
    # Volume envelope (fade in at start, fade out at end)
    env = 1.0
    if t < 2.0:
        env = t / 2.0
    elif t > 94.0:
        env = max(0.0, (96.04 - t) / 2.04)
        
    music_buffer[i] = (pad * pulse + sub) * env * 0.35

# Synthesize SFX and mix in
for evt_t, evt_type in sfx_events:
    start_idx = int(evt_t * sample_rate)
    
    if evt_type == "sms_ping":
        dur = 0.4
        for s in range(int(dur * sample_rate)):
            st = s / sample_rate
            idx = start_idx + s
            if idx < n_samples:
                chime = (math.sin(2 * math.pi * 880 * st) + math.sin(2 * math.pi * 1318 * st)) * math.exp(-st * 12) * 0.16
                music_buffer[idx] += chime
                
    elif evt_type == "siren_alert":
        dur = 2.0
        for s in range(int(dur * sample_rate)):
            st = s / sample_rate
            idx = start_idx + s
            if idx < n_samples:
                freq = 240 + 80 * math.sin(2 * math.pi * 3.0 * st)
                rumble = math.sin(2 * math.pi * freq * st) * math.exp(-st * 1.5) * 0.20
                music_buffer[idx] += rumble
                
    elif evt_type == "vault_lock":
        dur = 0.3
        for s in range(int(dur * sample_rate)):
            st = s / sample_rate
            idx = start_idx + s
            if idx < n_samples:
                click = math.sin(2 * math.pi * 600 * st) * math.exp(-st * 25) * 0.22
                music_buffer[idx] += click
                
    elif evt_type == "keystore_chime":
        dur = 0.8
        for s in range(int(dur * sample_rate)):
            st = s / sample_rate
            idx = start_idx + s
            if idx < n_samples:
                chime = (math.sin(2 * math.pi * 1046 * st) + math.sin(2 * math.pi * 1568 * st)) * math.exp(-st * 6) * 0.14
                music_buffer[idx] += chime
                
    elif evt_type == "call_reject":
        dur = 0.25
        for s in range(int(dur * sample_rate)):
            st = s / sample_rate
            idx = start_idx + s
            if idx < n_samples:
                drop = math.sin(2 * math.pi * 420 * st) * math.exp(-st * 20) * 0.20
                music_buffer[idx] += drop
                
    elif evt_type == "tap_click":
        dur = 0.15
        for s in range(int(dur * sample_rate)):
            st = s / sample_rate
            idx = start_idx + s
            if idx < n_samples:
                tap = math.sin(2 * math.pi * 180 * st) * math.exp(-st * 35) * 0.28
                music_buffer[idx] += tap
                
    elif evt_type == "pro_fanfare":
        dur = 2.5
        for s in range(int(dur * sample_rate)):
            st = s / sample_rate
            idx = start_idx + s
            if idx < n_samples:
                shimmer = 0.0
                for f_note, delay in [(523.25, 0.0), (659.25, 0.1), (783.99, 0.2), (1046.50, 0.3), (1318.51, 0.4)]:
                    if st >= delay:
                        t_rel = st - delay
                        shimmer += math.sin(2 * math.pi * f_note * t_rel) * math.exp(-t_rel * 4) * 0.10
                music_buffer[idx] += shimmer

temp_music_wav = "/tmp/music_sfx.wav"
with wave.open(temp_music_wav, 'w') as wav:
    wav.setnchannels(2)
    wav.setsampwidth(2)
    wav.setframerate(sample_rate)
    frames = bytearray()
    for sig in music_buffer:
        val = int(max(-1.0, min(1.0, sig)) * 32767)
        frames.extend(struct.pack('<hh', val, val))
    wav.writeframes(frames)

print(f"Music & SFX track written to {temp_music_wav}. Merging with narration...")

mix_cmd = [
    "ffmpeg", "-y",
    "-i", AUDIO_IN,
    "-i", temp_music_wav,
    "-filter_complex", "[0:a]volume=1.05[a0];[1:a]volume=0.38[a1];[a0][a1]amix=inputs=2:duration=first:dropout_transition=2[aout]",
    "-map", "[aout]",
    "-c:a", "pcm_s16le",
    AUDIO_OUT
]
subprocess.run(mix_cmd, check=True)
print(f"Master soundtrack generated successfully: {AUDIO_OUT}")

if __name__ == "__main__":
    pass
