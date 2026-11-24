# Platform limits and link rules

Platforms change these without notice and roll changes out by region. Use them as starting values and tell the user to trust the app's own edit screen when it disagrees.

## Text limits

| Field | Instagram | TikTok | YouTube | Facebook Page |
|---|---|---|---|---|
| Name | 2 changes per 14 days | 30 characters; 1 change per 7 days | 2 changes per 14 days | |
| Username | reclaimable for 14 days after a change | 1 change per 30 days | handle: 2 changes per 14 days | |
| Bio or description | 150 characters | 80 characters | 1,000 characters; the first sentence shows in search | |
| Link title | | | 30 characters | |
| Caption | 2,200 characters | about 4,000 | 5,000; title 100 | long |
| Hashtags | 3 to 5 | 3 to 5 | first 3 show above the title | 2 or 3 |

Count emoji as two characters when a bio is near its limit.

## Where a store link can be tapped

| Place | Instagram | TikTok | YouTube | Facebook |
|---|---|---|---|---|
| Profile | Links field (Edit profile → Links), any account, up to five | Website field: Business account, or a personal account past 1,000 followers | Channel links; the first shows on the banner | Page link |
| Post text | no | no | regular-video description; not Shorts descriptions | yes |
| Comments | no | no | regular-video comments; not Shorts comments | yes |
| Other | Story link sticker | Instagram and YouTube buttons on the profile | end screens allow videos and playlists only | |

- **Instagram** shows a single link as its raw address, whatever title it was given. That is the reason to use a short link on the app's own domain.
- **YouTube Shorts:** external URLs in descriptions and comments are not clickable. Use a channel profile link as the tappable route. Check [YouTube's link guidance](https://support.google.com/youtube/answer/13748639) when preparing a post.
- **TikTok Business accounts** lose most trending sounds. In some regions there is no plain switch, only "Become a Verified Business Account", which asks for a company address and registration documents. Without a registered business the user stays personal: connect Instagram and YouTube to the profile, put the web address in the bio as plain text, and wait for 1,000 followers. Never suggest entering business details that are not real.
- **Location.** No platform has a setting that aims an account at a country. YouTube's country field is where the owner lives and is tied to payments. What moves the audience is language, units, posting hours, and who the account follows and engages with.
- **Following far above followers** reads as follow-for-follow. Unfollowing is safe at roughly 50 to 100 a day by hand; bulk tools get accounts blocked.

## YouTube banner

- Upload 2560×1440, 6 MB or less.
- Shown on every device: the centre 1546×423. Tablets show 1855×423, desktop up to 2560×423, a TV the whole image.
- Profile pictures on every platform are shown as a small circle: the logo alone on a plain background.

## App Store campaign links

`https://apps.apple.com/app/apple-store/id<APP_ID>?pt=<PROVIDER_ID>&ct=<CAMPAIGN>&mt=8`

- `pt` identifies the developer account and must be exact. `ct` is free text, at most 30 characters; letters, digits and underscores.
- A misspelled `ct` is counted as a separate campaign.
- The link opens the App Store on an iPhone. On a Mac, an iPhone-only app shows an error, which is not a broken link.
- Installs from people who search the store by name are counted as search, not under any campaign. On Instagram and TikTok that is most of them.
