#!/usr/bin/env python3
"""
Prepare the profile photo for clean ASCII conversion:
  1. remove the background (rembg) so the subject is isolated
  2. bilateral-smooth away noise while keeping facial contours and features sharp
  3. apply CLAHE / tone stretch so skin tones land properly and hair/glasses stay dark
  4. darken linework (difference-of-gaussians ridges) for sunglasses and outlines
  5. composite onto white and crop square around the subject

Output: source-prepped.png (grayscale), consumed by make_ascii_svg.py.
"""
import os
import sys

import cv2
import numpy as np
from PIL import Image
from rembg import remove

HERE = os.path.dirname(os.path.abspath(__file__))
INP = sys.argv[1] if len(sys.argv) > 1 else os.path.join(HERE, "..", "avatar_darshan.png")
OUT = sys.argv[2] if len(sys.argv) > 2 else os.path.join(HERE, "..", "source-prepped.png")

LINE_WEIGHT = 0.5

print(f"Reading {INP}...")
orig_img = Image.open(INP).convert("RGBA")

# 1. cut out the subject using rembg
print("Removing background with rembg...")
cut = remove(orig_img)
rgb = np.array(cut.convert("RGB"))
alpha = np.array(cut.split()[-1])  # 0 = background

gray = cv2.cvtColor(rgb, cv2.COLOR_RGB2GRAY)

# 2. smooth texture, keep edges
smooth = gray
for _ in range(2):
    smooth = cv2.bilateralFilter(smooth, 9, 35, 9)

# 3. CLAHE local contrast enhancement
clahe = cv2.createCLAHE(clipLimit=2.5, tileGridSize=(8, 8))
clahe_img = clahe.apply(smooth)

# Tone stretch over subject area only
subject_mask = alpha > 40
if np.any(subject_mask):
    lo, hi = np.percentile(clahe_img[subject_mask], [3, 94])
    if hi > lo:
        tone = np.clip((clahe_img.astype(np.float32) - lo) / (hi - lo), 0, 1)
    else:
        tone = clahe_img.astype(np.float32) / 255.0
else:
    tone = clahe_img.astype(np.float32) / 255.0

# 4. difference-of-gaussians ridges to enhance glasses and jawline
fine = cv2.GaussianBlur(smooth, (0, 0), 1.2).astype(np.float32)
coarse = cv2.GaussianBlur(smooth, (0, 0), 5.0).astype(np.float32)
lines = np.clip((coarse - fine) / 35.0, 0, 1)
out = np.clip(tone - LINE_WEIGHT * lines, 0, 1) * 255.0

# 5. paste onto white background
mask = cv2.GaussianBlur(alpha.astype(np.float32) / 255.0, (0, 0), 0.8)
out = out * mask + 255.0 * (1.0 - mask)

# Crop with padding around subject
ys, xs = np.where(alpha > 30)
if len(xs) > 0 and len(ys) > 0:
    side = max(xs.max() - xs.min(), ys.max() - ys.min()) + 40
    cx, cy = (xs.min() + xs.max()) // 2, (ys.min() + ys.max()) // 2
    canvas = np.full((side, side), 255, np.uint8)
    x0, y0 = cx - side // 2, cy - side // 2
    sx0, sy0 = max(x0, 0), max(y0, 0)
    sx1, sy1 = min(x0 + side, out.shape[1]), min(y0 + side, out.shape[0])
    canvas[sy0 - y0:sy1 - y0, sx0 - x0:sx1 - x0] = out[sy0:sy1, sx0:sx1].astype(np.uint8)
else:
    canvas = out.astype(np.uint8)

Image.fromarray(canvas, mode="L").save(OUT)
print(f"wrote {OUT}: {canvas.shape}")
