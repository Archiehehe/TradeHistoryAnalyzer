from uuid import UUID

from fastapi import APIRouter, File, Form, UploadFile

from app.api.deps import AppSettings, DbSession
from app.schemas.uploads import ParsePreviewResponse, UploadBatchResponse
from app.services.uploads import build_parse_preview, process_portfolio_upload, process_transaction_upload

router = APIRouter()


@router.post("/transactions", response_model=UploadBatchResponse)
async def upload_transactions(
    db: DbSession,
    settings: AppSettings,
    files: list[UploadFile] = File(...),
    notes: str | None = Form(default=None),
) -> UploadBatchResponse:
    return await process_transaction_upload(files, notes, db, settings)


@router.post("/portfolio", response_model=UploadBatchResponse)
async def upload_portfolio(
    db: DbSession,
    settings: AppSettings,
    files: list[UploadFile] = File(...),
    notes: str | None = Form(default=None),
) -> UploadBatchResponse:
    return await process_portfolio_upload(files, notes, db, settings)


@router.get("/{upload_id}/parse-preview", response_model=ParsePreviewResponse)
async def get_parse_preview(upload_id: UUID, db: DbSession, settings: AppSettings) -> ParsePreviewResponse:
    return build_parse_preview(str(upload_id), db, settings)
