import asyncio, sys
from playwright.async_api import async_playwright
async def main():
    async with async_playwright() as p:
        b=await p.chromium.launch()
        pg=await b.new_page(viewport={'width':1080,'height':1350})
        await pg.goto('file://'+sys.argv[1]); await pg.wait_for_timeout(600)
        for i in range(1,7):
            await pg.locator(f'#s{i}').screenshot(path=f'{sys.argv[2]}/png_{i}.png')
        await b.close()
asyncio.run(main())
