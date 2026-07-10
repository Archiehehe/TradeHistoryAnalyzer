from fastapi import APIRouter

from app.api.routes import health, integrations, reports, uploads

api_router = APIRouter()
api_router.include_router(health.router, tags=["health"])
api_router.include_router(integrations.router, prefix="/integrations", tags=["integrations"])
api_router.include_router(uploads.router, prefix="/uploads", tags=["uploads"])
api_router.include_router(reports.router, prefix="/reports", tags=["reports"])

