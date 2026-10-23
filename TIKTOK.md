# TikTok daily pack (for the scheduled "GRIND TikTok daily" agent)

The owner posts 3 TikToks per day MANUALLY from TikTok Studio and schedules all 3 each morning. Nothing here goes through Make.com. This pack never changes the Instagram pipeline: do not edit RUNBOOK.md, log.md, insights.md, or anything under `queue/`. Write only under `tiktok/` (and `work/`, never committed).

Brand, hook, intrigue and caption-tone rules come from STRATEGY.md (read it). Account: personal TikTok account, no clickable link, so captions say "link in bio" at most and never contain a URL.

## 0. Setup
```bash
cd /home/claude && git clone https://github.com/mdouiri19-del/grind-social && cd grind-social
# EVENING MODE (owner decision 2026-10-22): the run fires around 21:20 Toronto and prepares TOMORROW's pack, delivered by 22:00.
DAY=${DAY:-$(TZ=America/Toronto date -d tomorrow +%F)}
[ -f tiktok/$DAY/plan.txt ] && echo "TikTok pack already done" && exit 0
mkdir -p tiktok/$DAY work
export HYPERFRAMES_SKIP_SKILLS=1
export HYPERFRAMES_BROWSER_PATH=/opt/pw-browsers/chromium-1194/chrome-linux/chrome
(cd work && npm init -y >/dev/null && npm i gsap@3.13.0 --silent && cp node_modules/gsap/dist/gsap.min.js gsap.js)
```

## 1. The 3 posts
- Slot A: today's Instagram carousel `queue/$DAY/post_01.jpg..post_06.jpg`, posted as a TikTok PHOTO post.
- Slot B: ONE TikTok-only video `tiktok/$DAY/tiktok_3.mp4` that you make (section 2).
- Slot C: today's Instagram reel `queue/$DAY/reel.mp4`.
The Instagram run for $DAY starts around 20:45 the evening before and is usually done before this run starts. If `queue/$DAY/manifest.json` does not exist yet, `git pull` every 5 minutes for up to 30 minutes. If it is still missing, make TWO TikTok-only videos (tiktok_3.mp4 and tiktok_4.mp4, different ideas) and use them for slots B and C, with no photo post.

## 2. TikTok-only video
- HyperFrames, in `work/reel3/` (copy `work/gsap.js` and `assets/fonts` next to index.html). Mechanics as in RUNBOOK section 2 and `templates/reel-example/index.html`; look as in STRATEGY section 12.
- Must be a DIFFERENT idea, pillar and reel style than today's Instagram reel and carousel (read `queue/$DAY/meta.json`). Never reuse a hook from `tiktok/log.md` or `log.md` in the last 30 days.
- Dynamic edit: word slams on the beat, whole-stage push and pan, a beat pump on the camera, a wipe on every scene cut, at least one pattern interrupt (color flip, flash, shake), partial reveal or count-up of the key number. Hook fully readable and still at 2.0 s (TikTok cover). End on a clean, calm outro (no wipe, no shake, no beat pump on it): GRIND. wordmark + ONE short line written fresh for that day's idea (never "Your semester. A little more under control.", never reuse an outro line from the last 14 days in tiktok/log.md) + "Free · link in bio". Vary the outro background (cream, blush, green) and layout day to day.
- Music: a new original track every video with `tools/score.py` (tools/music.py is retired, see RUNBOOK section 2 step 3): `python3 tools/score.py work/beat3.wav <dur> --seed <YYYYMMDD of $DAY + 1000> --style <deephouse|lofi|pop> --bpm <bpm> --cuts <cut times> [--brk start,end] [--drop t] --end <dur - 1.0>`, with a style different from the same day's Instagram reel; build the timeline on B = 60/bpm. Note the printed `music:` line in tiktok/log.md. Mux: `ffmpeg -y -i work/reel3_video.mp4 -i work/beat3.wav -c:v libx264 -preset slow -crf 20 -pix_fmt yuv420p -c:a aac -b:a 128k -ar 44100 -ac 2 -af "volume=0.5" -shortest -movflags +faststart tiktok/$DAY/tiktok_3.mp4`
- Checks: lint errorCount 0, LOOK at the snapshot contact sheet and at 3 frames plus the 2.0 s frame. Fix overflow, overlap, clipped or tiny text, more than 6 words on screen. 1080x1920, h264 + aac, 15 to 25 s, under 19 MB.

## 3. Timing (Toronto). Starting points; adjust from TikTok results once the owner shares them.
Slot times follow $DAY's weekday (the day the posts go live).
- Mon to Fri: 12:30 slot A (photos) · 16:30 slot B · 20:30 slot C
- Sat, Sun: 11:00 slot A (photos) · 15:30 slot B · 20:00 slot C

## 4. plan.txt
Write `tiktok/$DAY/plan.txt` (plain text, no em dashes):
- Line 1: "Settings for every post: Everyone, comments on, Disclose post content > Your brand, AI-generated off, no extra sound on videos."
- Per slot: time, type and file paths, then the caption: hook line + 1 to 2 value lines + one question, then 4 to 5 hashtags starting with #studytok, always followed by #fyp #foryou #foryoupage. Photo posts also get a "Title:" line (under 90 characters) and "add a calm trending sound". Videos get "(cover at 2 s)".

## 5. Publish and deliver
- Append a row to `tiktok/log.md`: date | slot A | slot B | slot C (time + hook each).
- `git add tiktok/ && git commit -m "TikTok $DAY" && git pull --rebase -q origin main && git push -q origin HEAD:main`
- Send the owner the files with SendUserFile in posting order (photos post_01..06, tiktok_3.mp4, reel.mp4) and plan.txt, so they can download them from the session on their phone.
