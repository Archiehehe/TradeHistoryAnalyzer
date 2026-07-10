from uuid import uuid4

from fastapi import HTTPException, UploadFile
from sqlalchemy import select
from sqlalchemy.orm import Session

from app.ai.router import AIRouter
from app.core.config import Settings
from app.core.key_status import build_integration_status
from app.models.entities import CurrentPosition, ParseWarning, RawFile, Transaction, Upload
from app.parsers.pdf import parse_transaction_pdf_bytes
from app.parsers.portfolio import parse_portfolio_csv_bytes
from app.parsers.transactions import parse_transaction_csv_bytes
from app.schemas.uploads import ParsePreviewResponse, ParsePreviewWarning, UploadBatchResponse
from app.storage.router import get_storage_backend


def _file_extension(filename: str) -> str:
    return filename.rsplit(".", 1)[-1].lower() if "." in filename else ""


async def process_transaction_upload(files: list[UploadFile], notes: str | None, db: Session, settings: Settings) -> UploadBatchResponse:
    if not files:
        raise HTTPException(status_code=400, detail="At least one transaction file is required.")

    upload = Upload(
        id=str(uuid4()),
        upload_type="transactions",
        original_filename=files[0].filename or "transactions",
        file_count=len(files),
        status="processing",
    )
    db.add(upload)
    db.flush()

    ai_router = AIRouter(settings)
    storage = get_storage_backend(settings)
    parsed_rows = 0
    warning_count = 0
    error_count = 0

    for upload_file in files:
        filename = upload_file.filename or f"file-{uuid4()}"
        file_bytes = await upload_file.read()
        raw_file = storage.save_bytes(upload.id, filename, file_bytes)
        raw_file_row = RawFile(
            id=str(uuid4()),
            upload_id=upload.id,
            filename=filename,
            file_type=raw_file.file_type,
            storage_path=raw_file.storage_path,
        )
        db.add(raw_file_row)
        db.flush()

        try:
            extension = _file_extension(filename)
            if extension == "pdf":
                parsed = parse_transaction_pdf_bytes(filename, file_bytes, ai_router)
            elif extension in {"csv", "tsv", "txt"}:
                parsed = parse_transaction_csv_bytes(filename, file_bytes, ai_router)
            else:
                raise ValueError(f"Unsupported transaction file type: {extension or 'unknown'}")
        except Exception as exc:
            error_count += 1
            db.add(
                ParseWarning(
                    id=str(uuid4()),
                    upload_id=upload.id,
                    source_file_id=raw_file_row.id,
                    warning_type="unsupported_file",
                    warning_message=f"{filename}: {exc}",
                    raw_payload={"filename": filename},
                )
            )
            continue

        for record in parsed.transactions:
            parsed_rows += 1
            db.add(
                Transaction(
                    id=str(uuid4()),
                    upload_id=upload.id,
                    source_file_id=raw_file_row.id,
                    row_number=record.row_number,
                    date=record.date,
                    ticker=record.ticker,
                    security_name=record.security_name,
                    action_raw=record.action_raw,
                    action_normalized=record.action_normalized,
                    quantity=record.quantity,
                    price=record.price,
                    gross_amount=record.gross_amount,
                    fees=record.fees,
                    net_amount=record.net_amount,
                    currency=record.currency,
                    description=record.description,
                    confidence_score=record.confidence_score,
                    parse_warnings=record.parse_warnings,
                )
            )

        for warning in parsed.warnings:
            warning_count += 1
            db.add(
                ParseWarning(
                    id=str(uuid4()),
                    upload_id=upload.id,
                    source_file_id=raw_file_row.id,
                    row_number=warning.row_number,
                    warning_type=warning.warning_type,
                    warning_message=warning.warning_message,
                    raw_payload=warning.raw_payload,
                )
            )

    upload.status = "parsed" if error_count == 0 else "partial_success"
    upload.parsed_rows = parsed_rows
    upload.warning_count = warning_count
    upload.error_count = error_count
    db.commit()

    return UploadBatchResponse(
        upload_id=upload.id,
        upload_type=upload.upload_type,
        status=upload.status,
        file_count=upload.file_count,
        parsed_rows=upload.parsed_rows,
        warning_count=upload.warning_count,
        error_count=upload.error_count,
    )


