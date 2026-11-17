#!/bin/bash
# Attach an ending to a finished video: the video's last frame is held under the ending, so the result is longer by the ending's length.
# Usage: append.sh <video> <ending-overlay.mov> <out.mp4>
# Keeps the video's size, frame rate and colour. For HLG (iPhone HDR) footage the card's white is matched to the
# footage's own whites; set WHITE_NPL to override the chosen level (203 is HLG reference white).
set -euo pipefail
v="$1"; o="$2"; out="$3"
probe() { ffprobe -v error -select_streams v:0 -show_entries "stream=$1" -of default=nw=1:nk=1 "$v" | head -1; }
d=$(probe duration); w=$(probe width); h=$(probe height); r=$(probe r_frame_rate); trc=$(probe color_transfer)
od=$(ffprobe -v error -show_entries format=duration -of default=nw=1:nk=1 "$o")
ow=$(ffprobe -v error -select_streams v:0 -show_entries stream=width -of default=nw=1:nk=1 "$o" | head -1)
oh=$(ffprobe -v error -select_streams v:0 -show_entries stream=height -of default=nw=1:nk=1 "$o" | head -1)
[ $((w * oh)) -eq $((h * ow)) ] || { echo "The video is ${w}x${h} and the ending is ${ow}x${oh}: different shapes." >&2; exit 1; }

if ffprobe -v error -select_streams a:0 -show_entries stream=index -of csv=p=0 "$v" | grep -q .; then
  a0="[0:a]aresample=48000,aformat=channel_layouts=stereo[a0]"
else
  a0="anullsrc=r=48000:cl=stereo,atrim=duration=${d}[a0]"
fi
audio="$a0;[1:a]aresample=48000,aformat=channel_layouts=stereo[a1];[a0][a1]concat=n=2:v=0:a=1[a]"
card="[1:v]format=yuva444p12le,fps=${r},scale=${w}:${h}:flags=lanczos,format=yuva444p12le"
hold="[0:v]tpad=stop_mode=clone:stop_duration=${od}[bg]"

case "$trc" in
  arib-std-b67)
    hlg() { echo "format=gbrp,zscale=tin=iec61966-2-1:pin=bt709:rin=full:t=arib-std-b67:p=bt2020:m=bt2020nc:r=limited:npl=$1,format=yuv420p10"; }
    luma() { grep -o "$1=[0-9]*" | cut -d= -f2; }
    npl="${WHITE_NPL:-}"
    if [ -z "$npl" ]; then
      # The level most of the footage's bright areas sit at, read from three frames.
      target=$(for f in 0.25 0.5 0.9; do
        ffmpeg -v error -ss "$(echo "$d * $f" | bc -l)" -i "$v" -frames:v 1 -vf "signalstats,metadata=print:key=lavfi.signalstats.YHIGH:file=-" -f null - | luma YHIGH
      done | sort -n | sed -n 2p)
      best=999999
      for n in 203 250 300 350 400 450 500 550 600; do
        y=$(ffmpeg -v error -f lavfi -i color=white:s=64x64 -frames:v 1 -vf "$(hlg "$n"),signalstats,metadata=print:key=lavfi.signalstats.YMAX:file=-" -f null - | luma YMAX)
        gap=$((y > target ? y - target : target - y))
        [ "$gap" -lt "$best" ] && { best=$gap; npl=$n; }
      done
      echo "footage whites at luma $target, card white set with npl=$npl"
    fi
    br=$(probe bit_rate); [ "$br" -gt 0 ] 2>/dev/null || br=30000000
    ffmpeg -v error -y -i "$v" -i "$o" -filter_complex "$hold;$card,split[c][m];[c]$(hlg "$npl")[c2];[m]alphaextract,format=gray10[m2];
      [c2][m2]alphamerge,setpts=PTS+${d}/TB[ov];[bg][ov]overlay=eof_action=pass:format=yuv420p10,format=yuv420p10le[vo];$audio" \
      -map "[vo]" -map "[a]" -c:v hevc_videotoolbox -profile:v main10 -b:v "$br" -tag:v hvc1 \
      -color_primaries bt2020 -color_trc arib-std-b67 -colorspace bt2020nc -color_range tv -c:a aac -b:a 256k -movflags +faststart "$out"
    ;;
  smpte2084)
    echo "This video is PQ HDR, which this script does not convert the card for. Export it as SDR or HLG." >&2; exit 1 ;;
  *)
    ffmpeg -v error -y -i "$v" -i "$o" -filter_complex "$hold;$card,setpts=PTS+${d}/TB[ov];[bg][ov]overlay=eof_action=pass:format=auto,format=yuv420p[vo];$audio" \
      -map "[vo]" -map "[a]" -c:v libx264 -preset slow -crf 17 -pix_fmt yuv420p -c:a aac -b:a 256k -movflags +faststart "$out"
    ;;
esac
echo "wrote $out"
