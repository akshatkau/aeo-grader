# app/services/location_benchmarks.py

LOCATION_BENCHMARKS = {
    "india": {
        "performance": -10,
        "seo": +5,
        "content": 0,
        "aeo": -5,
    },
    "us": {
        "performance": +10,
        "seo": 0,
        "content": +5,
        "aeo": +8,
    },
    "uk": {
        "performance": +5,
        "seo": +2,
        "content": +4,
        "aeo": +6,
    },
    "europe": {
        "performance": +7,
        "seo": +2,
        "content": +3,
        "aeo": +5,
    },
    "default": {
        "performance": 0,
        "seo": 0,
        "content": 0,
        "aeo": 0,
    }
}


# ----------------------------
# SINGLE SCORE ADJUSTMENT
# ----------------------------
def adjust_score_with_location(score: int, location: str, metric: str):
    if not location:
        return score

    loc = location.lower().strip()
    data = LOCATION_BENCHMARKS.get(loc, LOCATION_BENCHMARKS["default"])

    delta = data.get(metric, 0)

    return max(0, min(100, score + delta))


# ----------------------------
# APPLY LOCATION CONTEXT (WRAPPER)
# ----------------------------
def apply_location_context(all_scores: dict, location: str):
    """
    Modify all score buckets based on regional benchmarks.
    This is what analyze.py expects.
    """
    if not location:
        return all_scores

    all_scores["seo_score"] = adjust_score_with_location(
        all_scores["seo_score"], location, "seo"
    )

    all_scores["technical_score"] = adjust_score_with_location(
        all_scores["technical_score"], location, "performance"
    )

    all_scores["content_score"] = adjust_score_with_location(
        all_scores["content_score"], location, "content"
    )

    all_scores["aeo_score"] = adjust_score_with_location(
        all_scores["aeo_score"], location, "aeo"
    )

    return all_scores
