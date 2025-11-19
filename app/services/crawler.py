# app/services/crawler.py

from bs4 import BeautifulSoup
import httpx
import random
import subprocess
import json
import sys
import os

# --- CONFIGURATION ---

DEFAULT_UAS = [
    "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 "
    "(KHTML, like Gecko) Chrome/124.0.0.0 Safari/537.36",
    "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 "
    "(KHTML, like Gecko) Chrome/124.0.0.0 Safari/537.36 Edg/124.0",
    "Mozilla/5.0 (Macintosh; Intel Mac OS X 13_5) AppleWebKit/605.1.15 "
    "(KHTML, like Gecko) Version/16.4 Safari/605.1.15"
]

BASE_HEADERS = {
    "Accept": "text/html,application/xhtml+xml,application/xml;q=0.9,*/*;q=0.8",
    "Accept-Language": "en-US,en;q=0.9",
    "Connection": "keep-alive",
}

# Add your proxies here in the format: "http://username:password@host:port"
# If empty, the proxy fallback step will be skipped.
PROXIES = [
    # "http://user:pass@us-res-1.proxyprovider.com:8000",
    # "http://user:pass@us-res-2.proxyprovider.com:8000",
]

# --------- HTTPX Attempts ---------

async def attempt_http_fetch(url: str, timeout: int = 20):
    try:
        headers = BASE_HEADERS.copy()
        headers["User-Agent"] = random.choice(DEFAULT_UAS)

        async with httpx.AsyncClient(
            headers=headers,
            follow_redirects=True,
            timeout=timeout,
            verify=False
        ) as client:
            resp = await client.get(url)
            resp.raise_for_status()
            return resp.text
    except:
        return None


async def attempt_googlebot_fetch(url: str, timeout: int = 20):
    try:
        headers = BASE_HEADERS.copy()
        headers["User-Agent"] = (
            "Mozilla/5.0 (compatible; Googlebot/2.1; +http://www.google.com/bot.html)"
        )

        async with httpx.AsyncClient(
            headers=headers,
            follow_redirects=True,
            timeout=timeout,
            verify=False
        ) as client:
            resp = await client.get(url)
            resp.raise_for_status()
            return resp.text
    except:
        return None


async def attempt_mobile_fetch(url: str, timeout: int = 20):
    try:
        headers = BASE_HEADERS.copy()
        headers["User-Agent"] = (
            "Mozilla/5.0 (Linux; Android 10; Pixel 4 XL) "
            "AppleWebKit/537.36 (KHTML, like Gecko) "
            "Chrome/124.0.0.0 Mobile Safari/537.36"
        )

        async with httpx.AsyncClient(
            headers=headers,
            follow_redirects=True,
            timeout=timeout,
            verify=False
        ) as client:
            resp = await client.get(url)
            resp.raise_for_status()
            return resp.text
    except:
        return None


# --------- Playwright Worker Helpers ---------

async def run_playwright_worker(url: str, proxy: str = None) -> str | None:
    """
    Helper to run the subprocess. 
    If proxy is provided, it is passed as a second argument to the script.
    """
    try:
        worker_path = os.path.join(
            os.path.dirname(__file__),
            "playwright_worker.py"
        )
        
        # Build command: python playwright_worker.py "url" ["proxy"]
        cmd = [sys.executable, worker_path, url]
        if proxy:
            cmd.append(proxy)

        result = subprocess.run(
            cmd,
            capture_output=True,
            text=True,
            timeout=90,  # Increased timeout for stealth/proxy delays
            encoding='utf-8'
        )
        
        # Check for errors
        if result.returncode != 0:
            # Only print if it's not just a timeout/block that we expect to handle
            # print(f"Playwright worker stderr: {result.stderr}")
            return None
            
        try:
            data = json.loads(result.stdout)
        except json.JSONDecodeError:
            print(f"JSON Decode Error. Output was: {result.stdout[:200]}...")
            return None

        if "error" in data:
            # We can log this if we want to see why it failed (e.g., "access_denied")
            # print(f"Playwright worker reported error: {data['error']}")
            return None

        return data.get("html")

    except subprocess.TimeoutExpired:
        print(f"Playwright worker timeout for {url} (Proxy: {proxy is not None})")
        return None
    except Exception as e:
        print(f"Playwright fallback exception: {str(e)}")
        return None


async def fetch_playwright_fallback(url: str) -> str | None:
    """Standard no-proxy playwright attempt"""
    return await run_playwright_worker(url, proxy=None)


async def fetch_playwright_with_proxy(url: str, proxy: str) -> str | None:
    """Playwright attempt WITH proxy"""
    return await run_playwright_worker(url, proxy=proxy)


# --------- Main Crawler Entry ---------

async def fetch_html(url: str, timeout: int = 20) -> str | None:
    # 1. Fast HTTPX attempts
    for attempt in [
        attempt_http_fetch,
        attempt_googlebot_fetch,
        attempt_mobile_fetch,
    ]:
        html = await attempt(url, timeout)
        if html:
            return html

    print("HTTPX methods failed. Trying Playwright (Direct)...")

    # 2. Playwright (Direct / No Proxy)
    html = await fetch_playwright_fallback(url)
    if html:
        return html

    # 3. Playwright (Rotating Proxies)
    if PROXIES:
        print(f"Direct Playwright failed. Attempting {len(PROXIES)} proxies...")
        # Shuffle proxies to spread load if you have many
        random.shuffle(PROXIES)
        
        for proxy in PROXIES:
            print(f"Trying proxy: {proxy.split('@')[-1]}") # Log only the host:port part for privacy
            html = await fetch_playwright_with_proxy(url, proxy)
            if html:
                print("Proxy success!")
                return html
    else:
        print("No proxies configured in PROXIES list. Skipping proxy attempts.")

    raise Exception("Failed to fetch URL after all fallback attempts.")


# --------- HTML Parser ---------

def parse_onpage(html: str) -> dict:
    soup = BeautifulSoup(html, "lxml")

    title = soup.title.string.strip() if soup.title and soup.title.string else None

    meta_tag = soup.find("meta", attrs={"name": "description"})
    meta_description = meta_tag.get("content").strip() if meta_tag else None

    h1_tag = soup.find("h1")
    h1 = h1_tag.get_text(strip=True) if h1_tag else None

    headings = [
        h.get_text(strip=True)
        for tag in ["h1", "h2", "h3", "h4", "h5", "h6"]
        for h in soup.find_all(tag)
    ]

    imgs = soup.find_all("img")
    ratio = (
        round(sum(1 for i in imgs if i.get("alt")) / len(imgs), 3)
        if imgs else None
    )

    schema_present = bool(soup.find("script", attrs={"type": "application/ld+json"}))

    return {
        "title": title,
        "meta_description": meta_description,
        "h1": h1,
        "headings": headings,
        "schema_present": schema_present,
        "images_with_alt_ratio": ratio,
        "content_text": soup.get_text(separator=" ", strip=True)[:20000],
    }