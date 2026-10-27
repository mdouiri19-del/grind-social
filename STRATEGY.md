# GRIND. Instagram playbook (source of truth for the daily agent)

## 0. Brand rules (never break)
- Brand: GRIND. (with the dot). Product: student academic dashboard. Syllabus import, deadlines sorted by date and weight, grade tracking, Study Studio (AI quizzes, mock exams, revision notes, assignment plans).
- Link: always https://grindstudent.com/welcome ("link in bio" in reels, URL in caption).
- Language: English. Tone: a calm, smart senior student. Warm, a bit funny, never cringe, never corporate. Short lines.
- Colors: cream #F6F7F1, ink #203A2D, brand green #254D3B, lime #D9F88D (highlights, progress), blush #F2DEE5 (human touch). Font: Inter only (500/600/700). NEVER Instrument Serif or any italic serif headline.
- Signature material: GRIND. Glass (section 14). Part of the identity on Instagram, stories and the website; never on LinkedIn.
- No real people, no university logos or trademarks, no copyrighted characters or music with lyrics. No fake reviews, no fake stats, no invented testimonials. Never name the founder's family.
- Never promise grades. Never claim features GRIND does not have. Real features only: syllabus PDF import (dates + weights), weighted current average, "what's due in 14 days" priority, schedule, files, practice quizzes, Study Studio, calendar .ics export, EN/FR.

## 1. Audience
University and college students, 18 to 24, North America first (Canada, US), also francophone students. Pain: deadlines scattered across 5 syllabi, surprise due dates, not knowing their real grade, studying without a system, midterm and finals panic.

## 2. Content pillars (rotate)
1. GRADE MATH: "what do I need on the final", weighted averages, how weights really work. High save + share.
2. DEADLINE REALITY: relatable chaos, "wait, that's due tomorrow?". High share.
3. STUDY SYSTEMS: active recall, spaced practice, mock exams, planning a 15% assignment in steps. High save.
4. GRIND IN ACTION: syllabus to sorted dashboard, Study Studio building a quiz. Conversion.
5. SEMESTER MOMENTS: week 1, midterms, reading week, finals, new semester. Timely.

Mix target per week: 2 grade math, 1 deadline reality, 2 study systems, 1 GRIND in action, 1 semester moment. Product appears softly in every piece (last beat), hard only in pillar 4.

## 3. Weekly rotation (day of week, Toronto time)
| Day | Reel pillar | Post (carousel) pillar |
|---|---|---|
| Mon | Grade math | Study systems |
| Tue | Deadline reality | Grade math |
| Wed | Study systems | Semester moments |
| Thu | GRIND in action | Study systems |
| Fri | Grade math | Deadline reality |
| Sat | Semester moments | Checklist (any pillar) |
| Sun | Study systems | Week-ahead plan |

## 4. Reel formula (15 to 25 s, 1080x1920, 30 fps)
- 0.0 to 1.5 s HOOK: big text, 6 words max, motion from frame 1. No logo, no intro.
- 1.5 to 5 s TENSION: the problem in one line.
- 5 to 20 s PAYOFF: 3 beats max, one idea per screen, numbers on screen.
- Last 2 to 3 s: clean end card. A payoff line specific to the reel (e.g. "Skip the math next time."), GRIND. wordmark, "Free · link in bio". Change the line every reel; the old "Your semester, a little more under control." line is retired from reels.
- All text burned in, safe zone: keep text away from top 250 px and bottom 400 px (IG UI).
- Audio: instrumental, original, royalty free, generated FRESH for every reel with `tools/score.py` (deephouse, lofi or pop; style not the same as the last 2 reels; curated progressions, chord tones only, 4 layers max). Calm and musical, never busy: it sits under the visuals at -16 LUFS. Cuts land on its bar lines.
- Visual style: kinetic typography on cream/green, lime highlights, UI-card motifs (deadline rows, weight %, progress bars) that echo the GRIND. dashboard. Motion every 0.5 to 1 s.
- One reel = one idea. If it needs two, it's two reels.

## 5. Carousel formula (6 slides, 1080x1350) (updated 2026-10-21, owner feedback: more structured, use the signature effects, never the same last slide)
- Exactly 6 slides, told as one story: 1 hook, 2 to 5 one step each (the trap, the fix, the loop or proof, the tip), 6 save.
- One layout system on every slide: top bar (GRIND. wordmark left, 6-segment progress bar right, current segments filled), a numbered kicker ("01 · The trap"), the headline under it (max about 8 words, lime highlight on 1 to 2 words), ONE visual in the middle zone (y 400 to 1130), a one-line caption at y 1150 (bold the key phrase), small footer (sample label left, "Swipe →" right). Nothing else floating around.
- Use the signature effects (templates/effects/gx.js) as the main visual on at least 3 slides, each where it means something: LCD screen push for the hook or a big number, liquid glass as a magnifier over the one line that matters (GX.glassPanel, frost 0, zoomBehind about 1.1) or a glass card over a busy scene, a big plain number slammed into its UI row for a sample progress number (the glass graph is retired, owner 2026-10-27), over-the-shoulder still for before / after (cards beside a central phone, an arrow labelled with what GRIND. does; never frozen light streaks in a still).
- Slides 2 to 5: max 25 words each, one point per slide.
- Slide 6 (save) ROTATES, never the same design as the last 3 carousels (log it): (a) glass card over a collage of this carousel's own visuals; (b) LCD screen with a short save line plus a URL pill; (c) recap checklist of the 4 steps with a save icon; (d) a phone showing the GRIND. list with the save line above; (e) big number or date on blush with the save line. The words change too, always with a save ask that fits the topic ("Save this before midterms.", "Save it for your next paper.", "Keep this for finals week.") and "GRIND. organizes all of it from your syllabus. grindstudent.com/welcome" (or a close variant).
- Reference: templates/carousel-effects-example/carousel.html.

