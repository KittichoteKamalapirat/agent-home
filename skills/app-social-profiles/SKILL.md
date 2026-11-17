---
name: app-social-profiles
description: Sets up or rebrands the social accounts that promote the user's app (Instagram, TikTok, YouTube, Facebook) and writes what gets pasted into them. Covers account name, username, bio and channel description within each platform's limits, where a store link can be tapped, campaign names and short links for counting installs per platform, a YouTube channel banner, and per-platform captions for a video. Use when the user asks for a bio, handle, channel name or description, a channel banner, a link in bio, campaign or UTM tracking for an app link, captions or descriptions for posting a video to several platforms, or wants an existing account reviewed.
---

# App social profiles

The accounts exist to send people to the app's store page. Every choice below serves one of two routes there: a link someone can tap, or a name someone can search.

## 1. Look before writing

- Open the live profile in the browser and read it: name, bio, link, follower and following counts, the language of the existing posts. Advice written without looking is generic.
- Check candidate usernames by opening their profile URLs. "Page isn't available" usually means free, but banned and reserved names look the same; the real test is the platform's own username field. Say so.
- Find out how the app charges. If it has a paywall with a trial, never write "free"; write "try it free".

## 2. Name, username, bio

Give one recommendation per field, ready to paste, with the character count wherever a limit is close. Limits and link rules are in [PLATFORMS.md](PLATFORMS.md); they change, so treat a rejected save as the platform's answer.

- **Name:** `<App> | <two searchable words>`. The name field is searched, and the app's name alone means nothing to a stranger.
- **Username:** the same on every platform. Prefer `<app>app` over `<app>.app`: dots are not allowed everywhere, break mentions, and read as a web address.
- **Bio:** line one says what the channel gives the viewer, line two what the app does, line three points at the link. Reword per platform ("Reel", "Short", "video").
- Names and handles can only be changed a few times per fortnight. Settle them before the user saves.

## 3. Links

- A link only counts where it can be tapped. PLATFORMS.md lists where that is. Text in a bio, caption or comment is not tappable on Instagram or TikTok.
- **Campaigns.** An App Store link takes `?pt=<provider id>&ct=<name>&mt=8`. `ct` needs no setup in App Store Connect; any value of at most 30 characters is recorded. Name them `<platform>_<placement>` (`ig_channel`, `yt_channel`). A campaign shows in analytics only after five installs, so per-video campaigns are rarely worth it early on.
- **Short links.** A raw store address is long and gets cut off on a profile. Add temporary (307) redirects on the app's own site, one per platform (`/ig`, `/tt`, `/yt`, `/fb`), each pointing at the store link with its campaign. Ship them through the project's normal release path and request each one on the live site before telling the user to use it.
- The provider id is visible to anyone who follows the link, but keep it out of public repositories and skills all the same; read it from the user's own link.

## 4. Channel banner

Write a `banner.json` beside the logo and any images, then:

```bash
scripts/banner/render.sh <work-dir> <out.png>
```

```json
{
  "app": "Piiman", "logo": "logo.svg", "layout": "center",
  "tagline": "Easy recipes you'll actually cook", "highlight": "actually cook", "accent": "#1f922e",
  "badge": "app-store-badge.svg",
  "background": { "color": "#f4f8ef" }
}
```

- `layout` is `center` or `split` (text left, `side` image right). Optional: `sub`, `icons` (a row of small images), `decorations` (`image, x, y, width, rotate`), `text: "light"`, `background.image` with `background.scrim` (a colour such as `rgba(255,255,255,.85)`).
- Only the middle 1546×423 is shown on every device. Render once more with `guide` as the third argument and look at it: text, logo and badge inside the inner box.
- Use the app's real logo and type; image models misdraw both. A generated image is fine as a background only, and comes out small, so say it is enlarged.
- Offer three or so variations, state which you would pick and why, and never overwrite one the user liked: add a new numbered file.
- A banner cannot be tapped. A store badge on it only says "this is an iPhone app"; the tappable link is the channel's first link.

## 5. Captions for a video

- One shared body, with the opening line, the call to action and the hashtags changed per platform. Give each platform's caption whole, in its own code block, so it can be pasted without assembling.
- For a recipe or how-to, put the full content in the caption. It earns saves, and it is what the app reads when the video is shared to it.
- The call to action follows the link rules: a real link on YouTube and Facebook, "link in bio" on Instagram, the share steps on TikTok.
- Translate for the audience: units, ingredient names, an unfamiliar word explained once.

## 6. Reviewing an existing account

Report what a stranger sees in the first two seconds, most useful fix first: a link shown as a raw address, a grid in another language, following far above followers, a missing category. When an account is renamed for a new audience, say plainly that its current followers will drag early reach, and give the trade-off against starting fresh.