async def process_portfolio_upload(files: list[UploadFile], notes: str | None, db: Session, settings: Settings) -> UploadBatchResponse:
    if not files:
        raise HTTPException(status_code=400, detail="At least one portfolio file is required.")

    upload = Upload(
        id=str(uuid4()),
        upload_type="portfolio",
        original_filename=files[0].filename or "portfolio",
        file_count=len(files),
        status="processing",
    )
    db.add(upload)
    db.flush()

    storage = get_storage_backend(settings)
    warning_count = 0

    for upload_file in files:
        filename = upload_file.filename or f"portfolio-{uuid4()}"
        file_bytes = await upload_file.read()
        stored = storage.save_bytes(upload.id, filename, file_bytes)
        raw_file = RawFile(
            id=str(uuid4()),
            upload_id=upload.id,
            filename=filename,
            file_type=stored.file_type,
            storage_path=stored.storage_path,
        )
        db.add(raw_file)
        db.flush()

        try:
            parsed = parse_portfolio_csv_bytes(filename, file_bytes)
        except Exception as exc:
            db.add(
                ParseWarning(
                    id=str(uuid4()),
                    upload_id=upload.id,
                    source_file_id=raw_file.id,
                    warning_type="unsupported_file",
                    warning_message=f"{filename}: {exc}",
                    raw_payload={"filename": filename},
                )
            )
            warning_count += 1
            continue

        for position in parsed.positions:
            db.add(
                CurrentPosition(
                    id=str(uuid4()),
                    upload_id=upload.id,
                    ticker=position.ticker,
                    security_name=position.security_name,
                    shares=position.shares,
                    average_cost=position.average_cost,
                    total_invested=position.total_invested,
                    current_value=position.current_value,
                    portfolio_weight=position.portfolio_weight,
                    sector=position.sector,
                    notes=position.notes,
                    source=position.source,
                )
            )
        for warning in parsed.warnings:
            warning_count += 1
            db.add(
                ParseWarning(
                    id=str(uuid4()),
                    upload_id=upload.id,
                    source_file_id=raw_file.id,
                    row_number=warning.row_number,
                    warning_type=warning.warning_type,
                    warning_message=warning.warning_message,
                    raw_payload=warning.raw_payload,
                )
            )

    upload.status = "parsed"
    upload.parsed_rows = db.query(CurrentPosition).filter(CurrentPosition.upload_id == upload.id).count()
    upload.warning_count = warning_count
    db.commit()

    return UploadBatchResponse(
        upload_id=upload.id,
        upload_type=upload.upload_type,
        status=upload.status,
        file_count=upload.file_count,
        parsed_rows=upload.parsed_rows,
        warning_count=upload.warning_count,
        error_count=upload.error_count,
    )


def build_parse_preview(upload_id: str, db: Session, settings: Settings) -> ParsePreviewResponse:
    upload = db.get(Upload, upload_id)
    if upload is None:
        raise HTTPException(status_code=404, detail="Upload not found.")

    raw_files = db.scalars(select(RawFile).where(RawFile.upload_id == upload_id)).all()
    transactions = db.scalars(select(Transaction).where(Transaction.upload_id == upload_id)).all()
    warnings = db.scalars(select(ParseWarning).where(ParseWarning.upload_id == upload_id)).all()
    integration_status = build_integration_status(settings)

    dates = sorted(transaction.date for transaction in transactions if transaction.date)
    return ParsePreviewResponse(
        upload_id=upload.id,
        detected_file_types=sorted({file.file_type for file in raw_files}),
        parsed_transaction_count=len(transactions),
        detected_date_range=(dates[0], dates[-1]) if dates else (None, None),
        detected_tickers=sorted({transaction.ticker for transaction in transactions if transaction.ticker}),
        detected_currencies=sorted({transaction.currency for transaction in transactions if transaction.currency}),
        detected_transaction_types=sorted({transaction.action_normalized for transaction in transactions if transaction.action_normalized}),
        warning_rows=[
            ParsePreviewWarning(
                source_file=next((file.filename for file in raw_files if file.id == warning.source_file_id), upload.original_filename),
                row_number=warning.row_number,
                warning_type=warning.warning_type,
                warning_message=warning.warning_message,
            )
            for warning in warnings
        ],
        unparsed_rows=[warning.raw_payload for warning in warnings if warning.warning_type == "unparsed_row"],
        missing_keys=[
            key
            for key, configured in {
                "GEMINI_API_KEY": integration_status.gemini_configured,
                "GROQ_API_KEY": integration_status.groq_configured,
                "ALPHA_VANTAGE_API_KEY": integration_status.alpha_vantage_configured,
                "FMP_API_KEY": integration_status.fmp_configured,
                "SEC_USER_AGENT": integration_status.sec_user_agent_configured,
            }.items()
            if not configured
        ],
        disabled_features=integration_status.unavailable_features,
    )
