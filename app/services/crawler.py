# app/services/crawler.py

from bs4 import BeautifulSoup
import httpx
import random
import subprocess, json, sys
import os

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


# --------- Playwright Worker Fallback (Windows-safe) ---------

async def fetch_playwright_fallback(url: str) -> str | None:
    try:
        worker_path = os.path.join(
            os.path.dirname(__file__),
            "playwright_worker.py"
        )
        result = subprocess.run(
            [sys.executable, worker_path, url],
            capture_output=True,
            text=True,
            timeout=60  # Increased from 45
        )
        
        # Check for errors
        if result.returncode != 0:
            print(f"Playwright worker error: {result.stderr}")
            return None
            
        data = json.loads(result.stdout)
        return data.get("html")
    except subprocess.TimeoutExpired:
        print(f"Playwright worker timeout for {url}")
        return None
    except json.JSONDecodeError as e:
        print(f"JSON decode error: {e}, stdout: {result.stdout}")
        return None
    except Exception as e:
        print(f"Playwright fallback exception: {str(e)}")
        return None



# --------- Main Crawler Entry ---------

async def fetch_html(url: str, timeout: int = 20) -> str | None:

    for attempt in [
        attempt_http_fetch,
        attempt_googlebot_fetch,
        attempt_mobile_fetch,
    ]:
        html = await attempt(url, timeout)
        if html:
            return html

    # Final attempt: Playwright worker
    html = await fetch_playwright_fallback(url)
    if html:
        return html

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
