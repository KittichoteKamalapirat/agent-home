#!/bin/bash
# Render one thumbnail from the template.
# Usage: render.sh <thumb-dir> <out.jpg> "<query>"     e.g. render.sh thumb out.jpg "t1=No more&t2=what do I eat today?&icon=icon.png&phone=shot.jpg"
# Paths in the query are relative to <thumb-dir>; copy the icon and the app screenshot there first. Spaces in the query are fine.
set -euo pipefail
here="$(cd "$(dirname "$0")" && pwd)"
dir="$(cd "$1" && pwd)"; out="$2"; query="${3:-}"
cp "$here/thumb.html" "$dir/thumb.html"
encoded=$(python3 -c 'import sys,urllib.parse as u; print("&".join(k+"="+u.quote(v) for k,v in u.parse_qsl(sys.argv[1], keep_blank_values=True)))' "$query")
profile="$(mktemp -d)"
"/Applications/Google Chrome.app/Contents/MacOS/Google Chrome" --headless=new --disable-gpu --hide-scrollbars --force-device-scale-factor=1 \
  --window-size=1280,720 --user-data-dir="$profile" --screenshot="$dir/.thumb.png" "file://$dir/thumb.html?$encoded" >/dev/null 2>&1
ffmpeg -v error -y -i "$dir/.thumb.png" -q:v 2 "$out"
/bin/rm -f "$dir/.thumb.png"; /bin/rm -rf "$profile"
echo "wrote $out"
