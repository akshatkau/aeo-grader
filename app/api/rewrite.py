from fastapi import APIRouter, HTTPException, Query
from app.schemas.rewriter import RewriteRequest, RewriteResponse
from app.services.rewriter import generate_variants

router = APIRouter(prefix="/api", tags=["rewrite"])

@router.post("/rewrite", response_model=RewriteResponse)
async def rewrite_endpoint(
    req: RewriteRequest,
    adapter: str = Query("openai", description="LLM adapter (mock|openai)")
):
    """
    AI Rewrite Engine
    Accepts RewriteRequest → returns RewriteResponse.
    Supports multiple LLM adapters.
    """
    try:
        # Pass the adapter to the service
        output = generate_variants(req, adapter_name=adapter)
        return RewriteResponse(**output)
    except Exception as e:
        print(f"Rewrite API Error: {e}")
        raise HTTPException(status_code=500, detail=str(e))