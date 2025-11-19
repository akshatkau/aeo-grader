from typing import List, Dict
from app.schemas.rewriter import RewriteRequest, Variant
from app.core.config import settings
import re

# Graceful import for OpenAI
try:
    from openai import OpenAI
    OPENAI_AVAILABLE = True
except ImportError:
    OPENAI_AVAILABLE = False

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
    if not OPENAI_AVAILABLE:
        return [f"[Mock] Rewrite: {prompt[:50]}... (OpenAI not installed)"] * n
        
    if not settings.OPENAI_API_KEY:
        return [f"[Mock] Rewrite: {prompt[:50]}... (Missing API Key)"] * n

    client = OpenAI(api_key=settings.OPENAI_API_KEY)
    
    try:
        resp = client.chat.completions.create(
            model="gpt-4o-mini",  
            messages=[{"role":"user","content":prompt}],
            max_tokens=max_tokens,
            n=n,
            temperature=0.7
        )
        results = []
        for choice in resp.choices:
            text = choice.message.content if choice.message.content else ""
            results.append(text.strip())
        return results
    except Exception as e:
        print(f"LLM Call Error: {e}")
        return [f"Error generating content: {str(e)}"]

def keyword_coverage(text: str, keywords: List[str]) -> int:
    if not keywords: return 0
    t = text.lower()
    covered = sum(1 for k in keywords if k.lower() in t)
    return covered

# ✅ FIX: Added adapter_name parameter here to match API call
def generate_variants(req: RewriteRequest, adapter_name: str = "openai") -> Dict:
    
    # 1. Handle Mock Mode (Fast UI testing)
    if adapter_name == "mock":
        return {
            "original_length": len(req.content),
            "variants": [
                Variant(
                    text=f"[Mock] {req.content[:50]}... (Tone: {req.tone})", 
                    keywords_covered=1, 
                    length=len(req.content), 
                    notes=["Mock mode active"]
                ) for _ in range(req.variations or 1)
            ]
        }

    # 2. Handle Real Logic (OpenAI)
    prompt = build_prompt(req)
    
    # ask LLM for `variations` responses
    responses = call_llm(prompt, max_tokens=min(1024, (req.max_length or 800)), n=(req.variations or 1))
    
    variants = []
    for r in responses:
        # simple cleanup
        cleaned = r.strip()
        # If preserve_html=False, strip HTML tags
        if not req.preserve_html:
            cleaned = re.sub(r"<\/?[^>]+>", "", cleaned)

        kw_cov = keyword_coverage(cleaned, req.target_keywords or [])
        
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