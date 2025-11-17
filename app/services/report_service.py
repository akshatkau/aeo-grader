from reportlab.lib.pagesizes import letter
from reportlab.pdfgen import canvas
from reportlab.lib.units import inch
import io

def generate_pdf_report(data: dict) -> bytes:
    buffer = io.BytesIO()
    c = canvas.Canvas(buffer, pagesize=letter)
    text = c.beginText(1 * inch, 10 * inch)
    text.setFont("Helvetica", 12)

    text.textLine("AEO Grader Report")
    text.textLine("----------------------------------")
    text.textLine("")

    # Basic info
    text.textLine(f"URL: {data['input_echo']['url']}")
    text.textLine(f"Company: {data['input_echo'].get('company_name')}")
    text.textLine(f"Industry: {data['input_echo'].get('industry')}")
    text.textLine("")

    # Scores
    scores = data["scores"]
    text.textLine("Scores:")
    text.textLine(f"- SEO Score: {scores['seo_score']}")
    text.textLine(f"- Technical Score: {scores['technical_score']}")
    text.textLine(f"- Content Score: {scores['content_score']}")
    text.textLine(f"- AEO Score: {scores['aeo_score']}")
    text.textLine("")

    # Recommendations
    text.textLine("Recommendations:")
    for r in data["recommendations"]:
        text.textLine(f"• {r}")

    c.drawText(text)
    c.showPage()
    c.save()

    pdf_data = buffer.getvalue()
    buffer.close()
    return pdf_data
