# app/api/analyze.py

from fastapi import APIRouter, HTTPException
from typing import List

from app.schemas.inputs import AnalyzeRequest
from app.schemas.outputs import (
    AnalyzeResponse,
    OnPageSummary,
    PerformanceSummary,
    ContentInsights,
    Scores,
    Competitor,
    ScoreBreakdown,
    KeywordInsights,
    BenchmarkInsights,
    UXHeuristicInsights,
    PenaltyReport
)

from app.services.crawler import fetch_html, parse_onpage
from app.services.brand import enrich_brand_context

# keywords
from app.services.keyword_engine_base import extract_keywords
from app.services.keywords_advanced_engine import keyword_contextual_score

# scoring & engines
from app.services.scoring import (
    score_onpage,
    score_technical,
    score_content,
    score_aeo,
    apply_industry_context,
)
from app.services.score_engine import compute_weighted_score

# penalties & ux
from app.services.penalties import compute_penalties
from app.services.ux import compute_ux_score

# other services
from app.services.performance import get_performance
from app.services.location_benchmarks import apply_location_context
from app.services.search import get_serp_competitors
from app.services.llm import analyze_content_llm
from app.services.benchmarks_v2 import compute_benchmark_deltas
from app.core.config import settings

router = APIRouter(prefix="/api", tags=["analyze"])


def to_int(value):
    """Normalize many possible LLM numeric formats to int (0-100)."""
    try:
        if value is None:
            return 50
        if isinstance(value, int):
            return value
        if isinstance(value, float):
            return int(value)
        if isinstance(value, str):
            clean = value.strip().replace("%", "")
            if "-" in clean:
                clean = clean.split("-")[0]
            return int(float(clean))
    except Exception:
        return 50


