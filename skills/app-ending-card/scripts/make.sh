#!/bin/bash
# Render the ending for one or more platforms.
# Usage: make.sh <work-dir> [platform...]     (default: instagram tiktok facebook youtube)
# <work-dir> holds card.json and the files it names. With "ingredients" in card.json the ending is the 6.5 s ingredients variant. If it also holds bg.png (the video's final frame, 1080x1920), a preview is made.
# Writes <work-dir>/out/ending-<platform>-overlay.mov (transparent, with sound) and ending-<platform>-preview.mp4.
set -euo pipefail
here="$(cd "$(dirname "$0")" && pwd)"
capture="$here/../../dev-vlog-editing/scripts/capture.mjs"      # the shared HTML-to-frames tool
work="$(cd "$1" && pwd)"; shift
platforms=("$@"); [ ${#platforms[@]} -gt 0 ] || platforms=(instagram tiktok facebook youtube)
mkdir -p "$work/out"
variant=$(node -e 'process.stdout.write(require(process.argv[1]).ingredients ? "ingredients" : "")' "$work/card.json")
node "$here/audio.mjs" "$work/out/audio.wav" $variant
for p in "${platforms[@]}"; do
  node "$capture" --page "$here/page" --out "$work/out/$p" --size 1080x1920 --mount /work="$work" --file /card.json="$work/card.json" --query "?p=$p" all >/dev/null
  ffmpeg -v error -y -framerate 30 -i "$work/out/$p/frames/%05d.png" -i "$work/out/audio.wav" \
    -c:v prores_ks -profile:v 4444 -pix_fmt yuva444p10le -r 30 -c:a pcm_s16le -shortest "$work/out/ending-$p-overlay.mov"
  if [ -f "$work/bg.png" ]; then
    ffmpeg -v error -y -loop 1 -framerate 30 -i "$work/bg.png" -framerate 30 -i "$work/out/$p/frames/%05d.png" -i "$work/out/audio.wav" \
      -filter_complex "[0][1]overlay=shortest=1,format=yuv420p[v]" -map "[v]" -map 2:a -c:v libx264 -crf 18 -r 30 -c:a aac -b:a 160k -shortest \
      -movflags +faststart "$work/out/ending-$p-preview.mp4"
  fi
  echo "wrote $work/out/ending-$p-overlay.mov"
done
