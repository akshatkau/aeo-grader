# app/services/benchmarks.py

industry_benchmarks = {
    "electronics": {
        "aeo": 72,
        "seo": 68,
        "technical": 75,
        "content": 70,
        "intent_coverage": 65,
        "readability": "B2",
        "eat": 72,
        "lcp": 4.8,  # seconds
        "cls": 0.09,
        "fcp": 2.4
    },

    "healthcare": {
        "aeo": 65,
        "seo": 60,
        "technical": 70,
        "content": 72,
        "intent_coverage": 70,
        "readability": "C1",
        "eat": 80,
        "lcp": 5.2,
        "cls": 0.12,
        "fcp": 2.8
    },

    "finance": {
        "aeo": 78,
        "seo": 72,
        "technical": 82,
        "content": 74,
        "intent_coverage": 75,
        "readability": "B2",
        "eat": 85,
        "lcp": 4.2,
        "cls": 0.08,
        "fcp": 2.0
    },

    "hospitality": {
        "aeo": 70,
        "seo": 65,
        "technical": 68,
        "content": 75,
        "intent_coverage": 80,
        "readability": "B1",
        "eat": 78,
        "lcp": 5.5,
        "cls": 0.14,
        "fcp": 3.0
    }
}

def adjust_score_with_industry(score: float, industry: str, score_type: str):
    """
    Adjust the raw score based on industry benchmark.
    score_type: aeo, seo, technical, content
    """

    industry = (industry or "").lower()
    if industry not in industry_benchmarks:
        return score  # no adjustment

    benchmark = industry_benchmarks[industry][score_type]

    # Example: If benchmark is 80 and your score is 70 → relative score increases.
    adjusted = (score / benchmark) * 100

    return round(min(max(adjusted, 0), 100), 2)
