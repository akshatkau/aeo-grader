import sys, json, asyncio
from playwright.async_api import async_playwright

async def run(url):
    async with async_playwright() as pw:
        browser = await pw.chromium.launch(
            headless=True,
            args=[
                '--disable-blink-features=AutomationControlled',
                '--disable-web-security',
                '--no-sandbox'
            ]
        )
        context = await browser.new_context(
            user_agent='Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/124.0.0.0 Safari/537.36',
            viewport={'width': 1920, 'height': 1080},
            java_script_enabled=True
        )
        page = await context.new_page()
        
        # Add stealth scripts
        await page.add_init_script("""
            Object.defineProperty(navigator, 'webdriver', {
                get: () => undefined
            });
        """)
        
        # Increase timeout and use more lenient wait condition
        await page.goto(url, wait_until="domcontentloaded", timeout=60000)
        await page.wait_for_timeout(2000)  # Additional wait
        
        html = await page.content()
        await browser.close()
        print(json.dumps({"html": html}))

if __name__ == "__main__":
    url = sys.argv[1]
    asyncio.run(run(url))
