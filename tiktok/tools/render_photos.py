"""Render a TikTok photo post: 6 slides (#s1..#s6, each 1080x1350) to 2160x2700 JPGs.
usage: python3 tiktok/tools/render_photos.py <slides.html> <out_dir>
Writes <out_dir>/photo_b_01.jpg .. photo_b_06.jpg (device scale 2, sharp text)."""
import asyncio, sys, os
from playwright.async_api import async_playwright
from PIL import Image

async def main(src, out):
    os.makedirs(out, exist_ok=True)
    async with async_playwright() as p:
        b = await p.chromium.launch()
        pg = await b.new_page(viewport={'width': 1080, 'height': 1350}, device_scale_factor=2)
        await pg.goto('file://' + os.path.abspath(src))
        await pg.evaluate('document.fonts.ready')
        await pg.wait_for_timeout(600)
        for i in range(1, 7):
            png = f'{out}/_tmp_{i}.png'
            await pg.locator(f'#s{i}').screenshot(path=png)
            im = Image.open(png).convert('RGB')
            assert im.size == (2160, 2700), im.size
            im.save(f'{out}/photo_b_{i:02d}.jpg', quality=92)
            os.remove(png)
        await b.close()

asyncio.run(main(sys.argv[1], sys.argv[2]))
