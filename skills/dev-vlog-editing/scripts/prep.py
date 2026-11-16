"""Prepare an edit folder for one source video: probe it, extract speech audio, list silences.
Usage: python3 prep.py <source-video> <edit-dir>
Writes <edit-dir>/audio16k.wav, silences.txt (start end duration, seconds) and a starter edit.json."""
import json, os, re, subprocess, sys

src, edit = os.path.abspath(sys.argv[1]), sys.argv[2]
os.makedirs(edit, exist_ok=True)
probe = subprocess.run(["ffprobe", "-v", "error", "-select_streams", "v:0", "-show_entries",
                        "stream=width,height,r_frame_rate,color_transfer:format=duration,size", "-of", "json", src],
                       capture_output=True, text=True, check=True).stdout
print(probe)
subprocess.run(["ffmpeg", "-v", "error", "-y", "-i", src, "-vn", "-ac", "1", "-ar", "16000", f"{edit}/audio16k.wav"], check=True)
log = subprocess.run(["ffmpeg", "-hide_banner", "-i", f"{edit}/audio16k.wav", "-af", "silencedetect=n=-35dB:d=0.45", "-f", "null", "-"],
                     capture_output=True, text=True).stderr
starts = [float(x) for x in re.findall(r"silence_start: ([\d.]+)", log)]
ends = [float(x) for x in re.findall(r"silence_end: ([\d.]+)", log)]
with open(f"{edit}/silences.txt", "w") as f:
    for a, b in zip(starts, ends):
        f.write(f"{a:.3f} {b:.3f} {b - a:.3f}\n")
print(len(ends), "silences ->", f"{edit}/silences.txt")
cfg = f"{edit}/edit.json"
if not os.path.exists(cfg):
    json.dump({"source": src, "ranges": [], "hard_cut_after": [], "word_fixes": [], "drop_words": [], "extra_words": [], "cues": {}},
              open(cfg, "w"), indent=1)
    print("wrote starter", cfg)
