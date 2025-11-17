import json
from openai import OpenAI
from app.core.config import settings

client = OpenAI(api_key=settings.OPENAI_API_KEY)


def build_prompt(content_text, company, product, industry, location):
    return f"""
You are an expert SEO and AEO (Answer Engine Optimization) evaluator.

Analyze the webpage content based on the following:

---
COMPANY CONTEXT
Company: {company}
Product/Service: {product}
Industry: {industry}
Location: {location}
---

WEBPAGE CONTENT (TRUNCATED)
{content_text[:5000]}
---

RETURN VALID JSON ONLY WITH THE FOLLOWING FIELDS:
{{
  "intent_coverage": "0-100",
  "readability_grade": "A1/A2/B1/B2/C1/C2",
  "expertise_score": "0-100",
  "missing_sections": ["list"],
  "recommendations": ["list"],
  "content_score": "0-100",
  "aeo_score": "0-100"
}}

Evaluation Rules:
- Intent coverage: How well content matches search intent.
- Readability: Use CEFR levels.
- Expertise score: Authority, clarity, helpfulness.
- Missing sections: Identify gaps (FAQ, pricing, process, comparisons, etc.)
- Recommendations: Highly specific SEO/AEO improvements.
- Content score: Weighted evaluation.
- AEO score: How well page satisfies answer engines.

Return ONLY JSON. No explanations.
"""



def analyze_content_llm(content_text, company, product, industry, location):
    prompt = build_prompt(content_text, company, product, industry, location)

    response = client.chat.completions.create(
        model="gpt-4o-mini",
        temperature=0.3,
        messages=[
            {"role": "system", "content": "You are an SEO content analysis engine."},
            {"role": "user", "content": prompt}
        ]
    )

    output = response.choices[0].message.content

    # Try to parse clean JSON
    try:
        return json.loads(output)
    except:
        # Try to extract JSON if the LLM added text around it
        start = output.find("{")
        end = output.rfind("}") + 1
        return json.loads(output[start:end])

# --------------------------------------------------------
# New Feature: AI Rewrite Engine
# --------------------------------------------------------
async def rewrite_content(raw_text: str, tone: str = "professional", target_keywords: list[str] = None):
    """
    Rewrite content for SEO + clarity + tone control.

    Args:
        raw_text (str): Content to rewrite
        tone (str): writing style ("professional", "friendly", "salesy", etc.)
        target_keywords (list): optional keywords to include in rewrite

    Returns:
        dict: rewritten text + summary notes
    """

    if target_keywords is None:
        target_keywords = []

    prompt = f"""
You are an SEO rewriting assistant.

Rewrite the following content to improve:
- Clarity
- SEO ranking potential
- Readability
- Tone: {tone}

If possible, naturally include these keywords:
{", ".join(target_keywords)}

DO NOT hallucinate new facts.

Return the rewritten text ONLY.
    
Content to rewrite:
-------------------
{raw_text}
"""

    try:
        response = client.responses.create(
            model="gpt-4o-mini",
            input=prompt,
            temperature=0.4  # keep quality consistent
        )

        rewritten = response.output_text
        return {
            "rewritten_text": rewritten,
        }

    except Exception as e:
        return {
            "error": str(e),
            "rewritten_text": raw_text
        }
