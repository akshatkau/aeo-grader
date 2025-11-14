import json
import subprocess
import httpx
import os

from app.core.config import settings


# ---------------------------------------
# Lighthouse Runner (Primary)
# ---------------------------------------
def run_lighthouse(url: str, timeout: int = 60) -> dict | None:
    """Runs Lighthouse with safer Chrome flags for big websites."""

    try:
        output_path = "lh_report.json"

        chrome_path = r"C:\Program Files\Google\Chrome\Application\chrome.exe"

        cmd = [
        "lighthouse.cmd",   # ← Windows requires .cmd
        url,
        "--quiet",
        f'--chrome-path="{chrome_path}"',
        "--chrome-flags=--headless",
        f"--output-path={output_path}",
        "--output=json",
        "--only-categories=performance"
        ]


        # Use list without shell=True
        subprocess.run(cmd, check=True, timeout=timeout)

        with open(output_path, "r") as f:
            return json.load(f)

    except Exception as e:
        print("Lighthouse failed:", e)
        return None




# ---------------------------------------
# PageSpeed Insights API (Fallback)
# ---------------------------------------
async def run_pagespeed_insights(url: str) -> dict | None:
    api_key = settings.GOOGLE_API_KEY

    if not api_key:
        print("Missing GOOGLE_API_KEY. PSI disabled.")
        return None

    endpoint = "https://www.googleapis.com/pagespeedonline/v5/runPagespeed"

    params = {
        "url": url,
        "strategy": "mobile",
        "key": api_key
    }

    try:
        async with httpx.AsyncClient(timeout=30) as client:
            resp = await client.get(endpoint, params=params)
            resp.raise_for_status()
            return resp.json()
    except Exception as e:
        print("PageSpeed Insights failed:", e)
        return None



# ---------------------------------------
# Hybrid performance engine (recommended)
# ---------------------------------------
async def get_performance(url: str) -> dict:
    # 1) Try lighthouse first
    lh = run_lighthouse(url)
    if lh:
        try:
            audits = lh.get("audits", {})
            return {
                "performance_score": int(lh["categories"]["performance"]["score"] * 100),
                "core_web_vitals": {
                    "lcp": audits.get("largest-contentful-paint", {}).get("numericValue"),
                    "cls": audits.get("cumulative-layout-shift", {}).get("numericValue"),
                    "fcp": audits.get("first-contentful-paint", {}).get("numericValue"),
                },
                "mobile_friendly": True
            }
        except Exception:
            pass

    # 2) Try PSI fallback
    psi = await run_pagespeed_insights(url)
    if psi:
        try:
            lr = psi["lighthouseResult"]
            audits = lr["audits"]
            return {
                "performance_score": int(lr["categories"]["performance"]["score"] * 100),
                "core_web_vitals": {
                    "lcp": audits.get("largest-contentful-paint", {}).get("numericValue"),
                    "cls": audits.get("cumulative-layout-shift", {}).get("numericValue"),
                    "fcp": audits.get("first-contentful-paint", {}).get("numericValue"),
                },
                "mobile_friendly": True
            }
        except Exception:
            pass

    # 3) Final fallback
    return {
        "performance_score": 50,   # neutral fallback
        "core_web_vitals": None,
        "mobile_friendly": None,
        "fallback": True
    }

