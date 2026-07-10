from datetime import date
from uuid import UUID

from pydantic import BaseModel, Field


class UploadRequestMetadata(BaseModel):
    notes: str | None = None


class UploadBatchResponse(BaseModel):
    upload_id: UUID
    upload_type: str
    status: str
    file_count: int
    parsed_rows: int = 0
    warning_count: int = 0
    error_count: int = 0


class ParsePreviewWarning(BaseModel):
    source_file: str
    row_number: int | None = None
    warning_type: str
    warning_message: str


class ParsePreviewResponse(BaseModel):
    upload_id: UUID
    detected_file_types: list[str] = Field(default_factory=list)
    parsed_transaction_count: int = 0
    detected_date_range: tuple[date | None, date | None] = (None, None)
    detected_tickers: list[str] = Field(default_factory=list)
    detected_currencies: list[str] = Field(default_factory=list)
    detected_transaction_types: list[str] = Field(default_factory=list)
    warning_rows: list[ParsePreviewWarning] = Field(default_factory=list)
    unparsed_rows: list[dict] = Field(default_factory=list)
    missing_keys: list[str] = Field(default_factory=list)
    disabled_features: list[str] = Field(default_factory=list)

