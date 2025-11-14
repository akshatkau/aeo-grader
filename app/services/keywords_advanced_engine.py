# app/services/keywords_advanced.py
from app.schemas.outputs import KeywordInsights

SUGGESTED_KEYWORDS = {
    "healthcare": ["clinic", "doctor", "treatment", "appointment", "medical"],
    "electronics": ["buy", "online", "specifications", "price", "features"],
    "default": ["services", "solutions", "company", "best", "top"]
}

def keyword_contextual_score(content_text: str, industry: str) -> KeywordInsights:
    text = (content_text or "").lower()
    kw_list = SUGGESTED_KEYWORDS.get(industry.lower(), SUGGESTED_KEYWORDS["default"])

    used = [kw for kw in kw_list if kw in text]
    missing = [kw for kw in kw_list if kw not in used]

    return KeywordInsights(
        keywords_used=len(used),
        total_suggested=len(kw_list),
        missing_keywords=missing
    )
