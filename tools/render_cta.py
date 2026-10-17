"""Render a 1080x1350 single-image CTA post. Usage: python3 tools/render_cta.py ABS_HTML OUT.png  (element #s1)"""
import asyncio, sys
from playwright.async_api import async_playwright
async def main():
    async with async_playwright() as p:
        b = await p.chromium.launch()
        pg = await b.new_page(viewport={'width': int(sys.argv[3]) if len(sys.argv)>3 else 1080, 'height': int(sys.argv[4]) if len(sys.argv)>4 else 1350})
        await pg.goto('file://' + sys.argv[1]); await pg.wait_for_timeout(600)
        await pg.locator('#s1').screenshot(path=sys.argv[2])
        await b.close()
asyncio.run(main())
