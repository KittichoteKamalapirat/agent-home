"""Word-level transcript of <edit-dir>/audio16k.wav with local Whisper (no account needed).
Usage: uv run --with mlx-whisper python transcribe.py <edit-dir> [model]
Writes transcript.json (words with start/end) and takes.md (one line per phrase, split at pauses of 0.5 s or more).
Pass start and end seconds after the model to re-transcribe only that stretch; the words are printed, not saved."""
import json, subprocess, sys
import mlx_whisper

edit = sys.argv[1]
model = sys.argv[2] if len(sys.argv) > 2 else "mlx-community/whisper-small-mlx"
audio, offset = f"{edit}/audio16k.wav", 0.0
if len(sys.argv) > 4:
    offset, end = float(sys.argv[3]), float(sys.argv[4])
    audio = f"{edit}/stretch.wav"
    subprocess.run(["ffmpeg", "-v", "error", "-y", "-ss", str(offset), "-t", str(end - offset), "-i", f"{edit}/audio16k.wav", audio], check=True)
r = mlx_whisper.transcribe(audio, path_or_hf_repo=model, word_timestamps=True,
                           condition_on_previous_text=False, language="en", verbose=False)
words = [{"text": w["word"].strip(), "start": round(w["start"] + offset, 3), "end": round(w["end"] + offset, 3)}
         for s in r["segments"] for w in s.get("words", [])]
if offset or len(sys.argv) > 4:
    for w in words: print(json.dumps([w["text"], w["start"], w["end"]]))
    sys.exit()
json.dump({"model": model, "words": words}, open(f"{edit}/transcript.json", "w"), indent=0)
lines, cur = [], []
for w in words:
    if cur and w["start"] - cur[-1]["end"] >= 0.5:
        lines.append(cur); cur = []
    cur.append(w)
if cur: lines.append(cur)
with open(f"{edit}/takes.md", "w") as f:
    for l in lines:
        f.write("[%07.2f-%07.2f] %s\n" % (l[0]["start"], l[-1]["end"], " ".join(w["text"] for w in l)))
print(len(words), "words,", len(lines), "phrases ->", f"{edit}/takes.md")
