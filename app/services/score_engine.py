# app/services/score_engine.py
from app.schemas.score_details import ScoreBreakdown

def compute_weighted_score(scores: dict, penalties, ux) -> ScoreBreakdown:
    W_SEO = 0.30
    W_TECH = 0.30
    W_CONTENT = 0.25
    W_BRAND = 0.15

    brand_strength = 70

    seo_w = scores["seo_score"] * W_SEO
    tech_w = scores["technical_score"] * W_TECH
    content_w = scores["content_score"] * W_CONTENT
    brand_w = brand_strength * W_BRAND

    base_total = seo_w + tech_w + content_w + brand_w

    final_aeo = max(0, base_total - penalties.total_penalty)

    return ScoreBreakdown(
        seo_weighted=round(seo_w),
        technical_weighted=round(tech_w),
        content_weighted=round(content_w),
        brand_weighted=round(brand_w),
        competitor_adjustment=0,
        penalties=penalties.notes,
        ux_score=ux.ux_score,
        final_aeo=round(final_aeo)
    )
