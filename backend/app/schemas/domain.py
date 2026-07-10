from datetime import date as calendar_date

from pydantic import BaseModel, Field


class ParseIssue(BaseModel):
    source_file: str
    row_number: int | None = None
    warning_type: str
    warning_message: str
    raw_payload: dict = Field(default_factory=dict)


class NormalizedTransactionRecord(BaseModel):
    id: str | None = None
    upload_id: str | None = None
    source_file: str
    row_number: int
    date: calendar_date | None = None
    ticker: str | None = None
    security_name: str | None = None
    action_raw: str | None = None
    action_normalized: str = "unknown"
    quantity: float | None = None
    price: float | None = None
    gross_amount: float | None = None
    fees: float | None = None
    net_amount: float | None = None
    currency: str | None = None
    description: str | None = None
    confidence_score: float = 0.0
    parse_warnings: list[str] = Field(default_factory=list)
    raw_payload: dict = Field(default_factory=dict)


class PortfolioPositionRecord(BaseModel):
    ticker: str
    security_name: str | None = None
    shares: float | None = None
    average_cost: float | None = None
    total_invested: float | None = None
    current_value: float | None = None
    portfolio_weight: float | None = None
    sector: str | None = None
    notes: str | None = None
    source: str = "portfolio_upload"


class ParsedTransactionFile(BaseModel):
    source_file: str
    file_type: str
    detected_columns: dict[str, str | None] = Field(default_factory=dict)
    transactions: list[NormalizedTransactionRecord] = Field(default_factory=list)
    warnings: list[ParseIssue] = Field(default_factory=list)
    unparsed_rows: list[dict] = Field(default_factory=list)


class ParsedPortfolioFile(BaseModel):
    source_file: str
    detected_columns: dict[str, str | None] = Field(default_factory=dict)
    positions: list[PortfolioPositionRecord] = Field(default_factory=list)
    warnings: list[ParseIssue] = Field(default_factory=list)
