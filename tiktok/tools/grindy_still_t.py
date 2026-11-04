import asyncio, json, os, sys, threading, functools, urllib.parse
from http.server import ThreadingHTTPServer, SimpleHTTPRequestHandler
from playwright.async_api import async_playwright
ROOT=os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
h=functools.partial(SimpleHTTPRequestHandler,directory=ROOT);h.log_message=lambda *a:None
srv=ThreadingHTTPServer(("127.0.0.1",8768),h);threading.Thread(target=srv.serve_forever,daemon=True).start()
async def main(spec,out):
    os.makedirs(out,exist_ok=True)
    async with async_playwright() as p:
        b=await p.chromium.launch(args=["--use-gl=angle","--use-angle=swiftshader","--enable-unsafe-swiftshader"])
        for s in json.load(open(spec)):
            w,hh=s.get("w",900),s.get("h",900)
            pg=await b.new_page(viewport={"width":w,"height":hh});pg.on("pageerror",lambda e:print("pageerror:",e))
            q={k:s[k] for k in ("cz","cy","ly","cx") if k in s};q.update(w=w,h=hh,p=json.dumps(s.get("pose",{})))
            await pg.goto("http://127.0.0.1:8768/assets/grindy/sheet_t.html?"+urllib.parse.urlencode(q))
            await pg.wait_for_function("window.__done===true",timeout=120000);await pg.wait_for_timeout(300)
            await pg.locator("canvas").screenshot(path=f"{out}/{s['name']}.png",omit_background=True);await pg.close();print("ok",s['name'])
        await b.close()
asyncio.run(main(sys.argv[1],sys.argv[2]))
