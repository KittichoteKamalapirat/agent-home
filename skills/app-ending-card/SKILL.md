---
name: app-ending-card
description: Makes a short animated ending that promotes the user's app at the end of a vertical social video, one version per platform (Instagram, TikTok, Facebook, YouTube). It shows the taps that send this very video to the app, the saved result, then a closing screen with the app's name, store badge and web address. For recipes it can also show the ingredients the app pulls out of the video. Use when the user wants to tie their app into a cooking, recipe or other content video, asks for an outro, end card or call to action for a Reel, TikTok or Short, or wants the same ending for a new video.
---

# App ending card

A 5-second (or 6.5-second with ingredients), 1080×1920 ending the user places on top of their own edit. It never touches their project: the output is a transparent clip with sound, one per platform.

1. **0 to 3.1 s, over the video's final shot.** A card names the action ("Save this recipe to <App>"), shows that platform's three taps with a finger pressing each, then turns into the saved item with its name and a thumbnail from the video.
2. **3.1 to 5 s, full frame.** White grows from the logo and covers the frame: logo and app name, store badge, web address. The logo hops with a short beep.

## What to gather

- **The app:** name, logo without a background (SVG or PNG), store badge artwork and web address, all from the user's project. Take the accent colour from its design guide.
- **This video:** the item's name and a square thumbnail cropped from the final shot. If the user's editor is open, look at the last frame without changing the project; only move the playhead, and put it back.
- **The share steps:** `scripts/page/platforms.json` holds the usual two taps before choosing the app. If the app ships its own "how to share" tutorial, read it and make the steps match.

## Make it

Create a work folder holding the files above and a `card.json`:

```json
{
  "app": "Piiman",
  "logo": "logo.svg",
  "headline": "Save this recipe to Piiman",
  "savedLabel": "Saved to Recipes",
  "item": { "name": "Chipotle Bowl", "image": "dish.jpg" },
  "badge": "badge.svg",
  "url": "piiman.app",
  "brandIcons": { "tiktok": "tiktok.svg" },
  "accent": "#64cb3c",
  "accentText": "#285b32"
}
```

`badge`, `url`, `brandIcons`, `accent` and `accentText` are optional. Add `bg.png` (the final frame at 1080×1920) to also get a preview over the real shot.

### Ingredients variant (6.5 s)

For a recipe, the ending can also show that the app pulls out the ingredients. Add `ingredients` to `card.json`, and the saved item opens upward into an "Ingredients found" grid before the closing screen:

```json
"ingredients": {
  "total": 14,
  "items": [
    { "icon": "icons/beef.png", "name": "Beef", "amount": "150g" },
    { "icon": "icons/green-pepper.png", "name": "Green pepper", "amount": "5" }
  ]
}
```

- Up to 8 items are shown, in two rows of four. `total` counts every ingredient in the recipe, so "14 items" stays true when some have no icon. `amount` is optional, and `title` replaces "Ingredients found".
- Use the app's own ingredient icons, at their source resolution (around 400px). App asset catalogs are often only 72px and look soft at 150px. Leave out an ingredient that has no icon rather than using a near miss, such as a shellfish icon for oyster sauce.
- Use the same names and amounts as the video's cards and captions. Keep the names general ("Beef", not the cut), unless the user wants the cut named.
- The card grows upward over the frame, so the final shot's food needs to sit in the upper third.
- `make.sh` sees `ingredients`, then makes the 6.5 s clip and its matching sound (`audio.mjs <out> ingredients`). The closing screen starts at 4.6 s instead of 3.1 s. If you build a sound by hand, take it from this variant: the 5 s sound's beeps land 1.5 s early.
- **Every video needs its own overlay.** The dish name, thumbnail and ingredient list change with each recipe. Keep `card.json` and the icons with that video's work files, render the platforms again, and never reuse another dish's overlay.

```bash
scripts/make.sh <work-dir>
```

That renders all four platforms into `<work-dir>/out`; name platforms after the folder to render fewer. It uses the frame-capture tool from the `dev-vlog-editing` skill, which is installed alongside this one.

## Attach it to a finished video

When the user has exported their video and wants finished files, one per platform:

```bash
scripts/append.sh <video> <work-dir>/out/ending-<platform>-overlay.mov <out.mp4>
```

The video's last frame is held under the card, so the result is longer by the ending's length and nothing in their edit is covered. The output keeps the video's size, frame rate and colour.

- **iPhone HDR (HLG) exports.** A card converted at the standard level looks grey beside bright food and plates. The script reads how bright the footage's whites are and matches the card to them; it prints the level it chose. Dolby Vision metadata is dropped and the file stays plain HLG. Tell the user.
- **Check a frame from each half** of the ending in every output: the card over the held shot, and the closing screen. For HLG, view frames through a tonemap; a raw frame grab looks washed out and proves nothing.
- The file name of an export can state a different length than the file has. Report the measured duration.

## Check before handing over

- Extract frames from a preview at about 0.7, 1.3, 1.8, 2.5 and 4.5 s and look at them: the headline fits on one line, the ring is on the right step, the thumbnail is the dish, the closing screen is centred.
- The headline must stay under about 26 characters at this size. Shorten the wording before shrinking the type.
- Say which checks were not possible: the sound has not been listened to, and whether the user's editor accepts a transparent clip is unknown until they try. If it does not, attach the ending to their exported video as above.

## Guidance to give the user

- Put the card over the final food shot, with no separate black outro before it. The closing screen runs past the end of their video by 1.9 s.
- A shorter version exists by design: delete the closing screen by setting `out` and `end` in `scripts/page/timing.json` to the same value, about 2.5 s.
- The card is a template. For the next video, `item` changes, and so does `ingredients` when that variant is used. Render every platform again for each video.
- Pair it with a caption line and a pinned comment carrying the store link, since viewers who leave early never see the ending.
- Each platform gets its own file, since each ending shows that platform's share steps. Captions and links per platform are covered by the `app-social-profiles` skill.
