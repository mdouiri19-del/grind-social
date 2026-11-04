# Viral video writing: how GRIND. uses it (owner decision 2026-11-04)

Every new piece of GRIND. content (TikTok slot A, B, C, Instagram reel, sign-up post, LinkedIn post, captions) is written with the method in this folder (SKILL.md, hook-craft.md, story.md, retention.md, writing.md, checks.md). It sits ON TOP of TIKTOK.md, STRATEGY.md and RUNBOOK.md: those still decide the format, slots, series and brand rules; this decides the words.

For each post:
1. Facts sheet first (only real GRIND. features and real math; never invented stats, results, quotes or testimonials).
2. Write 5 hooks, judge them with the hook checklist (hook-craft.md), keep the best. Slide 1 / frame 0 must work on mute: hook text 8 words max, one thing to look at.
3. Write the body with one idea per slide or beat, a re-hook every slide (photos) or every 5 to 8 s (video), the best point in the middle, one CTA at the end.
4. Run the anti-AI check: write the post's full text (all slide text, or the spoken/on-screen script, plus the caption) one line per line into work/<slot>.txt and run `python3 tools/score_script.py work/<slot>.txt`. Zero HARD fails is mandatory. Soft "length" and "no CTA" flags can be ignored for short memes (7 to 12 s videos, meme slides) because they are short by design; every other soft flag must be fixed. Target 90+.
5. Rewrite until it passes (max 5 passes). Write the score and the chosen hook plus 2 rejected alternates in plan.txt (TikTok) or meta.json "writing" field (Instagram).
