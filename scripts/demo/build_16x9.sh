#!/bin/bash
# 16:9 demo assembly: animated story cards (left) + live phone PiP (right).
# Inputs: /tmp/opencode/cards/cardN.png, /tmp/opencode/video_cut.mp4 (phone),
#         /tmp/opencode/vo/narration.mp3, /tmp/opencode/wide.en.srt
# Output: /tmp/opencode/kavach-16x9-FINAL.mp4 (1920x1080, <120s)
# Lesson encoded here: overlay NEVER expands the canvas — pad the base first.
set -euo pipefail
OUT=${1:-/tmp/opencode/kavach-16x9-FINAL.mp4}

# 1. Left panel: cards with slow zoom + 0.4s crossfades, timed to narration acts.
python3 - <<'PYEOF'
durs = [12.26, 16.81, 18.76, 11.84, 26.28, 10.08]
XD = 0.4
parts = []
for i, d in enumerate(durs):
    D = int((d + XD) * 30)
    parts.append(f"[{i}:v]scale=1313:1080,zoompan=z='min(zoom+0.0008,1.07)':d={D}:s=1313x1080:fps=30,setpts=PTS-STARTPTS[c{i}]")
off = durs[0] - XD
parts.append(f"[c0][c1]xfade=transition=fade:duration={XD}:offset={off:.2f}[x1]")
for i in range(2, 6):
    off = off + durs[i-1] - XD
    out = "left" if i == 5 else f"x{i}"
    parts.append(f"[x{i-1}][c{i}]xfade=transition=fade:duration={XD}:offset={off:.2f}[{out}]")
open("/tmp/opencode/left_fc.txt", "w").write(";".join(parts))
PYEOF
FC=$(cat /tmp/opencode/left_fc.txt)
# shellcheck disable=SC2086
ffmpeg -y -v error -loop 1 -framerate 30 -i /tmp/opencode/cards/card1.png \
  -loop 1 -framerate 30 -i /tmp/opencode/cards/card2.png \
  -loop 1 -framerate 30 -i /tmp/opencode/cards/card3.png \
  -loop 1 -framerate 30 -i /tmp/opencode/cards/card4.png \
  -loop 1 -framerate 30 -i /tmp/opencode/cards/card5.png \
  -loop 1 -framerate 30 -i /tmp/opencode/cards/card6.png \
  -filter_complex "$FC" -map "[left]" -c:v libx264 -preset veryfast -crf 22 \
  -level:v 5.0 -r 30 -t 96 /tmp/opencode/left_panel.mp4

# 2. Composite: pad base to full canvas FIRST, then overlay phone at x=1313.
ffmpeg -y -v error -i /tmp/opencode/left_panel.mp4 -i /tmp/opencode/video_cut.mp4 \
  -i /tmp/opencode/vo/narration.mp3 -filter_complex \
  "[0:v]tpad=stop_mode=clone:stop_duration=14,pad=1920:1080:0:0:color=0x14100b[left];[1:v]scale=607:1080:force_original_aspect_ratio=decrease,setsar=1[ph];[left][ph]overlay=1313:0[base];[base]subtitles=/tmp/opencode/wide.en.srt:force_style='FontName=Noto Sans,FontSize=20,PrimaryColour=&H00D8FF&,OutlineColour=&H80000000&,BorderStyle=1,Outline=2,Shadow=1,Alignment=2,MarginV=36'[v]" \
  -map "[v]" -map 2:a -c:v libx264 -preset veryfast -crf 22 -level:v 5.0 -r 30 \
  -c:a aac -b:a 128k -af "apad=whole_dur=110" -t 110 "$OUT"
ffprobe -v error -show_entries format=duration,size -of default=noprint_wrappers=1 "$OUT"
