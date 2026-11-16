"""Lay the captured overlay frames over the cut and normalise loudness.
Usage: python3 compose.py <edit-dir> <output.mp4>
Reads base.mkv and frames/%05d.png (written by capture.mjs)."""
import json, subprocess, sys

E, out = sys.argv[1], sys.argv[2]
T = json.load(open(f"{E}/timeline.json")); n = round(T["total"] * T["fps"])
subprocess.run(["ffmpeg", "-v", "error", "-y", "-i", f"{E}/base.mkv", "-framerate", str(T["fps"]), "-i", f"{E}/frames/%05d.png",
                "-filter_complex", "[1:v]format=rgba[o];[0:v][o]overlay=eof_action=pass:format=auto,format=yuv420p[v];"
                                   "[0:a]loudnorm=I=-16:TP=-1.5:LRA=11,aresample=48000[a]",
                "-map", "[v]", "-map", "[a]", "-frames:v", str(n), "-c:v", "libx264", "-preset", "slow", "-crf", "21",
                "-maxrate", "9M", "-bufsize", "18M", "-pix_fmt", "yuv420p", "-c:a", "aac", "-b:a", "192k", "-movflags", "+faststart", out], check=True)
print(subprocess.run(["ffprobe", "-v", "error", "-show_entries", "format=duration,size", "-of", "csv=p=0", out], capture_output=True, text=True).stdout)
