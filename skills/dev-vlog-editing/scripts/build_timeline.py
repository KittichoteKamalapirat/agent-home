"""Turn the cut decisions in <edit-dir>/edit.json into timeline.json and master.srt.
Usage: python3 build_timeline.py <edit-dir>

edit.json fields (times are source seconds):
  source            path of the source video
  ranges            [[start, end], ...] kept takes in story order, on speech boundaries
  hard_cut_after    indexes of ranges that end on speech, not on a pause: no end pad, no audio overlap into the next
  word_fixes        [[["heard", "tokens"], ["Wanted", "tokens"]], ...] matched on lowercase letters and digits only
  drop_words        [[start, end], ...] words starting in these stretches are left out of the subtitles
  extra_words       [["text", start, end], ...] words the speech model missed
  cues              {"name": {"word": "decide", "after": 0, "nth": 0}} or {"name": {"time": 26.05}}: moments the graphics key off
  optional          fps 30, pad_in 0.08, pad_out 0.12, overlap_frames 4, sub_chars 36, sub_lookback 0.4, tighten_db -38
"""
import json, math, re, struct, sys, wave

E = sys.argv[1]
cfg = json.load(open(f"{E}/edit.json"))
FPS = cfg.get("fps", 30)
PAD_IN, PAD_OUT = cfg.get("pad_in", 0.08), cfg.get("pad_out", 0.12)
OV = cfg.get("overlap_frames", 4) / FPS      # J-cut: the next take's sound starts this long before the previous one has faded out
HARD = set(cfg.get("hard_cut_after", []))
DB = cfg.get("tighten_db", -38)

# Tighten every range to where the voice really starts and stops, measured on the audio itself.
_w = wave.open(f"{E}/audio16k.wav"); _sr = _w.getframerate()
_d = struct.unpack("<%dh" % _w.getnframes(), _w.readframes(_w.getnframes()))
_H = _sr // 100                                   # 10 ms
def _db(k):
    c = _d[k * _H:(k + 1) * _H]
    return 20 * math.log10(math.sqrt(sum(x * x for x in c) / len(c)) / 32768 + 1e-9) if c else -99
def _loud(k): return all(_db(j) > DB for j in (k, k + 1, k + 2))
def tighten(i, a, b):
    k0 = next((k for k in range(int((a - 0.08) * 100), int((a + 0.9) * 100)) if _loud(k)), None)
    k1 = next((k for k in range(int((b + 0.12) * 100), int((b - 0.9) * 100), -1) if _loud(k - 2)), None)
    a2 = max(a, k0 / 100 - 0.04) if k0 is not None else a
    b2 = min(b, k1 / 100 + 0.07) if k1 is not None and i not in HARD else b
    if a2 - a > 0.02 or b - b2 > 0.02: print("tighten %2d  start +%.2f  end -%.2f" % (i, a2 - a, b - b2))
    return (round(a2, 3), round(b2, 3))
RANGES = [tighten(i, a, b) for i, (a, b) in enumerate(cfg["ranges"])]

drops = cfg.get("drop_words", [])
words = [w for w in json.load(open(f"{E}/transcript.json"))["words"] if not any(a <= w["start"] < b for a, b in drops)]
words += [dict(text=t, start=a, end=b) for t, a, b in cfg.get("extra_words", [])]
words.sort(key=lambda w: w["start"])

segs, off = [], 0.0
for i, (a, b) in enumerate(RANGES):
    s, e = max(0, a - PAD_IN), b + (0 if i in HARD else PAD_OUT)
    ov = 0 if i == 0 or (i - 1) in HARD else OV
    off -= ov
    segs.append(dict(i=i, start=round(s, 3), end=round(e, 3), out=round(off, 4), ov=round(ov, 4))); off += e - s
total = off

def to_out(t):
    for s in segs:
        if s["start"] - 0.01 <= t <= s["end"] + 0.01: return round(s["out"] + t - s["start"], 3)
    n = min(segs, key=lambda s: min(abs(t - s["start"]), abs(t - s["end"])))      # in a removed stretch: snap to the nearest kept edge
    return round(n["out"] + min(max(t, n["start"]), n["end"]) - n["start"], 3)

norm = lambda t: re.sub(r"\W", "", t).lower()
FIXES = cfg.get("word_fixes", [])
def fix(ws):
    out, i = [], 0
    while i < len(ws):
        for pat, rep in FIXES:
            if [norm(w["text"]) for w in ws[i:i + len(pat)]] == [norm(x) for x in pat]:
                grp = ws[i:i + len(pat)]; a0, b0 = grp[0]["start"], grp[-1]["end"]
                for k, r in enumerate(rep):
                    out.append(dict(text=r, start=a0 + (b0 - a0) * k / len(rep), end=a0 + (b0 - a0) * (k + 1) / len(rep)))
                i += len(pat); break
        else:
            out.append(ws[i]); i += 1
    return out

CHARS, LOOK = cfg.get("sub_chars", 36), cfg.get("sub_lookback", 0.4)
subs = []
for s in segs:
    ws = [dict(w) for w in words if s["start"] - LOOK <= w["start"] < s["end"] - 0.05]
    if not ws: continue
    for w in ws: w["start"] = max(w["start"], s["start"]); w["end"] = max(w["end"], w["start"] + 0.05)
    ws = fix(ws)
    ws[0]["text"] = ws[0]["text"][0].upper() + ws[0]["text"][1:]
    sent, sents = [], []
    for w in ws:                                   # sentences -> balanced lines
        sent.append(w)
        if re.search(r"[.?!]$", w["text"]): sents.append(sent); sent = []
    if sent: sents.append(sent)
    for sent in sents:
        chars = len(" ".join(w["text"] for w in sent)); n = max(1, -(-chars // CHARS)); target = chars / n
        line, lines = [], []
        for w in sent:
            cur = len(" ".join(x["text"] for x in line))
            if line and len(lines) < n - 1 and cur + len(w["text"]) / 2 >= target: lines.append(line); line = []
            line.append(w)
        lines.append(line)
        for l in lines:
            subs.append(dict(start=to_out(l[0]["start"]), end=to_out(min(l[-1]["end"] + 0.2, s["end"])), text=" ".join(x["text"] for x in l)))
for a_, b_ in zip(subs, subs[1:]):
    if a_["end"] > b_["start"] or b_["start"] - a_["end"] < 0.3: a_["end"] = b_["start"]

def cue(spec):
    if "time" in spec: return to_out(spec["time"])
    hits = [w for w in words if w["start"] >= spec.get("after", 0) and norm(w["text"]) == norm(spec["word"])]
    if len(hits) <= spec.get("nth", 0): raise SystemExit(f"cue word not found: {spec}")
    return to_out(hits[spec.get("nth", 0)]["start"])
C = {k: cue(v) for k, v in cfg.get("cues", {}).items()}
C["end"] = round(total, 3)

json.dump(dict(fps=FPS, total=round(total, 3), source=cfg["source"], segs=segs, subs=subs, cues=C), open(f"{E}/timeline.json", "w"), indent=1)
def ts(t): return "%02d:%02d:%06.3f" % (int(t // 3600), int(t % 3600 // 60), t % 60)
open(f"{E}/master.srt", "w").write("".join("%d\n%s --> %s\n%s\n\n" % (i + 1, ts(s["start"]).replace(".", ","), ts(s["end"]).replace(".", ","), s["text"])
                                           for i, s in enumerate(subs)))
print("total %.2f s, %d takes, %d subtitle lines" % (total, len(segs), len(subs)))
print("cues", C)
for s in subs: print("%6.2f-%6.2f %s" % (s["start"], s["end"], s["text"]))