@router.post("/analyze", response_model=AnalyzeResponse)
async def analyze(req: AnalyzeRequest):
    # 1) Brand context
    brand_ctx = enrich_brand_context(
        req.company_name, req.location, req.product, req.industry
    )

    # 2) Crawl with Graceful Fallback
    html = None
    crawl_error = None
    try:
        html = await fetch_html(str(req.url), timeout=settings.TIMEOUT_SECS)
    except Exception as e:
        crawl_error = str(e)
        print(f"Crawl failed: {e}")

    # --- BLOCKING HANDLER START ---
    if not html:
        # If HTML is empty (blocked or failed), return a "Zero Score" response immediately.
        return AnalyzeResponse(
            input_echo=req.model_dump(),
            
            onpage=OnPageSummary(
                title="Access Denied / Scan Failed",
                h1="Could not access website",
                meta_description="The website blocked our scanner. This is common with high-security e-commerce sites (Ajio, Amazon, etc) when scanning without residential proxies.",
                headings=[],
                schema_present=False,
                images_with_alt_ratio=0.0
            ),
            
            # ⭐ FIX: Changed 'score' to 'performance_score'
            performance=PerformanceSummary(performance_score=0, core_web_vitals={}),
            
            content=ContentInsights(
                intent_coverage=0,
                readability_grade="N/A",
                expertise_score=0,
                missing_sections=[]
            ),
            
            scores=Scores(
                aeo_score=0, seo_score=0, technical_score=0, content_score=0
            ),
            
            competitors=[],
            
            score_breakdown=ScoreBreakdown(
                seo_weighted=0, technical_weighted=0, content_weighted=0, 
                brand_weighted=0, competitor_adjustment=0, penalties=[], 
                ux_score=0, final_aeo=0
            ),
            
            keyword_score=KeywordInsights(
                keywords_used=0, total_suggested=0, missing_keywords=[], coverage=0
            ),
            
            benchmark=BenchmarkInsights(
                industry=req.industry, seo_delta=0, technical_delta=0, 
                content_delta=0, aeo_delta=0, strengths=[], gaps=[]
            ),
            
            ux=UXHeuristicInsights(
                ux_score=0, cta_present=False, trust_signals_present=False,
                mobile_friendly=False, readability_ok=False, issues=[]
            ),
            
            penalties=PenaltyReport(
                total_penalty=0, meta_description_penalty=0, schema_penalty=0,
                alt_text_penalty=0, cwv_penalty=0, ux_penalty=0, notes=[]
            ),
            
            recommendations=[
                "The scanner was blocked by the website's firewall.",
                "Try using a Residential Proxy to bypass bot detection.",
                f"Debug info: {crawl_error or 'Unknown error'}"
            ],
            
            debug={"error": "Blocked", "details": crawl_error}
        )
    # --- BLOCKING HANDLER END ---


    # 3) Competitor discovery (SERP)
    try:
        query_parts = list(
            filter(None, [req.company_name, req.product, req.industry, req.location])
        )
        search_query = " ".join(query_parts) if query_parts else str(req.url)
        competitors_raw = []
        try:
            competitors_raw = get_serp_competitors(search_query) or []
        except Exception as se:
            competitors_raw = []
        
        # normalize to Competitor models
        competitors: List[Competitor] = []
        for c in competitors_raw:
            try:
                if isinstance(c, dict):
                    title = c.get("title") or c.get("name") or c.get("site") or "Unknown"
                    url = c.get("url") or c.get("link") or ""
                    competitors.append(Competitor(title=title, url=url))
                else:
                    competitors.append(Competitor(title=str(c), url=""))
            except Exception:
                continue
    except Exception:
        competitors = []

    # 4) On-page parsing
    onpage = parse_onpage(html) or {}
    
    # FIX HEADINGS FORMAT for Pydantic
    raw_headings = onpage.get("headings", []) or []
    if isinstance(raw_headings, dict):
        flat_headings = []
        for tag, items in raw_headings.items():
            if isinstance(items, list):
                flat_headings.extend(items)
        onpage["headings"] = flat_headings
    else:
        onpage["headings"] = raw_headings

    # 5) Keyword extraction (simple)
    extracted_keywords = []
    try:
        extracted_keywords = extract_keywords(onpage.get("content_text", "") or "")
    except Exception:
        extracted_keywords = []

    # 6) Performance metrics
    performance = await get_performance(str(req.url))

    # 7) LLM analysis (content insights)
    try:
        llm_raw = analyze_content_llm(
            content_text=onpage.get("content_text", ""),
            company=brand_ctx.get("company_name"),
            product=brand_ctx.get("product"),
            industry=brand_ctx.get("industry"),
            location=brand_ctx.get("location"),
        ) or {}
    except Exception:
        llm_raw = {}

    # 8) Normalize LLM numeric fields
    intent_coverage = to_int(llm_raw.get("intent_coverage"))
    expertise_score = to_int(llm_raw.get("expertise_score"))
    content_score_llm = to_int(llm_raw.get("content_score"))
    aeo_score_llm = to_int(llm_raw.get("aeo_score"))

    # 9) Algorithmic baseline scores
    seo_score = score_onpage(onpage)
    technical_score = score_technical(performance)
    content_score_algo = score_content(intent_coverage, expertise_score)
    aeo_score_algo = score_aeo(seo_score, technical_score, content_score_algo)

    # Prefer valid LLM-provided scores where available
    final_content_score = content_score_llm if content_score_llm != 50 else content_score_algo
    final_aeo_score = aeo_score_llm if aeo_score_llm != 50 else aeo_score_algo

    base_scores = {
        "seo_score": seo_score,
        "technical_score": technical_score,
        "content_score": final_content_score,
        "aeo_score": final_aeo_score,
    }

    # 10) Industry adjustments
    try:
        if req.industry:
            base_scores = apply_industry_context(base_scores, req.industry)
    except Exception:
        pass

    # 11) Location adjustments
    try:
        if req.location:
            base_scores = apply_location_context(base_scores, req.location)
    except Exception:
        pass

    # 12) Keyword Extraction + Contextual Scoring
    try:
        keyword_score_obj = keyword_contextual_score(
            content_text=onpage.get("content_text", "") or "",
            industry=req.industry or "default",
            product=req.product or "",
            company=req.company_name or ""
        )
    except Exception:
        keyword_score_obj = KeywordInsights(
            keywords_used=0,
            total_suggested=0,
            missing_keywords=[],
            coverage=0
        )

    # 13) UX heuristics
    try:
        ux_obj = compute_ux_score(onpage, performance)
    except Exception:
        ux_obj = UXHeuristicInsights(
            ux_score=60,
            cta_present=False,
            trust_signals_present=False,
            mobile_friendly=bool(performance.get("mobile_friendly", False)),
            readability_ok=False,
            issues=[],
        )

    # 14) Penalties
    try:
        penalties_obj = compute_penalties(onpage, performance, llm_raw)
        penalty_total = getattr(penalties_obj, "total_penalty", 0)
    except Exception:
        penalties_obj = PenaltyReport(
            total_penalty=0,
            meta_description_penalty=0,
            schema_penalty=0,
            alt_text_penalty=0,
            cwv_penalty=0,
            ux_penalty=0,
            notes=[],
        )
        penalty_total = 0

    # 15) Weighted scoring engine
    try:
        score_breakdown: ScoreBreakdown = compute_weighted_score(
            base_scores, penalties_obj, ux_obj
        )
    except Exception:
        score_breakdown = ScoreBreakdown(
            seo_weighted=round(base_scores["seo_score"] * 0.3),
            technical_weighted=round(base_scores["technical_score"] * 0.3),
            content_weighted=round(base_scores["content_score"] * 0.25),
            brand_weighted=round(15),
            competitor_adjustment=len(competitors) * 2,
            penalties=penalties_obj.notes if hasattr(penalties_obj, "notes") else [],
            ux_score=getattr(ux_obj, "ux_score", 50),
            final_aeo=max(0, round(base_scores["aeo_score"] - penalty_total)),
        )

    # 16) Benchmarks
    try:
        benchmark_obj: BenchmarkInsights = compute_benchmark_deltas(
            req.industry, base_scores, req.location
        )
    except Exception:
        benchmark_obj = BenchmarkInsights(
            industry=req.industry,
            seo_delta=0,
            technical_delta=0,
            content_delta=0,
            aeo_delta=0,
            strengths=[],
            gaps=[],
        )

    # 17) Recommendations
    recs = []
    if not onpage.get("schema_present"):
        recs.append("Add structured data (JSON-LD) for Organization, Product, or FAQ.")
    if not onpage.get("meta_description"):
        recs.append("Add a meta description (120–155 chars) including primary keyword.")
    ratio = onpage.get("images_with_alt_ratio")
    if ratio is not None and ratio < 0.8:
        recs.append("Improve image alt text coverage (>80% recommended).")
    
    missing = llm_raw.get("missing_sections", [])
    if isinstance(missing, list):
        for m in missing:
            recs.append(f"Missing key section: {m}")
    
    if req.product and any("Explicit product" in s for s in (missing or [])):
        recs.append(f"Mention your product ('{req.product}') more clearly in headings and content.")

    # 18) Build & return final response
    scores_int = {k: int(round(v)) for k, v in base_scores.items()}

    return AnalyzeResponse(
        input_echo=req.model_dump(),

        onpage=OnPageSummary(
            title=onpage.get("title"),
            meta_description=onpage.get("meta_description"),
            h1=onpage.get("h1"),
            headings=onpage.get("headings"),
            schema_present=onpage.get("schema_present"),
            images_with_alt_ratio=onpage.get("images_with_alt_ratio"),
        ),

        performance=PerformanceSummary(**performance),

        content=ContentInsights(
            intent_coverage=intent_coverage,
            readability_grade=llm_raw.get("readability_grade"),
            expertise_score=expertise_score,
            missing_sections=llm_raw.get("missing_sections", []),
        ),

        scores=Scores(
            seo_score=scores_int["seo_score"],
            technical_score=scores_int["technical_score"],
            content_score=scores_int["content_score"],
            aeo_score=scores_int["aeo_score"],
        ),

        competitors=competitors,
        score_breakdown=score_breakdown,
        keyword_score=keyword_score_obj,
        benchmark=benchmark_obj,
        ux=ux_obj,
        penalties=penalties_obj,
        recommendations=recs,

        debug={
            "extracted_keywords": extracted_keywords,
            "raw_llm": llm_raw,
            "penalties": penalties_obj.notes,
            "base_scores_before_rounding": base_scores,
        },
    )