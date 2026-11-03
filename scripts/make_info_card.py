#!/usr/bin/env python3
"""
Generate an animated neofetch-style SVG info card for Darshan Satbhai.
Plays a staggered line-by-line slide/fade-in animation once and freezes.
Supports STATIC=1 environment variable for frozen state previews.
"""
import html
import os
import sys

HERE = os.path.dirname(os.path.abspath(__file__))
OUT = sys.argv[1] if len(sys.argv) > 1 else os.path.join(HERE, "..", "info-card.svg")

STATIC = bool(os.environ.get("STATIC"))

W, H = 840, 880
PAD = 24
TITLEBAR_H = 36

BG = "#0d1117"
BG2 = "#111722"
FRAME = "#30363d"
MUTED = "#7d8590"
TEXT = "#e6edf3"
KEY_COLOR = "#22d3ee"      # cyan prompt key
VAL_COLOR = "#c9d1d9"      # crisp silver text
ACCENT = "#39d353"         # green
PURPLE = "#bc8cff"
GOLD = "#f2cc60"
CORAL = "#ff7b72"

# Terminal ANSI color palette dots/bars
ANSI_COLORS = [
    "#484f58", "#ff7b72", "#3fb950", "#d29922", "#58a6ff", "#bc8cff", "#39c5cf", "#b1bac4",
    "#6e7681", "#ffa198", "#56d364", "#e3b341", "#79c0ff", "#d2a8ff", "#56d4dd", "#f0f6fc"
]

info_lines = [
    ("darshan@github", "--------------------------------------", PURPLE, MUTED, True),
    ("OS", "Arch Linux x86_64", KEY_COLOR, VAL_COLOR, False),
    ("Host", "Darshan Satbhai", KEY_COLOR, VAL_COLOR, False),
    ("Role", "Full-Stack & Mobile Developer", KEY_COLOR, GOLD, False),
    ("Kernel", "Linux 6.8.9-antigravity", KEY_COLOR, VAL_COLOR, False),
    ("Uptime", "3+ years of continuous learning", KEY_COLOR, VAL_COLOR, False),
    ("Packages", "24 repos (pacman, npm, pub, pip)", KEY_COLOR, VAL_COLOR, False),
    ("Shell", "zsh 5.9 (omz / agy-theme)", KEY_COLOR, VAL_COLOR, False),
    ("Languages", "TypeScript, Python, Dart, Kotlin, JS", KEY_COLOR, ACCENT, False),
    ("Frontend", "React, Next.js, Three.js, Tailwind CSS", KEY_COLOR, VAL_COLOR, False),
    ("Mobile", "Flutter, Android, iOS, React Native", KEY_COLOR, VAL_COLOR, False),
    ("Backend", "Node.js, Express, FastAPI, PostgreSQL", KEY_COLOR, VAL_COLOR, False),
    ("Projects", "Echo-Music, Gullak.ai, OmniRoute, Solar-System", KEY_COLOR, PURPLE, False),
    ("Editor", "Neovim / VS Code", KEY_COLOR, VAL_COLOR, False),
    ("Terminal", "Kitty / Ghostty", KEY_COLOR, VAL_COLOR, False),
]

css = """
@keyframes fadeIn {
  0%   { opacity: 0; transform: translateX(-12px); }
  100% { opacity: 1; transform: translateX(0); }
}
.line {
  opacity: 0;
  animation: fadeIn 0.4s cubic-bezier(0.16, 1, 0.3, 1) both;
}
@media (prefers-reduced-motion: reduce) {
  .line { opacity: 1 !important; transform: none !important; animation: none !important; }
}
""".strip()

