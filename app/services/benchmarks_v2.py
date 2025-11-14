# app/services/benchmarks_v2.py

from app.schemas.outputs import BenchmarkInsights

INDUSTRY_AVG = {
    "electronics": {"seo": 65, "technical": 70, "content": 72, "aeo": 68},
    "healthcare": {"seo": 60, "technical": 67, "content": 70, "aeo": 66},
    "default": {"seo": 60, "technical": 60, "content": 60, "aeo": 60}
}

def compute_benchmark_deltas(scores: dict, industry: str):
    data = INDUSTRY_AVG.get(industry.lower(), INDUSTRY_AVG["default"])

    seo_delta = scores["seo_score"] - data["seo"]
    tech_delta = scores["technical_score"] - data["technical"]
    content_delta = scores["content_score"] - data["content"]
    aeo_delta = scores["aeo_score"] - data["aeo"]

    strengths = []
    gaps = []

    if seo_delta > 0: strengths.append("SEO performing above industry.")
    else: gaps.append("SEO below industry average.")

    if tech_delta > 0: strengths.append("Technical score above competitors.")
    else: gaps.append("Technical setup is behind industry.")

    if content_delta > 0: strengths.append("Content quality competitive.")
    else: gaps.append("Content not meeting industry depth.")

    if aeo_delta > 0: strengths.append("Overall AEO is strong.")
    else: gaps.append("Overall AEO needs improvement.")

    return BenchmarkInsights(
        industry=industry,
        seo_delta=seo_delta,
        technical_delta=tech_delta,
        content_delta=content_delta,
        aeo_delta=aeo_delta,
        strengths=strengths,
        gaps=gaps
    )
