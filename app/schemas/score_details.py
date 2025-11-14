# app/schemas/score_details.py

from pydantic import BaseModel
from typing import List, Optional

class ScoreBreakdown(BaseModel):
    seo_weighted: int
    technical_weighted: int
    content_weighted: int
    brand_weighted: int
    competitor_adjustment: int
    penalties: List[str]
    ux_score: int
    final_aeo: int
