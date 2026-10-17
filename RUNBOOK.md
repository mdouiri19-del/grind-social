# Daily run (for the scheduled Claude agent)

Goal: every day, publish ONE reel and ONE 6-slide carousel for GRIND. into `queue/<date>/`. Make.com posts them to Instagram at 12:00 (reel) and 19:00 (carousel), Toronto time. Nobody reviews the output before it goes live, so quality and brand rules are on you.

## 0. Setup (fresh container every run)
```bash
cd /home/claude && git clone https://github.com/mdouiri19-del/grind-social && cd grind-social
DAY=$(TZ=America/Toronto date +%F)
[ -f queue/$DAY/manifest.json ] && echo "already published today" && exit 0
mkdir -p queue/$DAY work
export HYPERFRAMES_SKIP_SKILLS=1
export HYPERFRAMES_BROWSER_PATH=/opt/pw-browsers/chromium-1194/chrome-linux/chrome   # or any chromium under /opt/pw-browsers
(cd work && npm init -y >/dev/null && npm i gsap@3.13.0 --silent && cp node_modules/gsap/dist/gsap.min.js gsap.js)
```
Network: only GitHub and package registries work. No CDNs, no web fonts, no stock media. Everything is local (fonts in `assets/fonts/`).

## 1. Plan
1. Read `STRATEGY.md` (brand rules, pillars, weekly rotation, hook bank, caption rules) and `log.md`.
2. Pick today's reel pillar and carousel pillar from the weekly rotation (Toronto day of week) and the seasonal calendar.
3. Pick hooks. Never reuse a hook that appears in `log.md` within the last 30 days. Remix the hook bank or write new ones in the same spirit.
4. Reel and carousel cover DIFFERENT ideas the same day.

## 2. Reel (HyperFrames, 1080x1920, 15 to 25 s)
1. Write `work/reel/index.html` as a fresh HyperFrames composition. Use `templates/reel-example/index.html` for mechanics only (root attrs, clips, one paused GSAP timeline on `window.__timelines["main"]`, local gsap.js and fonts). Vary layout and motion day to day so the feed doesn't look templated.
   Rules: hook in first 1.5 s with motion from frame 0; one idea; 3 beats max; final 2 to 3 s CTA on brand green "Your semester. A little more under control." + GRIND. + "Free · link in bio". Text inside y 250 to 1520. No `<br>` except display titles split into block spans. Animate only opacity/transform/colors. No CSS transform on elements GSAP transforms.
2. Copy `work/gsap.js` and `assets/fonts` next to it (or fix paths). Then:
   ```bash
   cd work/reel && npx hyperframes lint --json   # errorCount must be 0
   npx hyperframes snapshot --frames 8           # LOOK at the contact sheet. Fix overlaps, clipped text, empty frames.
   npx hyperframes render --quality high --fps 30 --output ../reel_video.mp4
   ```
3. Music: `python3 tools/beat.py work/beat.wav <duration> <day-of-year>` (or a file from `assets/music/` if present).
4. Mux: `ffmpeg -y -i work/reel_video.mp4 -i work/beat.wav -c:v libx264 -preset slow -crf 20 -pix_fmt yuv420p -c:a aac -b:a 128k -ar 44100 -ac 2 -af "volume=0.55" -shortest -movflags +faststart queue/$DAY/reel.mp4`
5. Cover: Make only supports a cover FRAME (milliseconds into the reel). Put `"cover_ms": <int>` in meta.json at a moment where the hook is fully on screen and still (default 1900). Also save that frame as `queue/$DAY/cover.jpg`, 1080x1920 JPEG. (`ffmpeg -ss <seconds> -i queue/$DAY/reel.mp4 -frames:v 1 -q:v 2 queue/$DAY/cover.jpg`) and LOOK at it: hook fully visible, big, centered (the profile grid crops covers to 4:5, keep text in the middle). If no frame works as a cover, redesign the hook scene so one does.
6. Check with ffprobe: 1080x1920, h264, aac, duration 15 to 25 s, under 19 MB. Extract 3 frames and look at them.

## 3. Carousel (6 slides, 1080x1350)
1. Write `work/carousel.html` with 6 `<section class="s" id="s1..s6">`, styled from `templates/carousel-example/carousel.html` (fonts path `../assets/fonts/`).
2. Render: `python3 tools/render_carousel.py $PWD/work/carousel.html $PWD/work` then `ffmpeg -i work/png_N.png -q:v 2 queue/$DAY/post_0N.jpg` for N=1..6.
3. Look at every slide. Text must not overflow cards or hit the footer. Fix and re-render.

## 4. Captions + meta
- `queue/$DAY/reel_caption.txt` and `post_caption.txt` per STRATEGY section 7. Short. No em dashes. End with 3 to 6 hashtags.
- `queue/$DAY/meta.json`: {"pillars":{"reel":"...","post":"..."},"hooks":{"reel":"...","post":"..."}}

## 5. Publish
```bash
python3 tools/publish.py $DAY      # pushes media, then manifest.json with pinned URLs
```
Then append one row to `log.md`, commit ("Log $DAY") and push.

## 6. Hard rules
- Brand rules in STRATEGY section 0 are absolute (Inter only, no serif italic, real features only, no fake stats/testimonials, no real people or school logos, never the founder's family name).
- Sample data on screen (course codes, %, dates) must look illustrative, never claims about real users.
- If anything fails and can't be fixed, publish NOTHING (no manifest = nothing posts). Never push a half package.
- Do not touch anything outside this repo.
