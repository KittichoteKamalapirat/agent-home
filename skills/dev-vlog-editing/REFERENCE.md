# Dev vlog editing: reference

`S` is this skill's `scripts` folder. `<edit>` is the edit folder for one video.

## Files in the edit folder

| File | Written by | Purpose |
|---|---|---|
| `audio16k.wav`, `silences.txt` | `prep.py` | Speech audio and every pause of 0.45 s or more (start, end, length) |
| `transcript.json`, `takes.md` | `transcribe.py` | Words with times; one line per phrase for reading |
| `edit.json` | you | Every editing decision |
| `timeline.json`, `master.srt` | `build_timeline.py` | Kept takes on the output timeline, subtitle lines, cue times |
| `clips/`, `base.wav`, `base.mkv` | `render_base.py` | The cut without graphics |
| `overlay/`, `frames/` | you, `capture.mjs` | The graphics page and its transparent frames |
| `verify/` | `check_cuts.py` | Sheets to look at |

## edit.json

All times are seconds in the source video.

```json
{
  "source": "/path/to/footage.MOV",
  "ranges": [[0.46, 7.95], [17.88, 24.25]],
  "hard_cut_after": [],
  "word_fixes": [[["bimang"], ["Piiman,"]], [["gonna"], ["going", "to"]]],
  "drop_words": [[10.6, 20.0]],
  "extra_words": [["And", 17.88, 18.10]],
  "cues": { "hook": { "word": "decide" }, "hook_out": { "time": 26.05 }, "goal": { "word": "100", "after": 325 } }
}
```

- **ranges**: the kept takes in story order. Put each start and end on a pause edge from `silences.txt`. The script then tightens each edge to where the voice measurably starts and stops, pads it, and overlaps the sound of neighbouring takes.
- **hard_cut_after**: indexes of takes that end on speech because the next word was a mistake. They get no end pad and no sound overlap. Tell the user about each one.
- **word_fixes**: heard tokens and their replacement, matched on letters and digits only. Use it for the app's name, misheard words, and wording the user prefers.
- **drop_words** and **extra_words**: remove words the model invented or placed in a removed take, and add words it missed.
- **cues**: named moments for the graphics. `word` finds the first matching word at or after `after`; `nth` picks a later match; `time` is a fixed source time. A time inside a removed stretch snaps to the nearest kept edge.
- Optional: `fps` (30), `pad_in` (0.08), `pad_out` (0.12), `overlap_frames` (4), `sub_chars` (36), `sub_lookback` (0.4), `tighten_db` (-38). Raise `sub_lookback` when the first word of a take is missing from its subtitle.

## Graphics page

`overlay/index.html` draws one frame for any time: it defines `seek(t)` and `window.ready`. Nothing may animate on its own, so use the helpers (`panel`, `rise`, `pop`, `chip`, `phone`, `draw`, `slide`) and derive every position from `t`.

- Start a graphic on the cue for the word it illustrates and hold it until the topic changes. Bring in one new thing at a time.
- Set `--side-x` to the left edge of the empty side of the frame.
- App recordings: extract 30 frames per second as `rec/<name>/001.jpg` (600×1304 for a phone) and list them in `RECORDINGS`.
- Subtitles are the last element in the page so they sit above every graphic.

Check stills first, then capture:

```bash
node $S/capture.mjs --page <edit>/overlay --out <edit> --file /timeline.json=<edit>/timeline.json --mount /rec=<edit>/rec 5.5 20 61
```

```bash
node $S/capture.mjs --page <edit>/overlay --out <edit> --file /timeline.json=<edit>/timeline.json --mount /rec=<edit>/rec all
```

Add `--mount /assets=<project assets folder>` to reuse the project's own images and stylesheets. `all <from> <to>` re-captures a frame range after changing one scene; `compose.py` then rebuilds the video without re-rendering the cut.

## Things that go wrong

- **The speech model skips a retake.** Speech between two silences with no words in `takes.md` means missed words. Re-transcribe that stretch: `transcribe.py <edit> <model> <start> <end>` prints the words to add as `extra_words`.
- **Invented words over silence**, often "Thank you" at the very end. Remove them with `drop_words`.
- **A pause survives a cut.** Silence detection treats a quiet breath as speech. `build_timeline.py` prints each range it tightened; check `check_cuts.py` afterwards.
- **iPhone footage is HDR.** `render_base.py` tone-maps HLG to SDR. Check skin tone on the first render.
- **A larger speech model is not cached.** The default small model runs offline with `HF_HUB_OFFLINE=1`. Downloading a larger one can stall; do not wait on it.
- **Changing one take shifts everything after it.** Rebuild the timeline, then re-capture all frames from the changed cut onward.