## 6. Hook bank (reuse, remix, never repeat the exact same hook within 30 days)
- "Your syllabus is lying to you about one thing."
- "That 10% quiz matters more than you think."
- "Here's the math on what you actually need on the final."
- "Stop rereading your notes. Do this instead."
- "5 courses. 37 deadlines. One screen."
- "POV: you just found a deadline you didn't know existed."
- "If your midterm is worth 25%, read this."
- "The 14-day rule that saves your semester."
- "You're not lazy. You're unorganized. Fixable."
- "How to study for an exam in 3 days (realistic version)."
- "Nobody tells first years this about grade weights."
- "A 70 on a 40% final vs a 90 on a 10% quiz. Which matters more?"
- "Turn your syllabus into a plan in 30 seconds."
- "Reading week is a trap. Here's the fix."
- "Every course has one assignment that decides your grade."
- "Your average isn't what you think it is."
- "Write this before your next midterm."
- "Things I'd tell myself in week 1."

## 7. Caption rules
- Line 1 = hook restated (it shows before "more").
- 2 to 4 short lines of value. One question to drive comments ("What's your worst deadline this week?").
- CTA line: "Free for students: grindstudent.com/welcome"
- 3 to 6 hashtags, niche over huge: #studytips #universitylife #studentlife #studymotivation #gradeschool #collegetips #midterms #finalsweek #studentorganization. Generic tags only, no school names.

## 8. Seasonal calendar (adjust pillar 5)
- Sep: week 1, syllabus week. Oct: first midterms, reading week. Nov: midterm 2, papers. Dec: finals. Jan: new semester setup. Feb: reading week. Mar: crunch. Apr: finals. May to Aug: summer courses, prep for fall (lower volume ok).

## 9. Daily output package (see RUNBOOK.md)
Folder `queue/YYYY-MM-DD/` in this repo (mdouiri19-del/grind-social, public):
- `reel.mp4` (H.264 + AAC, 1080x1920, 30 fps, 15 to 25 s, under 19 MB)
- `cta.jpg` + `cta_caption.txt` (single-image sign-up post, posted Mon/Wed/Fri 08:45; one real feature per post)
- `linkedin.txt` (+ optional `linkedin.jpg`): GRIND. LinkedIn page post, Tue/Wed/Thu only, posted 08:30
- `cover.jpg` (reel thumbnail 1080x1920, hook readable in the center)
- `reel_caption.txt`, `post_caption.txt`
- `post_01.jpg ... post_06.jpg` (1080x1350). Carousel is ALWAYS exactly 6 slides (Make.com maps 6 fixed slots).
- `meta.json`: {"pillars":{"reel":..,"post":..},"hooks":{"reel":..,"post":..}}
- `manifest.json` written LAST by `tools/publish.py` (URLs pinned to the media commit).
Make.com reads `queue/<today Toronto>/manifest.json`: carousel 12:45 and reel 19:30 (daily), sign-up photo 08:45 (Mon/Wed/Fri), LinkedIn 08:30 (Tue/Wed/Thu).

## 10. Learning loop
- Log each day in `log.md` (this repo): date, pillar, hook, format.
- Every Sunday: if the person pastes stats (views, saves, shares, follows), keep hooks with best 3 s hold and saves, drop the bottom 20%.

## 11. Platform visual identities (keep them clearly different)
- INSTAGRAM (reels, carousels, sign-up post): light and playful. Cream #F6F7F1 backgrounds (sign-up post on brand green), lime highlight blocks on words, white UI cards (deadline rows, weight pills, checklists), blush touches, motion, emoji allowed in captions. Formats 1080x1920 and 1080x1350.
- LINKEDIN (GRIND. page): editorial and calm. Deep ink background #16261E with a faint 100px grid, white Inter type, muted sage #9DB09A body text, ONE lime accent (short rule + kicker), uppercase letter-spaced labels "GRIND. Notes" + day theme, optional stats row with true figures only, footer "From the GRIND. team". No UI cards, no blush, no emoji, no highlight blocks. Format 1200x1500. Template: templates/linkedin-example/linkedin.html.

## 12. Instagram variety system (same identity, never the same look twice in a row)
Constants that NEVER change: Inter, the palette, GRIND. wordmark, lime as the highlight color, plain friendly copy.
Everything else rotates. Never reuse a reel style or carousel layout used in the previous 3 days (check log.md).

