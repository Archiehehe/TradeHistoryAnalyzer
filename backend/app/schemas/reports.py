from datetime import date as calendar_date, datetime
from uuid import UUID

from pydantic import BaseModel, Field


class ReportGenerateRequest(BaseModel):
    upload_id: UUID
    portfolio_upload_id: UUID | None = None


class MetricCard(BaseModel):
    name: str
    score: float
    explanation: str
    payload: dict = Field(default_factory=dict)


class CapitalFlowItem(BaseModel):
    label: str
    value: float
    detail: str


class TradeReviewItem(BaseModel):
    ticker: str
    trade_date: calendar_date | None = None
    review_priority: str
    behavioral_signal: str
    notes: str


class DataQualitySection(BaseModel):
    parsed_rows: int
    warning_rows: int
    unknown_rows: int
    unsupported_files: list[str] = Field(default_factory=list)
    missing_keys: list[str] = Field(default_factory=list)
    disabled_features: list[str] = Field(default_factory=list)


class ReportSummary(BaseModel):
    trading_personality: str
    overall_behavior_score: float
    main_strength: str
    main_weakness: str
    summary: str


class ReportDetailResponse(BaseModel):
    report_id: UUID
    upload_id: UUID
    portfolio_upload_id: UUID | None = None
    generated_at: datetime
    title: str
    summary: ReportSummary
    metric_cards: list[MetricCard] = Field(default_factory=list)
    capital_flow: list[CapitalFlowItem] = Field(default_factory=list)
    theme_drift: dict = Field(default_factory=dict)
    trade_review_list: list[TradeReviewItem] = Field(default_factory=list)
    data_quality: DataQualitySection
    report_markdown: str
    ai_available: bool


class ReportGenerateResponse(BaseModel):
    report_id: UUID
    status: str
    ai_available: bool
    message: str


class ReportTransactionsResponse(BaseModel):
    report_id: UUID
    transactions: list[dict] = Field(default_factory=list)


class TickerTimelineEntry(BaseModel):
    date: calendar_date | None = None
    action_normalized: str
    quantity: float | None = None
    price: float | None = None
    net_amount: float | None = None
    description: str | None = None


class TickerReportResponse(BaseModel):
    report_id: UUID
    ticker: str
    first_buy_date: calendar_date | None = None
    latest_buy_date: calendar_date | None = None
    latest_sell_date: calendar_date | None = None
    total_bought: float | None = None
    total_sold: float | None = None
    net_invested: float | None = None
    current_shares: float | None = None
    average_buy_price: float | None = None
    realized_events: list[dict] = Field(default_factory=list)
    behavioral_note: str
    timeline: list[TickerTimelineEntry] = Field(default_factory=list)


class WarningListResponse(BaseModel):
    report_id: UUID
    warnings: list[dict] = Field(default_factory=list)