parts = [
    f'<svg xmlns="http://www.w3.org/2000/svg" width="{W}" height="{H}" viewBox="0 0 {W} {H}" '
    f'font-family="ui-monospace, SFMono-Regular, Menlo, Consolas, monospace">',
    f'<style>{css}</style>',
    '<defs>'
    f'<linearGradient id="cardbg" x1="0" y1="0" x2="0" y2="1">'
    f'<stop offset="0" stop-color="{BG2}"/><stop offset="1" stop-color="{BG}"/>'
    f'</linearGradient>'
    '</defs>',
    f'<rect width="{W}" height="{H}" rx="14" fill="url(#cardbg)"/>',
    f'<rect x="0.5" y="0.5" width="{W-1}" height="{H-1}" rx="14" fill="none" stroke="{FRAME}" stroke-width="1"/>',
    f'<line x1="0" y1="{TITLEBAR_H}" x2="{W}" y2="{TITLEBAR_H}" stroke="{FRAME}" stroke-width="1"/>',
]

# Window control dots
for i, dot in enumerate(["#ff5f56", "#ffbd2e", "#27c93f"]):
    parts.append(f'<circle cx="{PAD + i * 20}" cy="{TITLEBAR_H / 2}" r="6" fill="{dot}"/>')

parts.append(
    f'<text x="{W / 2}" y="{TITLEBAR_H / 2 + 5}" fill="{MUTED}" font-size="13" '
    f'text-anchor="middle">darshan@github: ~$ neofetch --me</text>'
)

# Start rendering lines
y_start = TITLEBAR_H + 34
line_height = 42

for idx, (key, val, kcol, vcol, is_header) in enumerate(info_lines):
    y = y_start + idx * line_height
    delay = 0.08 * (idx + 1)
    anim_style = "" if STATIC else f' style="animation-delay: {delay:.2f}s;"'
    cls = "" if STATIC else ' class="line"'
    safe_key = html.escape(key)
    safe_val = html.escape(val)

    parts.append(f'<g{cls}{anim_style}>')
    if is_header:
        parts.append(f'<text x="{PAD + 12}" y="{y}" fill="{kcol}" font-size="22" font-weight="700">{safe_key}</text>')
        parts.append(f'<text x="{PAD + 12}" y="{y + 16}" fill="{vcol}" font-size="16">{safe_val}</text>')
    else:
        # Prompt symbol + Key + Value
        parts.append(f'<text x="{PAD + 12}" y="{y}" fill="{CORAL}" font-size="18" font-weight="700">&gt;</text>')
        parts.append(f'<text x="{PAD + 34}" y="{y}" fill="{kcol}" font-size="18" font-weight="600">{safe_key}:</text>')
        val_x = PAD + 180
        parts.append(f'<text x="{val_x}" y="{y}" fill="{vcol}" font-size="18">{safe_val}</text>')
    parts.append('</g>')

# Color blocks row at bottom
color_y = y_start + len(info_lines) * line_height + 24
color_start_delay = 0.08 * (len(info_lines) + 1)
anim_style = "" if STATIC else f' style="animation-delay: {color_start_delay:.2f}s;"'
cls = "" if STATIC else ' class="line"'

parts.append(f'<g{cls}{anim_style}>')
parts.append(f'<line x1="{PAD}" y1="{color_y - 16}" x2="{W - PAD}" y2="{color_y - 16}" stroke="{FRAME}" stroke-opacity="0.5"/>')

block_w = 40
block_h = 24
gap = 6
total_palette_w = 8 * (block_w + gap) - gap
start_x = (W - total_palette_w) / 2

for i in range(8):
    bx = start_x + i * (block_w + gap)
    parts.append(f'<rect x="{bx:.1f}" y="{color_y:.1f}" width="{block_w}" height="{block_h}" rx="4" fill="{ANSI_COLORS[i]}"/>')
    parts.append(f'<rect x="{bx:.1f}" y="{color_y + block_h + 6:.1f}" width="{block_w}" height="{block_h}" rx="4" fill="{ANSI_COLORS[i+8]}"/>')

parts.append('</g>')

parts.append('</svg>')
svg = "".join(parts)

with open(OUT, "w", encoding="utf-8") as f:
    f.write(svg)

print(f"wrote {OUT}: {W} x {H}, {len(svg)} bytes")
