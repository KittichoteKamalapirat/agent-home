#!/bin/bash
# Render a YouTube channel banner (2560x1440 PNG) from <work-dir>/banner.json.
# Usage: render.sh <work-dir> <out.png> [guide]
# Image paths in banner.json are relative to <work-dir>. "guide" draws the phone, tablet and desktop boxes
# and writes a check image; never upload that one.
set -euo pipefail
here="$(cd "$(dirname "$0")" && pwd)"
dir="$(cd "$1" && pwd)"; out="$2"; guide="${3:-}"
python3 -c 'import json,sys; json.load(open(sys.argv[1]))' "$dir/banner.json"
cp "$here/banner.html" "$dir/banner.html"
{ printf 'window.BANNER = '; cat "$dir/banner.json"; } > "$dir/banner.config.js"
profile="$(mktemp -d)"
"/Applications/Google Chrome.app/Contents/MacOS/Google Chrome" --headless=new --disable-gpu --hide-scrollbars --force-device-scale-factor=1 \
  --window-size=2560,1440 --allow-file-access-from-files --user-data-dir="$profile" --screenshot="$out" \
  "file://$dir/banner.html${guide:+?guide=1}" >/dev/null 2>&1
/bin/rm -rf "$profile"
[ -s "$out" ] || { echo "Chrome wrote no image" >&2; exit 1; }
echo "wrote $out"
