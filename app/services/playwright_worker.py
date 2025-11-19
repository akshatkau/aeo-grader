# app/services/playwright_worker.py
import sys
import json
import asyncio
from playwright.async_api import async_playwright
# Make sure to run: pip install playwright-stealth
from playwright_stealth import stealth_async

async def run(url: str, proxy: str | None = None):
    async with async_playwright() as pw:
        launch_args = [
            "--disable-blink-features=AutomationControlled",
            "--no-sandbox",
            "--disable-infobars",
            "--disable-dev-shm-usage",
            "--disable-web-security",
            "--window-size=1920,1080",
        ]
        
        # Setup proxy if provided
        proxy_cfg = {"server": proxy} if proxy else None

        # Ajio often blocks "Headless" mode. 
        # If running locally, try headless=False to see if it opens. 
        # For servers, we must keep headless=True.
        browser = await pw.chromium.launch(
            headless=True, 
            proxy=proxy_cfg,
            args=launch_args
        )

        context = await browser.new_context(
            viewport={"width": 1920, "height": 1080},
            user_agent="Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/124.0.0.0 Safari/537.36",
            locale="en-US",
            timezone_id="Asia/Kolkata", # Ajio is India-specific
            permissions=["geolocation"],
            java_script_enabled=True,
        )

        page = await context.new_page()
        
        # Apply advanced stealth
        await stealth_async(page)

        try:
            # Ajio can be slow; give it time
            await page.goto(url, wait_until="domcontentloaded", timeout=60000)
            
            # Wait for a key element that indicates success (e.g., the footer or a product grid)
            # If this times out, we know we were blocked or the page didn't load.
            try:
                # Wait a bit for dynamic content
                await page.wait_for_timeout(5000) 
            except:
                pass

            content = await page.content()
            
            # Check for common "Access Denied" markers
            if "access denied" in content.lower() or "accessdenied" in content.lower():
                 print(json.dumps({"error": "access_denied"}))
            else:
                print(json.dumps({"html": content}))

        except Exception as e:
            print(json.dumps({"error": str(e)}))
        finally:
            await browser.close()

if __name__ == "__main__":
    url_arg = sys.argv[1] if len(sys.argv) > 1 else ""
    proxy_arg = sys.argv[2] if len(sys.argv) > 2 else None
    asyncio.run(run(url_arg, proxy_arg))