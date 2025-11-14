# app/services/keyword_engine.py

import re
from urllib.parse import urlparse
from app.schemas.outputs import KeywordInsights


# -------------------------------------------------------------
# 1. Extract raw keywords (for debugging)
# -------------------------------------------------------------
def extract_keywords(text: str):
    """Extracts unique words (min length 4) from content."""
    if not text:
        return []
    words = re.findall(r"\b[a-zA-Z]{4,}\b", text.lower())
    return list(set(words))[:50]


# -------------------------------------------------------------
# 2. Build Suggested Keywords (Industry + Product + Brand)
# -------------------------------------------------------------
BASE_KEYWORDS = {
    "healthcare": ["clinic", "doctor", "treatment", "medical", "appointment", "specialist"],
    "electronics": ["buy", "specifications", "features", "price", "online", "compare", "review"],
    "software": ["saas", "pricing", "demo", "cloud", "integrations", "features"],
    "education": ["courses", "admission", "training", "certificate", "online classes"],
    "finance": ["loan", "interest rate", "eligibility", "apply online", "emi"],
    "default": ["services", "solutions", "company", "best", "top"]
}

def generate_suggested_keywords(industry: str, product: str = "", company: str = ""):
    industry = (industry or "default").lower()
    base = BASE_KEYWORDS.get(industry, BASE_KEYWORDS["default"])

    product_keywords = []
    if product:
        product_keywords = [
            product.lower(),
            f"{product} price",
            f"{product} features",
            f"buy {product}",
            f"{product} review",
            f"best {product}"
        ]

    brand_keywords = []
    if company:
        brand_keywords = [
            f"{company.lower()} review",
            f"{company} services",
            f"{company} pricing",
            f"{company} contact"
        ]

    final_list = list(dict.fromkeys(base + product_keywords + brand_keywords))
    return final_list[:25]   # limit to keep scoring stable


# -------------------------------------------------------------
# 3. MULTI-LAYER Keyword Detection
# -------------------------------------------------------------
def keyword_in_title(kw, title):
    return title and kw.lower() in title.lower()

def keyword_in_h1(kw, h1):
    return h1 and kw.lower() in h1.lower()

def keyword_in_headings(kw, headings):
    if not headings:
        return False
    return any(kw.lower() in h.lower() for h in headings)

def keyword_in_content(kw, content):
    return kw.lower() in (content or "").lower()

def keyword_in_url(kw, url):
    if not url:
        return False
    path = urlparse(url).path.lower()
    return kw.lower().replace(" ", "-") in path


# -------------------------------------------------------------
# 4. Final Keyword Scoring Engine (Step-5)
# -------------------------------------------------------------
def keyword_contextual_score(content_text: str, industry: str, product: str, company: str, onpage: dict, url: str):
    """Full Step-5 keyword scoring engine."""

    suggested = generate_suggested_keywords(industry, product, company)

    title = onpage.get("title", "")
    h1 = onpage.get("h1", "")
    headings = onpage.get("headings", [])
    content = content_text or ""

    used = []
    missing = []

    for kw in suggested:
        score_sources = [
            keyword_in_title(kw, title),
            keyword_in_h1(kw, h1),
            keyword_in_headings(kw, headings),
            keyword_in_content(kw, content),
            keyword_in_url(kw, url),
        ]

        if any(score_sources):
            used.append(kw)
        else:
            missing.append(kw)

    total = len(suggested)
    used_count = len(used)

    coverage = 0
    if len(suggested) > 0:
        coverage = int((len(used) / len(suggested)) * 100)

    return KeywordInsights(
        keywords_used=len(used),
        total_suggested=len(suggested),
        missing_keywords=missing,
        coverage=coverage
    )

