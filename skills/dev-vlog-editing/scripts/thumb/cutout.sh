#!/bin/bash
# Cut the person out of a frame and blur the room behind them, for a thumbnail.
# Usage: cutout.sh <frame.jpg> <thumb-dir> [blur-sigma, default 10]
# Writes <thumb-dir>/frame.jpg, mask.png, person.png (the person on transparency) and bg-blur.jpg (the room, blurred, without the person).
set -euo pipefail
here="$(cd "$(dirname "$0")" && pwd)"
frame="$1"; dir="$2"; sigma="${3:-10}"
mkdir -p "$dir"
[ "$frame" -ef "$dir/frame.jpg" ] || cp "$frame" "$dir/frame.jpg"
swift "$here/mask.swift" "$dir/frame.jpg" "$dir/mask.png"
size=$(ffprobe -v error -select_streams v:0 -show_entries stream=width,height -of csv=s=x:p=0 "$dir/frame.jpg")
ffmpeg -v error -y -i "$dir/frame.jpg" -i "$dir/mask.png" \
  -filter_complex "[1:v]format=gray,scale=${size/x/:}:flags=bicubic,gblur=sigma=2.5[m];[0:v][m]alphamerge" "$dir/person.png"
uv run -q --with pillow --with numpy "$here/blurbg.py" "$dir" "$sigma"
echo "wrote $dir/person.png and $dir/bg-blur.jpg"
