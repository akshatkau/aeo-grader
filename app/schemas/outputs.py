# app/schemas/outputs.py
from pydantic import BaseModel
from typing import List, Optional
from app.schemas.score_details import ScoreBreakdown


# -------------------------------------------------------
# Step-3 Competitor Schema
# -------------------------------------------------------
class Competitor(BaseModel):
    title: str
    url: str


# -------------------------------------------------------
# Step-4 Supporting Schemas FIRST  (IMPORTANT ORDER)
# -------------------------------------------------------
class PenaltyReport(BaseModel):
    total_penalty: float
    meta_description_penalty: float
    schema_penalty: float
    alt_text_penalty: float
    cwv_penalty: float
    ux_penalty: float
    notes: List[str] = []


class UXHeuristicInsights(BaseModel):
    ux_score: int
    cta_present: bool
    trust_signals_present: bool
    mobile_friendly: bool
    readability_ok: bool
    issues: List[str] = []


class KeywordInsights(BaseModel):
    keywords_used: int
    total_suggested: int
    missing_keywords: List[str]
    coverage: int   # NEW




class BenchmarkInsights(BaseModel):
    industry: Optional[str]
    seo_delta: int
    technical_delta: int
    content_delta: int
    aeo_delta: int
    strengths: List[str]
    gaps: List[str]


# -------------------------------------------------------
# Normal Step-1 / Step-2 Schemas
# -------------------------------------------------------
class OnPageSummary(BaseModel):
    title: Optional[str]
    meta_description: Optional[str]
    h1: Optional[str]
    headings: Optional[list]
    schema_present: Optional[bool]
    images_with_alt_ratio: Optional[float]


class PerformanceSummary(BaseModel):
    performance_score: int
    core_web_vitals: Optional[dict]
    mobile_friendly: Optional[bool] = None
    fallback: Optional[bool] = None


class ContentInsights(BaseModel):
    intent_coverage: int
    readability_grade: Optional[str]
    expertise_score: int
    missing_sections: List[str]


class Scores(BaseModel):
    seo_score: int
    technical_score: int
    content_score: int
    aeo_score: int


# -------------------------------------------------------
# FINAL RESPONSE SCHEMA — must come LAST
# -------------------------------------------------------
class AnalyzeResponse(BaseModel):
    input_echo: dict
    onpage: OnPageSummary
    performance: PerformanceSummary
    content: ContentInsights
    scores: Scores

    # Step-3
    competitors: List[Competitor]

    # Step-4
    score_breakdown: ScoreBreakdown
    keyword_score: KeywordInsights
    benchmark: BenchmarkInsights
    penalties: PenaltyReport
    ux: UXHeuristicInsights

    recommendations: List[str]
    debug: dict
