import asyncio
from pathlib import Path
from playwright.async_api import async_playwright

html = Path(r"D:\roseempire\demo-recordings\crm_overlay.html").resolve().as_uri()
out = Path(r"D:\roseempire\demo-recordings\crm_bottom.png")

async def main():
    async with async_playwright() as p:
        browser = await p.chromium.launch(headless=True)
        page = await browser.new_page(viewport={"width": 1080, "height": 960})
        await page.goto(html, wait_until="networkidle", timeout=30000)
        await asyncio.sleep(1)
        await page.screenshot(path=str(out), full_page=False)
        await browser.close()
    print(out)

asyncio.run(main())
