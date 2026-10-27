# TikTok daily pack (for the scheduled "GRIND TikTok daily" agent)

The owner posts 3 TikToks per day MANUALLY from TikTok Studio and schedules all 3 from this pack. Nothing here goes through Make.com. This pack never changes the Instagram pipeline: do not edit RUNBOOK.md, log.md, insights.md, or anything under `queue/`. Write only under `tiktok/` (and `work/`, never committed).

Brand, hook and intrigue rules come from STRATEGY.md (read it). TikTok captions follow section 5 below, NOT STRATEGY section 7. Account: personal TikTok account, no clickable link, so captions say "link in bio" at most and never contain a URL.

## What week 1 showed (owner export, Oct 18 to 24, 2026) and why the rules changed
- Photo posts beat videos: avg 377 views (median 254) and 3.7% likes vs 162 views / 1.5% for TikTok-only videos and 192 / 0.9% for Instagram reels. Best post: the "4 midterm mistakes" photo post, 780 views, 36 likes.
- Videos stall at 120 to 280 views (TikTok's first test pool): viewers leave in the first seconds.
- Product-led posts were the bottom three (118 to 142 views). Pure-advice posts did best.
- Best video topic: grade math ("Do this math before your final", 259).
- 0 comments, 1 share, about 2 profile views a day: nothing turns views into follows.
Small sample (one week, one outlier). Owner decision 2026-10-26: run the plan below as a TEST WEEK, Oct 27 to Nov 2, 2026, then compare with the next export.

## 0. Setup
```bash
cd /home/claude && git clone https://github.com/mdouiri19-del/grind-social && cd grind-social
# EVENING MODE (owner decision 2026-10-22): the run fires around 21:20 Toronto and prepares TOMORROW's pack, delivered by 22:00.
DAY=${DAY:-$(TZ=America/Toronto date -d tomorrow +%F)}
[ -f tiktok/$DAY/plan.txt ] && echo "TikTok pack already done" && exit 0
mkdir -p tiktok/$DAY work
export HYPERFRAMES_SKIP_SKILLS=1
export HYPERFRAMES_BROWSER_PATH=$(ls -d /opt/pw-browsers/chromium-*/chrome-linux*/chrome | head -1)
(cd work && npm init -y >/dev/null && npm i gsap@3.13.0 --silent && cp node_modules/gsap/dist/gsap.min.js gsap.js)
```

## 1. The 3 posts (2 photo posts + 1 short video, updated 2026-10-26)
- Slot A: UPDATE 2026-10-28: the Instagram carousel is PAUSED (owner decision), so from 2026-10-28 there is no `post_0N.jpg` in queue/$DAY. Slot A is then always a second TikTok-only photo post (`photo_a_01..06.jpg`, a different idea from slot B, made the same way as slot B), and the wait for the manifest below is not needed for slot A. Old rule, only if `post_01.jpg` exists: DAY's Instagram carousel `queue/$DAY/post_01.jpg..post_06.jpg`, upscaled to `tiktok/$DAY/photo_01.jpg..photo_06.jpg` (2160x2700, lanczos), posted as a TikTok PHOTO post.
- Slot B: a TikTok-only PHOTO post you make, `tiktok/$DAY/photo_b_01.jpg..photo_b_06.jpg` (section 2). Part of the running series (section 4).
- Slot C: a TikTok-only SHORT VIDEO you make, `tiktok/$DAY/tiktok_video.mp4` (section 3).
- The Instagram reel `queue/$DAY/reel.mp4` is NOT posted on TikTok during the test. It is only the fallback for slot C if your video breaks and you cannot fix it (say so in plan.txt and the final message).
- The Instagram run for $DAY starts around 20:45 the evening before and is usually done before this run. If `queue/$DAY/manifest.json` does not exist yet, `git pull` every 5 minutes for up to 30 minutes. If it is still missing, make slot A a second TikTok-only photo post (`photo_a_01..06.jpg`, different idea) and keep going.
- The 3 posts of a day are 3 different ideas: read `queue/$DAY/meta.json` and never repeat its hooks or topics. Never reuse a hook from `tiktok/log.md` or `log.md` in the last 30 days.

## 2. Slot B: TikTok-only photo post
- 6 slides, 1080x1350 HTML sections `#s1..#s6`, rendered with `python3 tiktok/tools/render_photos.py work/photos/slides.html tiktok/$DAY` (device scale 2, writes photo_b_01..06.jpg at 2160x2700). Mechanics and layout reference: `tiktok/templates/photos-example.html` (never reuse its words; vary background colors and the visual on each slide day to day). Fonts: `assets/fonts` (adjust relative paths if the HTML lives in work/).
- LIST FORMATS ONLY (the week 1 winner): "X mistakes that cost marks", "do these 4 things next", "the plan, day by day", "X signs you...", "before / after your midterm", "X things I'd do in week N". Rotate the format; do not use the same format two days in a row.
- Slide 1: series pill (section 4), hook of 8 words max that opens a loop (never states the answer), one teaser line ("Number 3 is the one everyone skips."). Slides 2 to 5: one point each, big number, a short headline with a lime highlight, max 25 words, optional ONE small visual (a deadline card, a weight pill, a tiny grade calc with SAMPLE label). Slide 6: save ask + "Follow for part N+1" + the ONLY product line ("GRIND. keeps every deadline and weight from your syllabus in one list. Free, link in bio." or a close variant naming one real feature).
- Text big enough to read on a phone without zooming: body 44px minimum, headlines 90px or more. LOOK at all 6 slides before committing: no overflow, no overlap, nothing clipped.
- Topics: study systems, deadline reality, grade math, semester moments (STRATEGY sections 2 and 8). Advice must be honest and general; numbers are structural or labelled sample.

## 3. Slot C: TikTok-only short video
- 10 to 15 s (was 15 to 25). HyperFrames in `work/reel3/` (copy `work/gsap.js` and `assets/fonts` next to index.html). Mechanics as in RUNBOOK section 2 and `templates/reel-example/index.html`; look as in STRATEGY section 12. GX effects are optional here (at most the glass graph, only if it fits in the time).
- TOPIC: grade math on at least 4 of the 7 days (week 1's best video topic): "what do I need on the final", a 10% quiz, weighted average traps, drop-the-lowest, a bonus 2%. Other days: deadline reality or study systems, still a number-driven idea. Different idea from the day's Instagram reel and carousel.
- STRUCTURE (the payoff must come early, week 1 videos lost viewers in the first seconds):
  - 0.0 to 1.2 s: hook, max 6 words, motion from frame 0, full hook readable and still from 0.8 s to 2.0 s (TikTok cover at 1 s).
  - by 3.0 s: the ANSWER or key number is on screen ("79.5, not 100."). No slow tension build.
  - 3 to 11 s: the why in 2 beats max (the math line, one tip).
  - last 2 to 3 s: calm outro: GRIND. wordmark + ONE short line written fresh for the idea (never "Your semester. A little more under control.", never an outro line from the last 14 days in tiktok/log.md) + "Free · link in bio" + "Follow for more" small. Vary background (cream, blush, green) and layout day to day.
- Dynamic edit as before: word slams on the beat, whole-stage push/pan, beat pump, a wipe or flash on every cut, one pattern interrupt, count-up or partial reveal of the key number. No wipe, shake or pump on the outro.
- Music: new original track with `tools/score.py`: `python3 tools/score.py work/beat3.wav <dur> --seed <YYYYMMDD of $DAY + 1000> --style <deephouse|lofi|pop> --bpm <bpm> --cuts <cut times> [--brk start,end] [--drop t] --end <dur - 1.0>`, style different from the day's Instagram reel; build the timeline on B = 60/bpm. Note the printed `score:` line as `music:` in tiktok/log.md. Mux: `ffmpeg -y -i work/reel3_video.mp4 -i work/beat3.wav -c:v libx264 -preset slow -crf 20 -pix_fmt yuv420p -c:a aac -b:a 128k -ar 44100 -ac 2 -af "volume=0.5" -shortest -movflags +faststart tiktok/$DAY/tiktok_video.mp4`
- SOUND TEST: on EVEN dates of $DAY the plan tells the owner to add a trending sound in TikTok Studio and set the original sound to 0%; on ODD dates the original track stays and no sound is added. Log which one in tiktok/log.md ("sound: trending" or "sound: original").
- Checks: lint errorCount 0, LOOK at the snapshot contact sheet and at 3 frames plus the 1.0 s and 3.0 s frames (hook readable at 1.0 s, answer visible at 3.0 s). Fix overflow, overlap, clipped or tiny text, more than 6 words on screen. 1080x1920, h264 + aac, 10 to 15 s, under 19 MB.

## 4. The series (follow driver)
- Slot B photo posts form a numbered series shown as a pill on every slide and in the caption's first line: "Midterm survival · N/7" until Nov 15, 2026, then "Finals survival · N/7" until Dec 20, then pick a season-fitting name (STRATEGY section 8).
- N continues from the last series entry in tiktok/log.md (1 to 7, then a new 7 starts at 1). Slide 6 says "Follow for part N+1" (after part 7: "Follow for the next one").

## 5. Captions (all 3 posts)
- First line = the hook, written with words students actually search: "how to study for a midterm", "what do I need on my final", "how to plan an essay", "weighted average". Series posts start with "Midterm survival N/7:".
- Then 1 to 2 short lines of pure advice. NO product, no feature names, no "GRIND." in TikTok captions (week 1: product-led posts were the bottom three). The product lives only on the last slide or the outro card. End the advice with "link in bio" at most.
- ONE question that can be answered in one word or number: "Which one are you, 1, 2 or 3?", "A or B?", "Comment the number you need on your final", "Comment your worst day this week". Never an open "How do you usually...?" question.
- 4 hashtags: #studytok + 3 niche ones from the topic (#midterms #grademath #studytips #universitylife #activerecall #examprep #collegetips #studentlife). No #fyp, #foryou or #foryoupage.
- Emoji: one at most, after the hook.
- "Pin comment:" line per post: a short first comment the owner posts and pins right after publishing, easy to answer ("Drop your number below 👇", "Which slide hit hardest? 1 to 5", "Part N+1 tomorrow, what should it cover?"). Never promise personal advice or replies to everyone.

## 6. Timing (Toronto). Unchanged for the test; adjust from results once the owner shares them.
Slot times follow $DAY's weekday (the day the posts go live).
- Mon to Fri: 12:30 slot A (photos) · 16:30 slot B (photos, series) · 20:30 slot C (video)
- Sat, Sun: 11:00 slot A (photos) · 15:30 slot B (photos, series) · 20:00 slot C (video)

## 7. plan.txt
Write `tiktok/$DAY/plan.txt` (plain text, no em dashes):
- Line 1: "Settings for every post: Everyone, comments on, Disclose post content > Your brand, AI-generated off."
- Line 2: "After posting: pin the comment below on each post, and reply to the first comments with a video reply when one asks a question."
- Per slot: time, type and file paths, then "Title:" (photo posts only, under 90 characters), the caption (section 5), the hashtags, "Pin comment: ...", and the sound line: photo posts "add a calm trending sound"; the video "(cover at 1 s)" plus the day's sound test ("add a trending sound, set original sound to 0%" on even dates, "keep the original sound, add nothing" on odd dates).

## 8. Publish and deliver
- Append a row to `tiktok/log.md`: date | slot A | slot B | slot C (time + hook each) | series: <name N/7> | format: <list format> | outro: "<line>" | music: <score line> | sound: <trending|original>.
- `git add tiktok/ && git commit -m "TikTok $DAY" && git pull --rebase -q origin main && git push -q origin HEAD:main`
- Send the owner the files with SendUserFile in posting order (photo_01..06, photo_b_01..06, tiktok_video.mp4) and plan.txt, so they can download them from the session on their phone.

## 9. Review (after the test week)
When the owner shares a new TikTok export, compare by format (slot A photos, slot B series photos, slot C video), by sound test (trending vs original), and comments, shares and profile views per day against week 1 (avg 377 / 162 / 192 views; 0 comments; about 2 profile views a day). Ask for per-video average watch time, % watched in full and traffic source if they are missing. Keep what wins, drop the bottom 20%, and record the decision at the top of this file.
