"""Render every <section data-out="name.png"> of a page at its own size (for brand assets and templates).
Usage: python3 tools/render_sections.py /abs/page.html /abs/outdir [scale]   (scale 2 = sharp 2x export)"""
import asyncio, sys
from playwright.async_api import async_playwright
async def main():
    async with async_playwright() as p:
        b = await p.chromium.launch(); pg = await b.new_page(viewport={'width': 1200, 'height': 2000}, device_scale_factor=float(sys.argv[3]) if len(sys.argv) > 3 else 1)
        await pg.goto('file://' + sys.argv[1]); await pg.wait_for_function("window.__ready===true", timeout=60000); await pg.wait_for_timeout(300)
        for el in await pg.query_selector_all('section[data-out]'):
            await el.screenshot(path=f"{sys.argv[2]}/{await el.get_attribute('data-out')}")
        await b.close()
asyncio.run(main())
