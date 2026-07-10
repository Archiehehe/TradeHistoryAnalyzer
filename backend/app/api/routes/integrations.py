from fastapi import APIRouter

from app.core.config import get_settings
from app.core.key_status import build_integration_status
from app.schemas.integrations import IntegrationStatusResponse

router = APIRouter()


@router.get("/status", response_model=IntegrationStatusResponse)
def integration_status() -> IntegrationStatusResponse:
    return build_integration_status(get_settings())

