# app/services/penalties.py
from app.schemas.outputs import PenaltyReport

def compute_penalties(onpage: dict, performance: dict, llm_raw: dict) -> PenaltyReport:
    penalties = []
    total_penalty = 0

    # --- Meta description ---
    meta_penalty = 0
    if not onpage.get("meta_description"):
        meta_penalty = 10
        penalties.append("Missing meta description")

    # --- Schema ---
    schema_penalty = 0
    if not onpage.get("schema_present"):
        schema_penalty = 8
        penalties.append("Schema markup missing")

    # --- Alt text ---
    alt_penalty = 0
    ratio = onpage.get("images_with_alt_ratio")
    if ratio is not None and ratio < 0.7:
        alt_penalty = 6
        penalties.append("Low alt text coverage")

    # --- Core Web Vitals ---
    cwv_penalty = 0
    if not performance.get("core_web_vitals"):
        cwv_penalty = 5
        penalties.append("Missing Core Web Vitals data")

    # --- LLM readability ---
    ux_penalty = 0
    if llm_raw.get("readability_grade") not in [None, "A", "B", "C"]:
        ux_penalty = 4
        penalties.append("Poor readability grade")

    total_penalty = meta_penalty + schema_penalty + alt_penalty + cwv_penalty + ux_penalty

    return PenaltyReport(
        total_penalty=total_penalty,
        meta_description_penalty=meta_penalty,
        schema_penalty=schema_penalty,
        alt_text_penalty=alt_penalty,
        cwv_penalty=cwv_penalty,
        ux_penalty=ux_penalty,
        notes=penalties,
    )
