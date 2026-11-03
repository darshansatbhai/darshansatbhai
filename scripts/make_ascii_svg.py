#!/usr/bin/env python3
"""
Convert a prepped portrait photo into a clean, monochrome ASCII-art SVG
that "types" itself in like a terminal, then freezes.

GitHub renders SVGs embedded via <img> and runs their SMIL animations.
Each row is revealed with a left-to-right clip wipe plus a small block cursor
riding the wipe edge, staggered top -> bottom, so the portrait prints once
and freezes.
"""
import html
import os
import sys
from PIL import Image, ImageEnhance, ImageFilter

HERE = os.path.dirname(os.path.abspath(__file__))
SRC = sys.argv[1] if len(sys.argv) > 1 else os.path.join(HERE, "..", "source-prepped.png")
OUT = sys.argv[2] if len(sys.argv) > 2 else os.path.join(HERE, "..", "darshan-ascii.svg")

# Canvas dimensions (840 x 880 matches info-card / stats card)
CANVAS_W = 840
CANVAS_H = 880
PAD = 20
TITLEBAR_H = 32
STATUS_H = 34

ART_W = CANVAS_W - PAD * 2
ART_H = CANVAS_H - TITLEBAR_H - STATUS_H - PAD

COLS = int(os.environ.get("COLS", 140))
ROWS = int(os.environ.get("ROWS", round(COLS * (ART_H / ART_W) * (8 / 15))))
CELL_W = ART_W / COLS
CELL_H = ART_H / ROWS

RAMP = " .`:-=+*cs#%@"  # bright (sparse) -> dark (dense); leading space clears white bg

CONTRAST = 1.15
BRIGHTNESS = 1.02
GAMMA = 1.12
WHITE_FLOOR = 0.85

BG = "#0d1117"
BG2 = "#111722"
FRAME = "#30363d"
TITLE_TEXT = "#7d8590"
INK = "#c9d1d9"        # monochrome silver-gray fill
CURSOR = "#c9d1d9"

# Animation timing (one-shot sweep top -> bottom in ~5 seconds)
TOTAL_DUR = 5.2
ROW_DUR = TOTAL_DUR / ROWS
STAGGER = ROW_DUR

print(f"Loading {SRC}...")
im = Image.open(SRC).convert("L")
im = ImageEnhance.Brightness(im).enhance(BRIGHTNESS)
im = ImageEnhance.Contrast(im).enhance(CONTRAST)
im = im.resize((COLS, ROWS), Image.Resampling.LANCZOS)
px = im.load()

STATIC = bool(os.environ.get("STATIC"))

rows_txt = []
for y in range(ROWS):
    chars = []
    for x in range(COLS):
        lum = px[x, y] / 255.0
        lum = pow(lum, GAMMA)
        if lum >= WHITE_FLOOR:
            chars.append(" ")
            continue
        idx = int((1.0 - lum) * (len(RAMP) - 1) + 0.5)
        idx = max(0, min(len(RAMP) - 1, idx))
        chars.append(RAMP[idx])
    rows_txt.append("".join(chars))

art_top = TITLEBAR_H + 10

parts = [
    f'<svg xmlns="http://www.w3.org/2000/svg" width="{CANVAS_W}" height="{CANVAS_H}" '
    f'viewBox="0 0 {CANVAS_W} {CANVAS_H}" font-family="ui-monospace, SFMono-Regular, Menlo, Consolas, monospace">',
    '<defs>'
    f'<linearGradient id="bg" x1="0" y1="0" x2="0" y2="1">'
    f'<stop offset="0" stop-color="{BG2}"/><stop offset="1" stop-color="{BG}"/>'
    f'</linearGradient></defs>',
    f'<rect width="{CANVAS_W}" height="{CANVAS_H}" rx="12" fill="url(#bg)"/>',
    f'<rect x="0.5" y="0.5" width="{CANVAS_W-1}" height="{CANVAS_H-1}" rx="12" fill="none" stroke="{FRAME}" stroke-width="1"/>',
    f'<line x1="0" y1="{TITLEBAR_H}" x2="{CANVAS_W}" y2="{TITLEBAR_H}" stroke="{FRAME}"/>',
]

# Window dots
for i, dotcol in enumerate(["#ff5f56", "#ffbd2e", "#27c93f"]):
    parts.append(f'<circle cx="{PAD + i*16}" cy="{TITLEBAR_H/2}" r="5" fill="{dotcol}"/>')
parts.append(f'<text x="{CANVAS_W/2}" y="{TITLEBAR_H/2 + 4}" fill="{TITLE_TEXT}" font-size="12" '
             f'text-anchor="middle">darshan@github: ~$ ./portrait.sh</text>')

# Render rows
font_size = CELL_H * 0.92
for ry, line in enumerate(rows_txt):
    y = art_top + ry * CELL_H + CELL_H * 0.74
    row_y = art_top + ry * CELL_H
    delay = ry * STAGGER
    safe = html.escape(line)
    text = (f'<text xml:space="preserve" x="{PAD}" y="{y:.1f}" fill="{INK}" '
            f'font-size="{font_size:.1f}" textLength="{ART_W}" lengthAdjust="spacing">{safe}</text>')

    if STATIC:
        parts.append(text)
        continue

    parts.append(
        f'<clipPath id="r{ry}"><rect x="{PAD}" y="{row_y:.1f}" height="{CELL_H:.2f}" width="0">'
        f'<animate attributeName="width" from="0" to="{ART_W}" begin="{delay:.3f}s" '
        f'dur="{ROW_DUR:.2f}s" fill="freeze"/></rect></clipPath>'
    )
    parts.append(f'<g clip-path="url(#r{ry})">{text}</g>')
    parts.append(
        f'<rect y="{row_y+0.5:.1f}" width="{CELL_W:.1f}" height="{CELL_H-1:.2f}" fill="{CURSOR}" opacity="0">'
        f'<animate attributeName="x" from="{PAD}" to="{PAD+ART_W}" begin="{delay:.3f}s" '
        f'dur="{ROW_DUR:.2f}s" fill="freeze"/>'
        f'<set attributeName="opacity" to="0.85" begin="{delay:.3f}s"/>'
        f'<set attributeName="opacity" to="0" begin="{delay+ROW_DUR:.3f}s"/></rect>'
    )

# Status line with terminal prompt and blinking cursor
status_line_y = CANVAS_H - STATUS_H
status_y = status_line_y + 20
parts.append(f'<line x1="0" y1="{status_line_y:.1f}" x2="{CANVAS_W}" y2="{status_line_y:.1f}" stroke="{FRAME}"/>')
status_prompt = "darshan@github:~$ whoami "
status_name = "Darshan Satbhai"
parts.append(f'<text x="{PAD}" y="{status_y:.1f}" fill="{TITLE_TEXT}" font-size="13">'
             f'{status_prompt}<tspan fill="{INK}">{status_name}</tspan></text>')

cursor_x = PAD + len(status_prompt + status_name + " ") * 8.2
parts.append(f'<rect x="{cursor_x:.1f}" y="{status_y-12:.1f}" width="8" height="15" fill="{INK}">'
             f'<animate attributeName="opacity" values="1;1;0;0" keyTimes="0;0.5;0.51;1" '
             f'dur="1s" repeatCount="indefinite"/></rect>')

parts.append("</svg>")
svg = "".join(parts)

with open(OUT, "w", encoding="utf-8") as f:
    f.write(svg)

print(f"wrote {OUT}: {CANVAS_W} x {CANVAS_H}, {len(svg)} bytes ({COLS}x{ROWS} grid)")
