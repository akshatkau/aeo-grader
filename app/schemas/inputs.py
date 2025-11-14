from pydantic import BaseModel, HttpUrl, Field

class AnalyzeRequest(BaseModel):
    url: HttpUrl = Field(..., description="Primary website URL to analyze")
    company_name: str = Field("", description="Brand/Company name")
    location: str = Field("", description="City/State/Country")
    product: str = Field("", description="Primary product or service")
    industry: str = Field("", description="Industry vertical")
