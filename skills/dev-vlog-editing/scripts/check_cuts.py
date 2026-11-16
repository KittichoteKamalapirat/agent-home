"""Check a finished video against its timeline: how long the quiet is at every cut, plus contact sheets to look at.
Usage: python3 check_cuts.py <edit-dir> <video.mp4>
Writes verify/cuts-N.jpg (the frame before and after each cut) and verify/moments.jpg (one frame per cue)."""
import json, os, re, subprocess, sys

E, video = sys.argv[1], sys.argv[2]
T = json.load(open(f"{E}/timeline.json")); S, FPS = T["segs"], T["fps"]
os.makedirs(f"{E}/verify", exist_ok=True)
o = subprocess.run(["ffmpeg", "-v", "error", "-i", video, "-vn", "-af",
                    "astats=metadata=1:reset=1,ametadata=print:key=lavfi.astats.Overall.RMS_level:file=-", "-f", "null", "-"],
                   capture_output=True, text=True).stdout
r = [max(-99, float(x)) if x != "-inf" else -99 for x in re.findall(r"RMS_level=(\S+)", o)]
st = 1024 / 48000
for s in S[1:]:
    c = s["out"] + s["ov"] / 2; k = int(c / st); w = r[max(0, k - 10):k + 14]
    quiet = sum(1 for v in w if v < -35) * st
    print("cut %7.2f s  quiet %.2f s %s" % (c, quiet, "  <- long pause" if quiet > 0.25 else ""))
cuts = [round((s["out"] + s["ov"] / 2) * FPS) for s in S[1:]]
for n in range(0, len(cuts), 8):
    part = cuts[n:n + 8]; sel = "+".join(f"eq(n,{c - 1})+eq(n,{c})" for c in part)
    subprocess.run(["ffmpeg", "-v", "error", "-y", "-i", video, "-vf", f"select='{sel}',scale=400:-1,tile=4x{-(-len(part) // 2)}", "-frames:v", "1", "-vsync", "0",
                    f"{E}/verify/cuts-{n // 8}.jpg"], check=True)
ts = sorted(set(min(round((t + 1.5) * FPS), round(T["total"] * FPS) - 5) for k, t in T["cues"].items() if k != "end"))[:16]
if ts:
    sel = "+".join(f"eq(n,{f})" for f in ts)
    subprocess.run(["ffmpeg", "-v", "error", "-y", "-i", video, "-vf", f"select='{sel}',scale=640:-1,tile=4x{-(-len(ts) // 4)}", "-frames:v", "1", "-vsync", "0",
                    f"{E}/verify/moments.jpg"], check=True)
print("sheets in", f"{E}/verify")
