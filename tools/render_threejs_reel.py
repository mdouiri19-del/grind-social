"""Render a deterministic three.js + DOM reel page frame by frame.
The page must define window.renderAt(t) and set window.__ready = true.
Usage: python3 tools/render_threejs_reel.py URL DURATION_S OUT.mp4 [FPS]
Serve the repo first:  (cd <repo> && python3 -m http.server 8766 &)
Needs three in assets/grindy/node_modules:  (cd assets/grindy && npm i three@0.169.0)
"""
import asyncio, os, subprocess, sys, tempfile
from playwright.async_api import async_playwright
url, dur, out = sys.argv[1], float(sys.argv[2]), sys.argv[3]
fps = int(sys.argv[4]) if len(sys.argv) > 4 else 30
async def main():
    tmp = tempfile.mkdtemp()
    async with async_playwright() as p:
        b = await p.chromium.launch(args=["--use-gl=angle", "--use-angle=swiftshader", "--enable-unsafe-swiftshader"])
        pg = await b.new_page(viewport={'width': 1080, 'height': 1920})
        pg.on("pageerror", lambda e: print("pageerror:", e))
        await pg.goto(url); await pg.wait_for_function("window.__ready===true", timeout=120000)
        await pg.wait_for_timeout(500)
        n = int(dur * fps)
        for i in range(n):
            await pg.evaluate(f"window.renderAt({i / fps})")
            await pg.screenshot(path=f"{tmp}/f_{i:05d}.jpg", type="jpeg", quality=92)
            if i % 60 == 0: print("frame", i, "/", n, flush=True)
        await b.close()
    subprocess.run(["ffmpeg", "-loglevel", "error", "-y", "-framerate", str(fps), "-i", f"{tmp}/f_%05d.jpg",
                    "-c:v", "libx264", "-pix_fmt", "yuv420p", "-crf", "20", "-preset", "medium", out], check=True)
    print("done", out)
asyncio.run(main())
