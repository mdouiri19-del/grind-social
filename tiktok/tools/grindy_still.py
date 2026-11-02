"""Render Grindy stills (PNG) for slideshows, from a JSON list of shots.
usage: python3 tiktok/tools/grindy_still.py shots.json out_dir
shots.json: [{"name": "s1", "w": 1080, "h": 900, "bg": "#D9F88D", "cz": 13.5, "cy": 2.9, "ly": 2.2, "cx": 0,
              "pose": {"expression": "alert", "armL": 2.6, "armR": 2.6, "props": {"coffee": true}, "glow": 2.4}}]
Expressions: happy, alert, focused, sleepy, proud, shocked, sad. Props: glasses, cap, coffee.
Pose keys: armL, armR (raise), armLx, armRx, tilt, turn, yaw, bounce, squash, glow, antenna, look [x,y], blink, visor.
Needs three: (cd assets/grindy && npm i three@0.169.0 --silent). Starts its own local server on port 8767."""
import asyncio, json, os, sys, threading, functools, urllib.parse
from http.server import ThreadingHTTPServer, SimpleHTTPRequestHandler
from playwright.async_api import async_playwright
ROOT = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
def serve():
    h = functools.partial(SimpleHTTPRequestHandler, directory=ROOT)
    h.log_message = lambda *a: None
    srv = ThreadingHTTPServer(("127.0.0.1", 8767), h); threading.Thread(target=srv.serve_forever, daemon=True).start(); return srv
async def main(spec, out):
    os.makedirs(out, exist_ok=True); shots = json.load(open(spec)); srv = serve()
    async with async_playwright() as p:
        b = await p.chromium.launch(args=["--use-gl=angle", "--use-angle=swiftshader", "--enable-unsafe-swiftshader"])
        for s in shots:
            w, h = s.get("w", 1080), s.get("h", 1080)
            pg = await b.new_page(viewport={"width": w, "height": h}); pg.on("pageerror", lambda e: print("pageerror:", e))
            q = {k: s[k] for k in ("bg", "cz", "cy", "ly", "cx") if k in s}; q.update(w=w, h=h, p=json.dumps(s.get("pose", {})))
            await pg.goto("http://127.0.0.1:8767/assets/grindy/sheet.html?" + urllib.parse.urlencode(q))
            await pg.wait_for_function("window.__done===true", timeout=120000); await pg.wait_for_timeout(300)
            await pg.locator("canvas").screenshot(path=f"{out}/{s['name']}.png"); await pg.close(); print("ok", s["name"])
        await b.close()
    srv.shutdown()
asyncio.run(main(sys.argv[1], sys.argv[2]))
