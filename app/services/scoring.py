from math import floor
from app.services.benchmarks import adjust_score_with_industry
from app.services.location_benchmarks import adjust_score_with_location

def clamp(x: int, lo: int = 0, hi: int = 100) -> int:
    return max(lo, min(hi, x))

def score_onpage(onpage: dict) -> int:
    score = 0
    checks = 0

    checks += 1
    title = onpage.get("title")
    if title and 30 <= len(title) <= 65:
        score += 100
    else:
        score += 50 if title else 0

    checks += 1
    md = onpage.get("meta_description")
    if md and 80 <= len(md) <= 160:
        score += 100
    else:
        score += 40 if md else 0

    checks += 1
    score += 100 if onpage.get("h1") else 0

    checks += 1
    score += 100 if onpage.get("schema_present") else 30

    checks += 1
    ratio = onpage.get("images_with_alt_ratio")
    if ratio is None:
        score += 50
    else:
        score += floor(ratio * 100)

    return clamp(round(score / checks))

def score_technical(perf: dict | None) -> int:
    if not perf:
        return 50
    base = perf.get("performance_score", 60)
    mobile = 15 if perf.get("mobile_friendly") else 0
    vitals = 10 if perf.get("core_web_vitals") else 0
    return clamp(base + mobile + vitals)

def score_content(intent_coverage, expertise):
    ic = intent_coverage if intent_coverage is not None else 55
    eeat = expertise if expertise is not None else 55
    return clamp(round(0.6 * ic + 0.4 * eeat))

def score_aeo(seo, technical, content):
    return clamp(round(0.3 * seo + 0.3 * technical + 0.4 * content))


def apply_industry_context(all_scores, industry: str):
    all_scores["aeo_score"] = adjust_score_with_industry(all_scores["aeo_score"], industry, "aeo")
    all_scores["seo_score"] = adjust_score_with_industry(all_scores["seo_score"], industry, "seo")
    all_scores["technical_score"] = adjust_score_with_industry(all_scores["technical_score"], industry, "technical")
    all_scores["content_score"] = adjust_score_with_industry(all_scores["content_score"], industry, "content")
    return all_scores


def apply_location_context(all_scores, location: str):
    all_scores["seo_score"] = adjust_score_with_location(all_scores["seo_score"], location, "seo")
    all_scores["technical_score"] = adjust_score_with_location(all_scores["technical_score"], location, "performance")
    all_scores["content_score"] = adjust_score_with_location(all_scores["content_score"], location, "content")
    all_scores["aeo_score"] = adjust_score_with_location(all_scores["aeo_score"], location, "aeo")
    return all_scores
