# GRIND. Instagram playbook (source of truth for the daily agent)

## 0. Brand rules (never break)
- Brand: GRIND. (with the dot). Product: student academic dashboard. Syllabus import, deadlines sorted by date and weight, grade tracking, Study Studio (AI quizzes, mock exams, revision notes, assignment plans).
- Link: always https://grindstudent.com/welcome ("link in bio" in reels, URL in caption).
- Language: English. Tone: a calm, smart senior student. Warm, a bit funny, never cringe, never corporate. Short lines.
- Colors: cream #F6F7F1, ink #203A2D, brand green #254D3B, lime #D9F88D (highlights, progress), blush #F2DEE5 (human touch). Font: Inter only (500/600/700). NEVER Instrument Serif or any italic serif headline.
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
- Last 2 to 3 s: soft CTA "Your semester, a little more under control. GRIND. link in bio".
- All text burned in, safe zone: keep text away from top 250 px and bottom 400 px (IG UI).
- Audio: instrumental, royalty free, from `assets/music/` if tracks exist (rotate, never same track 2 days in a row), else generate an original beat with `tools/beat.py` (seed = day of year). Music at about -18 LUFS, under the visuals. No voiceover by default.
- Visual style: kinetic typography on cream/green, lime highlights, UI-card motifs (deadline rows, weight %, progress bars) that echo the GRIND. dashboard. Motion every 0.5 to 1 s.
- One reel = one idea. If it needs two, it's two reels.

## 5. Carousel formula (6 slides, 1080x1350)
- Exactly 6 slides.
- Slide 1: hook headline (same hook rules), cream background, ink text, lime highlight on 1 to 2 words.
- Slides 2 to 5: one point per slide, max 25 words, big type.
- Last slide: "Save this for midterms" + "GRIND. organizes all of it from your syllabus. grindstudent.com/welcome".

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

