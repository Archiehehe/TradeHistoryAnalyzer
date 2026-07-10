from datetime import UTC, datetime

from fastapi import APIRouter

from app.core.config import get_settings
from app.schemas.health import HealthResponse

router = APIRouter()


@router.get("/health", response_model=HealthResponse)
def healthcheck() -> HealthResponse:
    settings = get_settings()
    return HealthResponse(
        status="ok",
        timestamp=datetime.now(UTC),
        database_configured=bool(settings.database_dsn),
        environment=settings.environment,
    )

