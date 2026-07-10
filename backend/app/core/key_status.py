from fastapi import HTTPException

from app.core.config import Settings
from app.schemas.integrations import IntegrationStatusResponse


def build_integration_status(settings: Settings) -> IntegrationStatusResponse:
    gemini_configured = settings.gemini_api_key is not None
    groq_configured = settings.groq_api_key is not None
    alpha_vantage_configured = settings.alpha_vantage_api_key is not None
    fmp_configured = settings.fmp_api_key is not None
    database_configured = settings.database_dsn is not None
    r2_configured = settings.r2_configured
    sec_user_agent_configured = bool(settings.sec_user_agent)

    unavailable_features: list[str] = []
    if not gemini_configured:
        unavailable_features.append("Final AI behavior report generation is disabled because GEMINI_API_KEY is missing.")
    if not groq_configured:
        unavailable_features.append("AI-assisted transaction classification is disabled because GROQ_API_KEY is missing.")
    if not alpha_vantage_configured:
        unavailable_features.append("Price-based timing analysis is disabled because ALPHA_VANTAGE_API_KEY is missing.")
    if not fmp_configured:
        unavailable_features.append("Fallback market-data enrichment through FMP is disabled because FMP_API_KEY is missing.")
    if not r2_configured:
        unavailable_features.append("Cloud storage is disabled because R2 credentials are incomplete; local storage will be used instead.")
    if not sec_user_agent_configured:
        unavailable_features.append("SEC filing lookups are disabled because SEC_USER_AGENT is missing.")
    if not database_configured:
        unavailable_features.append("The backend cannot start report processing until DATABASE_URL or NEON_DATABASE_URL is configured.")

    return IntegrationStatusResponse(
        gemini_configured=gemini_configured,
        groq_configured=groq_configured,
        alpha_vantage_configured=alpha_vantage_configured,
        fmp_configured=fmp_configured,
        database_configured=database_configured,
        r2_configured=r2_configured,
        sec_user_agent_configured=sec_user_agent_configured,
        unavailable_features=unavailable_features,
    )


def assert_startup_requirements(settings: Settings) -> None:
    if not settings.database_dsn:
        raise RuntimeError(
            "DATABASE_URL or NEON_DATABASE_URL must be configured before starting the backend. "
            "Copy .env.example to .env and provide the Neon Postgres connection string."
        )


def ensure_database_ready(settings: Settings) -> None:
    if not settings.database_dsn:
        raise HTTPException(
            status_code=503,
            detail="Database is not configured. Set DATABASE_URL or NEON_DATABASE_URL and restart the backend.",
        )

