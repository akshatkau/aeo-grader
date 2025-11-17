# app/services/rewriter.py
from typing import List, Dict
from app.schemas.rewriter import RewriteRequest, Variant
from app.core.config import settings
# Use your existing LLM wrapper — example using OpenAI (replace with your wrapper)
from openai import OpenAI
import re

client = OpenAI(api_key=settings.OPENAI_API_KEY)

PROMPT_TEMPLATE = """
You are an SEO copywriter. Rewrite the following content to improve clarity and SEO.
Requirements:
- Tone: {tone}
- Max length: {max_len} characters (approx)
- If seo_focus is true, include / prioritize these keywords if natural: {keywords}
- Preserve HTML: {preserve_html}
- Provide only the rewritten content, no explanation metadata.

Original Content:
{content}

--- END ---
"""

def build_prompt(req: RewriteRequest) -> str:
    kw_text = ", ".join(req.target_keywords) if req.target_keywords else "none"
    return PROMPT_TEMPLATE.format(
        tone=req.tone,
        max_len=req.max_length,
        keywords=kw_text,
        preserve_html=str(req.preserve_html),
        content=req.content
    )

def call_llm(prompt: str, max_tokens: int=512, n: int=1) -> List[str]:
    # Example: OpenAI client usage. Replace with your wrapper if different.
    resp = client.chat.completions.create(
        model="gpt-4o-mini",  # change as needed
        messages=[{"role":"user","content":prompt}],
        max_tokens=max_tokens,
        n=n,
        temperature=0.2
    )
    results = []
    for choice in resp.choices:
        text = choice.message.get("content", "") if hasattr(choice, "message") else choice.text
        results.append(text.strip())
    return results

def keyword_coverage(text: str, keywords: List[str]) -> int:
    t = text.lower()
    covered = sum(1 for k in keywords if k.lower() in t)
    return covered

def generate_variants(req: RewriteRequest) -> Dict:
    prompt = build_prompt(req)
    # ask LLM for `variations` responses
    responses = call_llm(prompt, max_tokens=min(1024, req.max_length*2//3), n=req.variations)
    variants = []
    for r in responses:
        # simple cleanup
        cleaned = r.strip()
        # If preserve_html=False, strip HTML tags from LLM output for safety (optional)
        if not req.preserve_html:
            cleaned = re.sub(r"<\/?[^>]+>", "", cleaned)

        kw_cov = keyword_coverage(cleaned, req.target_keywords)
        variants.append(Variant(
            text=cleaned,
            keywords_covered=kw_cov,
            length=len(cleaned),
            notes=[]
        ))
    return {
        "original_length": len(req.content),
        "variants": variants
    }
