# app/services/ux.py

from app.schemas.outputs import UXHeuristicInsights

def compute_ux_score(onpage: dict, performance: dict) -> UXHeuristicInsights:
    issues = []

    # CTA detection - naive text scan
    cta_present = any(
        kw in (onpage.get("content_text", "").lower())
        for kw in ["contact", "buy", "book", "call", "enquire", "get started"]
    )

    if not cta_present:
        issues.append("No clear call-to-action (CTA) found.")

    # Trust signal detection
    trust_keywords = ["testimonials", "reviews", "certified", "awards", "case study"]
    trust_present = any(
        kw in (onpage.get("content_text", "").lower())
        for kw in trust_keywords
    )

    if not trust_present:
        issues.append("Missing trust signals (reviews, testimonials, certifications).")

    readability_ok = True
    if len(onpage.get("content_text", "")) < 300:
        readability_ok = False
        issues.append("Content too short — may not satisfy user intent.")

    mobile_friendly = bool(performance.get("mobile_friendly", False))


    # simple formula
    ux_score = 80
    if not cta_present: ux_score -= 10
    if not trust_present: ux_score -= 10
    if not readability_ok: ux_score -= 10
    if not mobile_friendly: ux_score -= 10

    return UXHeuristicInsights(
        ux_score=max(0, ux_score),
        cta_present=cta_present,
        trust_signals_present=trust_present,
        mobile_friendly=mobile_friendly,
        readability_ok=readability_ok,
        issues=issues
    )
