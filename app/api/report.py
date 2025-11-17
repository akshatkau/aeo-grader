from fastapi import APIRouter, Response
from reportlab.platypus import (
    SimpleDocTemplate,
    Paragraph,
    Spacer,
    Table,
    TableStyle
)
from reportlab.lib.styles import getSampleStyleSheet
from reportlab.lib import colors
import tempfile

from app.schemas.outputs import AnalyzeResponse


router = APIRouter(prefix="/api/report", tags=["report"])


# ---------------------------------------------------------
#  PDF BUILDER — takes AnalyzeResponse model (dict form)
# ---------------------------------------------------------
def build_pdf_from_report(report: dict) -> bytes:
    styles = getSampleStyleSheet()
    title_style = styles["Title"]
    heading_style = styles["Heading2"]
    body_style = styles["BodyText"]

    tmp = tempfile.NamedTemporaryFile(delete=False, suffix=".pdf")
    pdf = SimpleDocTemplate(tmp.name)
    story = []

        # ------------------------ COVER PAGE ------------------------
    story.append(Paragraph("AEO Optimization Report", title_style))
    story.append(Spacer(1, 20))

    # NEW FIX — read from input_echo instead of root
    echo = report.get("input_echo", {})

    cover_fields = [
        ("Website", echo.get("url")),
        ("Company", echo.get("company_name")),
        ("Industry", echo.get("industry")),
        ("Location", echo.get("location")),
        ("Product", echo.get("product")),
    ]

    for label, value in cover_fields:
        story.append(Paragraph(f"{label}: {value}", body_style))

    story.append(Spacer(1, 30))


    # ------------------------ SCORES ------------------------
    story.append(Paragraph("Overall Scores", heading_style))

    scores = report["scores"]
    scores_table = Table([
        ["SEO Score", scores["seo_score"]],
        ["Technical Score", scores["technical_score"]],
        ["Content Score", scores["content_score"]],
        ["AEO Score", scores["aeo_score"]],
    ])

    scores_table.setStyle(TableStyle([
        ("BACKGROUND", (0, 0), (-1, 0), colors.grey),
        ("TEXTCOLOR", (0, 0), (-1, 0), colors.white),
        ("ALIGN", (0, 0), (-1, -1), "CENTER"),
        ("BOX", (0, 0), (-1, -1), 1, colors.black),
        ("GRID", (0, 0), (-1, -1), 0.5, colors.grey),
    ]))

    story.append(scores_table)
    story.append(Spacer(1, 20))

    # ------------------------ PERFORMANCE ------------------------
    story.append(Paragraph("Technical Performance", heading_style))

    perf = report["performance"]
    perf_table = Table([
        ["Performance Score", perf.get("performance_score")],
        ["LCP", perf.get("core_web_vitals", {}).get("lcp")],
        ["CLS", perf.get("core_web_vitals", {}).get("cls")],
        ["FCP", perf.get("core_web_vitals", {}).get("fcp")],
        ["Mobile Friendly", perf.get("mobile_friendly")],
    ])

    perf_table.setStyle(TableStyle([
        ("ALIGN", (0, 0), (-1, -1), "LEFT"),
        ("GRID", (0, 0), (-1, -1), 0.5, colors.lightgrey),
    ]))

    story.append(perf_table)
    story.append(Spacer(1, 20))

    # ------------------------ KEYWORD COVERAGE ------------------------
    story.append(Paragraph("Keyword Coverage", heading_style))

    kw = report["keyword_score"]
    story.append(Paragraph(f"Keywords Used: {kw['keywords_used']}", body_style))
    story.append(Paragraph(f"Total Suggested: {kw['total_suggested']}", body_style))
    story.append(Paragraph("Missing Keywords:", body_style))

    for kwd in kw.get("missing_keywords", []):
        story.append(Paragraph(f"- {kwd}", body_style))

    story.append(Spacer(1, 20))

    # ------------------------ RECOMMENDATIONS ------------------------
    story.append(Paragraph("Recommendations", heading_style))
    for rec in report.get("recommendations", []):
        story.append(Paragraph(f"- {rec}", body_style))
        
        
        
    # ------------------------ SCORE EXPLANATION ------------------------
    story.append(Paragraph("Score Interpretation Guide", heading_style))
    story.append(Paragraph("""
    <b>SEO Score (0–100)</b><br/>
    Measures metadata, headings, alt text, structured data, and keyword presence.<br/>
    0–40: Poor<br/>
    40–70: Average<br/>
    70–85: Good<br/>
    85–100: Excellent<br/><br/>

    <b>Technical Score (0–100)</b><br/>
    Based on performance, Core Web Vitals, mobile-friendliness.<br/>
    0–40: Poor<br/>
    40–70: Needs Improvement<br/>
    70–90: Good<br/>
    90–100: Excellent<br/><br/>

    <b>Content Score (0–100)</b><br/>
    Measures E-E-A-T, completeness, readability, and intent coverage.<br/>
    0–40: Weak content<br/>
    40–70: Needs expansion<br/>
    70–90: Strong<br/>
    90–100: Excellent<br/><br/>

    <b>AEO Score (0–100)</b><br/>
    Final weighted score combining SEO, technical, content, UX, and brand signals.<br/>
    0–50: Poor<br/>
    50–75: Average<br/>
    75–90: Good<br/>
    90–100: Excellent<br/><br/>
    """, body_style))
    story.append(Spacer(1, 20))


    # ------------------------ BUILD PDF ------------------------
    pdf.build(story)

    with open(tmp.name, "rb") as f:
        return f.read()


# ---------------------------------------------------------
#  FINAL FIXED ENDPOINT — expects AnalyzeResponse object
# ---------------------------------------------------------
@router.post("/pdf")
async def generate_pdf(data: AnalyzeResponse):
    """
    Accepts full AnalyzeResponse JSON from the frontend
    and generates a PDF.

    This prevents 422 errors and avoids re-running /analyze.
    """
    pdf_bytes = build_pdf_from_report(data.model_dump())

    return Response(
        content=pdf_bytes,
        media_type="application/pdf",
        headers={
            "Content-Disposition": 'attachment; filename="AEO_Report.pdf"'
        }
    )
