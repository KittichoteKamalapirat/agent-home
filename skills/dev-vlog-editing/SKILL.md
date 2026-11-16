---
name: dev-vlog-editing
description: Edits one-take talking-head footage into a finished dev vlog for YouTube. Removes retakes and pauses, burns in subtitles, adds on-screen graphics that show the app being discussed, then makes the thumbnail and the upload kit (title, description, chapters, subtitle file). Use when the user shares raw footage of themselves talking about an app they are building, or asks for a dev vlog, a build-in-public video, a YouTube thumbnail, or a YouTube description for one.
---

# Dev vlog editing

Turn raw footage of the user talking to camera into a video they can upload, plus everything YouTube asks for. Go straight to a first cut with the defaults below, show it, and take notes from there. Do not stop to confirm a plan first.

## The user's standing preferences

- **Last take wins.** When a sentence is said more than once, keep the final attempt and remove every earlier one, including a single repeated word at the start of a take.
- **No dead air.** Cut the pauses between sentences. Let each sentence's sound start a moment before the previous one has faded out (the scripts do this). Do not overlap actual words.
- **No zoom on the speaker.** Every shot keeps the same framing. Do not punch in to hide cuts.
- **Subtitles are burned in.** The user is not a native English speaker. Also deliver the subtitle file for YouTube.
- **Graphics go on the empty side of the frame** and match what is being said at that moment: a card for a claim or a number, a phone showing the app for a feature.
- **Show the real app.** Use real screen recordings or simulator captures, not mock screens. Keep a widget or small control at its real size; a gentle push-in (about 1.4×) is the most to add.
- **Normal speaking pace.** Do not speed the video up. Offer 1.1× only if the user says it feels slow.
- **Title and thumbnail must match what the video is mostly about**, not its last ten seconds. A stronger hook that the video does not deliver belongs to a later episode.

## Workflow

Work in an edit folder inside the user's project (for example `vlog-edit/<video-name>/`). `S` is this skill's `scripts` folder. Run long renders in the background.

1. **Prepare.** `python3 $S/prep.py <source> <edit>` then `uv run --with mlx-whisper python $S/transcribe.py <edit>`. Read `takes.md` and `silences.txt`.
2. **Choose takes.** Compare `takes.md` with the silences: any stretch of speech the transcript skips is a retake the speech model missed, so re-transcribe that stretch. Write the kept ranges, word corrections and cue words into `<edit>/edit.json`. See [REFERENCE.md](REFERENCE.md) for the fields.
3. **Build the cut.** `python3 $S/build_timeline.py <edit>` and read the printed subtitles in full. Fix misheard names and dropped words in `edit.json`, then run it again. `python3 $S/render_base.py <edit>` renders the cut.
4. **Add graphics.** Copy `$S/overlay-starter` to `<edit>/overlay` and write this video's scenes, keyed to cues. Use the project's own design guide, logo, colours and app recordings. Check stills before a full capture, then capture every frame. Commands are in [REFERENCE.md](REFERENCE.md).
5. **Compose and check.** `python3 $S/compose.py <edit> <edit>/<name>.mp4`, then `python3 $S/check_cuts.py <edit> <video>`. Look at every sheet in `<edit>/verify`.
6. **Thumbnail and upload kit.** Follow [YOUTUBE.md](YOUTUBE.md).

## Before showing the result

- Every cut in `verify/cuts-*.jpg` shows the same framing on both sides and no half-finished gesture.
- `check_cuts.py` reports no pause longer than about 0.25 s. A longer one usually means a breath before a sentence; tighten that range.
- Each graphic in `verify/moments.jpg` is on screen while its sentence is spoken, and no subtitle is hidden.
- The subtitles read correctly from first line to last, with the app's name spelled right.
- The file's length matches the timeline's total.

## Reporting

- Say plainly that the audio has not been listened to. Frames and loudness can be checked; how a cut sounds cannot.
- Name any cut that lands between two close words, and any line where the wording in the subtitles differs from what was said.
- A finished file larger than the chat's attachment limit stays on the computer: give its path and copy it to Downloads.
- List anything changed on a simulator or device while capturing, and put it back if asked.
