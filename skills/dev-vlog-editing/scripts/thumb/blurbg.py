# Blur the room without the person bleeding into it: blur only background pixels, weighted by the inverse person mask.
# Usage: uv run --with pillow --with numpy blurbg.py <thumb-dir> [sigma]   (reads frame.jpg and mask.png, writes bg-blur.jpg)
import sys
import numpy as np
from PIL import Image, ImageFilter

d = sys.argv[1]
sigma = float(sys.argv[2]) if len(sys.argv) > 2 else 10
img = Image.open(f"{d}/frame.jpg").convert("RGB")
mask = Image.open(f"{d}/mask.png").convert("L").resize(img.size, Image.BICUBIC).filter(ImageFilter.MaxFilter(21))  # grow the person a little
w = 1 - np.asarray(mask, dtype=np.float32) / 255
rgb = np.asarray(img, dtype=np.float32)
blur = lambda a: np.asarray(Image.fromarray(a).filter(ImageFilter.GaussianBlur(sigma)), dtype=np.float32)
den = np.maximum(blur((w * 255).astype(np.uint8)) / 255, 1e-3)
res = np.stack([blur((rgb[..., c] * w).astype(np.uint8)) / den for c in range(3)], axis=-1)
Image.fromarray(np.clip(res, 0, 255).astype(np.uint8)).save(f"{d}/bg-blur.jpg", quality=94)
