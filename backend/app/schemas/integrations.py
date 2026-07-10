from pydantic import BaseModel


class IntegrationStatusResponse(BaseModel):
    gemini_configured: bool
    groq_configured: bool
    alpha_vantage_configured: bool
    fmp_configured: bool
    database_configured: bool
    r2_configured: bool
    sec_user_agent_configured: bool
    unavailable_features: list[str]

