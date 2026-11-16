"""Render the cut from <edit-dir>/timeline.json: one picture file per take joined losslessly, sound mixed with the J-cut overlaps.
Usage: python3 render_base.py <edit-dir> [WIDTHxHEIGHT]   (default 1920x1080)
Writes clips/seg_NN.mkv, base.wav and base.mkv. HLG (iPhone HDR) sources are tone-mapped to SDR."""
import json, os, subprocess, sys

E = sys.argv[1]
W, H = (sys.argv[2] if len(sys.argv) > 2 else "1920x1080").split("x")
T = json.load(open(f"{E}/timeline.json")); S, FPS, SRC = T["segs"], T["fps"], T["source"]
os.makedirs(f"{E}/clips", exist_ok=True)
transfer = subprocess.run(["ffprobe", "-v", "error", "-select_streams", "v:0", "-show_entries", "stream=color_transfer", "-of", "csv=p=0", SRC],
                          capture_output=True, text=True).stdout.strip()
GRADE = "format=yuv420p"
if transfer == "arib-std-b67":
    GRADE = ("zscale=tin=arib-std-b67:min=bt2020nc:pin=bt2020:rin=tv:t=linear:npl=203,format=gbrpf32le,tonemap=hable:desat=0,"
             "zscale=p=bt709:t=bt709:m=bt709:r=tv,eq=contrast=1.05:brightness=0.02:saturation=1.06,format=yuv420p")
# picture cuts sit in the middle of each audio overlap, on whole frames
cuts = [0] + [round((s["out"] + s["ov"] / 2) * FPS) for s in S[1:]] + [round(T["total"] * FPS)]
lst = []
for s in S:
    i = s["i"]; n = cuts[i + 1] - cuts[i]; ss = s["start"] + cuts[i] / FPS - s["out"]; out = f"{E}/clips/seg_%02d.mkv" % i
    vf = f"fps={FPS},scale={W}:{H}:flags=lanczos,{GRADE}"
    if i == len(S) - 1: vf += f",fade=t=out:st={n / FPS - 0.5:.3f}:d=0.5"
    subprocess.run(["ffmpeg", "-v", "error", "-y", "-ss", f"{ss:.4f}", "-i", SRC, "-map", "0:v:0", "-vf", vf, "-frames:v", str(n),
                    "-c:v", "libx264", "-preset", "fast", "-crf", "12", "-pix_fmt", "yuv420p", "-r", str(FPS), out], check=True)
    lst.append("file '%s'" % os.path.abspath(out)); print("take", i, n, "frames", flush=True)
open(f"{E}/clips/concat.txt", "w").write("\n".join(lst) + "\n")
subprocess.run(["ffmpeg", "-v", "error", "-y", "-f", "concat", "-safe", "0", "-i", f"{E}/clips/concat.txt", "-c", "copy", f"{E}/base_v.mkv"], check=True)
# sound: every take keeps its full length; they are mixed with the overlaps
cmd, fc = ["ffmpeg", "-v", "error", "-y"], []
for s in S:
    i = s["i"]; d = s["end"] - s["start"]; last = i == len(S) - 1
    fin = 0.06 if s["ov"] else 0.03
    fout = 0.5 if last else (0.12 if S[i + 1]["ov"] else 0.03)
    cmd += ["-ss", str(s["start"]), "-t", f"{d:.3f}", "-i", SRC]
    fc.append(f"[{i}:a:0]aformat=sample_rates=48000:channel_layouts=stereo,highpass=f=80,afftdn=nr=8:nf=-45,"
              f"afade=t=in:st=0:d={fin},afade=t=out:st={d - fout:.3f}:d={fout},adelay={round(s['out'] * 48000)}S:all=1[a{i}]")
fc.append("".join(f"[a{s['i']}]" for s in S) + f"amix=inputs={len(S)}:normalize=0:duration=longest[a]")
subprocess.run(cmd + ["-filter_complex", ";".join(fc), "-map", "[a]", "-c:a", "pcm_s16le", f"{E}/base.wav"], check=True)
subprocess.run(["ffmpeg", "-v", "error", "-y", "-i", f"{E}/base_v.mkv", "-i", f"{E}/base.wav", "-c", "copy", f"{E}/base.mkv"], check=True)
os.remove(f"{E}/base_v.mkv")
print("base done:", f"{E}/base.mkv", cuts[-1], "frames")
