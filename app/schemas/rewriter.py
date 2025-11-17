# app/schemas/rewriter.py
from pydantic import BaseModel, Field
from typing import List, Optional

class RewriteRequest(BaseModel):
    content: str = Field(..., description="Original content (plain text or HTML)")
    target_keywords: Optional[List[str]] = Field(default_factory=list)
    tone: Optional[str] = "neutral"  # e.g. friendly, professional, witty
    seo_focus: Optional[bool] = True
    preserve_html: Optional[bool] = False
    max_length: Optional[int] = 800
    variations: Optional[int] = 2

class Variant(BaseModel):
    text: str
    keywords_covered: int
    length: int
    notes: Optional[List[str]] = []

class RewriteResponse(BaseModel):
    original_length: int
    variants: List[Variant]
    explanation: Optional[str] = None
    warnings: Optional[List[str]] = []