### Reel styles (rotate)
1. KINETIC SLAM: words hit the screen one by one, scale and shake, hard cuts on the beat.
2. FAKE UI DEMO: a GRIND.-like dashboard built in HTML, cursor moves, clicks, rows sort themselves, zooms into one number.
3. COUNTDOWN: a huge ticking timer or "days left" counter drives the whole reel, urgency, red-free (use ink + lime).
4. PLAN VS REALITY: split screen, left "the plan" neat, right "reality" chaotic, then GRIND. fixes the right side.
5. NOTIFICATION PILE-UP: POV phone screen, reminders and "due 11:59 PM" banners stack and overflow, then calm.
6. MATH REVEAL: an equation builds live (weights, averages), numbers count up, the answer lands big.
7. MYTH / FACT: a claim appears, gets stamped MYTH, flips to the fact with a check.
8. SPEEDRUN LIST: 5 tips in 12 seconds, numbered stamps, one cut per tip.
9. SYLLABUS ZOOM: a PDF-like page, camera dives through it to the one buried line that matters.

### Intrigue rules (every reel)
- Open loop in the first second: the hook raises a question the viewer needs answered ("Nobody reads line 3 of their syllabus."). Never state the answer in the hook.
- Something moves every 0.5 s, the scene changes every 1 to 2.5 s, no static frame longer than 1.2 s. Move the whole stage too (slow push-in, pan, tilt), not just the text.
- At least one pattern interrupt mid-reel (color flip to green or blush, a zoom punch, a freeze-frame).
- Partial reveals: blur or mask a key number and reveal it late.
- Max 6 words on screen at once. Cuts land on the bar lines printed by tools/score.py.
- Loop ending: the last frame visually leads back into the first so replays feel seamless.
- Vary background dominance per reel: cream, brand green, blush, or lime-forward.

### Carousel layouts (rotate)
checklist, big-number cover, step-by-step guide, myth vs fact, before / after, mistakes list ("5 things that cost you marks"), timeline of a week, quote-style truth bomb, mini-quiz (answer on last slide). Alternate cover background between cream, green and blush.

## 13. Mascot: Grindy (Instagram only, never LinkedIn)
- Who: GRIND.'s study-buddy robot. Dark green vinyl body, cream visor with big ink eyes, lime smile, lime antenna bulb that GLOWS/FLASHES when a deadline is close. Calm, smart, a little deadpan, never mean, never cringe. He never talks in first-person ads; he reacts.
- He is a clearly fictional brand character: never present him as a real student, never give him testimonials or fake usage numbers.
- Expressions: happy, alert (blush visor + flashing antenna), focused (brows down, optional glasses), sleepy (eyes almost closed, coffee), proud (grin, grad cap), shocked, sad.
- Props: glasses, coffee, grad cap.
- Use: in about 3 of 7 reels per week (rotate with the other styles in section 12), as the emotional reaction layer on top of the story (relatable moment, then GRIND. fixes it). Reaction beats: sleepy -> deadpan stare -> panic jump with flashing antenna -> focused with glasses -> proud with cap.
- Engine: assets/grindy/grindy.js (three.js). Example reel: assets/grindy/reel_grindy_midterm.html, rendered with tools/render_threejs_reel.py. Can also appear in carousel covers (render a still with assets/grindy/sheet.html?p=<pose json>).

## 14. GRIND. Glass (brand material, adopted 2026-10-21)
GRIND. Glass is liquid glass in the brand colours: a rounded card that frosts and gently bends what is behind it, with a bright rim of light (strongest top left), a soft corner highlight and a soft shadow. It is how GRIND. puts "the one thing that matters" on top of the chaos.
- Four variants, nothing else (presets in templates/effects/gx.js `GX.GLASS`, web in assets/glass/web/grind-glass.css):
  - ink (default): brand green tint 0.62, frost 8, cream text. Over cream, sage or busy scenes.
  - lime: lime tint 0.55, frost 8, ink text. Over dark green scenes only.
  - frost: cream tint 0.55, frost 12, ink text. Over bold colour (blush, lime, blobs).
  - lens: clear (tint about 0), no frost, light bend, magnifies about 1.08x. Over the ONE line that matters (a date in a syllabus, a row in a list). Centre it on that line and make it wider than the text, so text never warps.
- Glass needs something behind it: always place it over content or colour (rows, a page, a calendar, blobs). Never over a flat empty background.
- One glass element per frame or slide (two only in a collage). Radius 34 to 40 for cards, full pill for lens, a circle for highlight covers.
- Type on glass: Inter 600/700, big and short (a headline, a number, one line). No paragraphs on glass.
- Numbers on glass follow the honesty rules: true structural figures or data labelled "sample".
- Every reel has at least one glass moment (a glass panel; the glass graph is retired, owner 2026-10-27); every carousel at least one glass slide; stories and sign-up images use the glass templates in assets/glass/out when they fit.
- LinkedIn keeps its flat editorial system (section 11): no glass there, so the two identities stay distinct.
- Brand kit and ready assets: assets/glass/ (glass-kit.html renders the variant swatches, story and post templates and highlight covers into assets/glass/out).

