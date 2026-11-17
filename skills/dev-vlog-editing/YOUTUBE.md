# Thumbnail and upload kit

`S` is this skill's `scripts` folder.

## Thumbnail

1. **Pick the frame.** Look for a moment where the speaker faces the camera with nothing covering the face: usually just before the first word or just after the last, when the microphone is lowered. Extract it at full resolution with the same colour treatment as the video.
2. **Cut out and blur.** `$S/thumb/cutout.sh <frame.jpg> <thumb-dir>` writes the speaker on transparency and the room blurred without them.
3. **Render variations.** Copy the app icon and one real app screenshot into the thumb folder, then:

```bash
$S/thumb/render.sh <thumb-dir> out.jpg "t1=No more&t2=what do I eat today?&icon=icon.png&phone=shot.jpg"
```

Parameters: `t1` white line, `t2` highlighted line, `icon`, `phone`, `iconw` (default 255), `dim` (default 0.4), `blur=0` for the sharp frame, `side=left` when the speaker sits on the right, `label` for a series tag such as "Building X / ep. 2", `hl` for another highlight colour.

Make three or four with different words, look at each one, and recommend one. What has worked for this user: a blurred, moderately darkened room; the speaker's real face, not a mascot over it; a large app icon overlapping the phone; a short white line plus a yellow highlighted phrase of two to five words.

## Title

The title and the thumbnail are read together, so each should say what the other leaves out. Keep the title under about 60 characters. Measure both against the video: if the hook covers only the closing seconds, propose it as the next episode and choose words that fit this one.

## Description

```
<Two sentences: the problem and what the user built.>

<One sentence saying what the app is and who it is for.>

Download <App> (<platform>): <App Store campaign link>
Website: <site>

In this video:
0:00 <chapter>
...

<One line inviting feedback.>

#<tag> #<tag> #<tag>
```

- **Chapters** come from the cue times in `timeline.json`. The first must be 0:00, there must be at least three, and each must last 10 seconds or more. Recompute them whenever the cut changes.
- **App Store link.** Use the country-neutral form `https://apps.apple.com/app/id<ID>` and find the ID in the project, not from a pasted storefront link. For tracking, add a campaign to the link (`?pt=<provider id>&ct=<name>&mt=8`). The name needs no setup in App Store Connect: any `ct` of at most 30 characters is recorded, one per video (`yt_ep1`). Results appear only after five installs. Naming and short links are covered by the `app-social-profiles` skill. The link opens the App Store on an iPhone; on a Mac an iPhone-only app shows an error, which is not a broken link.

## Upload steps to tell the user

- **Subtitles:** upload `master.srt` as English "with timing", even though subtitles are burned in. It gives YouTube the correct spelling of the app's name for search and translation. The option is greyed out until the video has finished processing and its language is set.
- **Playlist:** one per project, named "Building <App>", with a description that states the goal of the series.
- **End screen:** YouTube requires a video or playlist element. Add the series playlist and a Subscribe button for the last 6 seconds, placed so they cover neither the face nor the final graphic. Outside links are not allowed there, so the store link goes in the description and a pinned comment.
- **Audience:** not made for kids. Category: Science & Technology.
