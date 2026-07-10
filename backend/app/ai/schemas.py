from typing import Literal

from pydantic import BaseModel, Field


class TransactionClassificationInput(BaseModel):
    source_file: str
    row_number: int
    action_raw: str
    description: str
    ticker: str | None = None
    quantity: float | None = None
    amount: float | None = None


class TransactionClassificationResult(BaseModel):
    action_normalized: Literal["buy", "sell", "dividend", "dividend_tax", "deposit", "withdrawal", "interest", "fee", "split", "transfer", "unknown"]
    confidence_score: float = Field(ge=0.0, le=1.0)
    rationale: str
    trade_tag: str | None = None


class ThemeClassificationResult(BaseModel):
    primary_theme: str
    secondary_themes: list[str] = Field(default_factory=list)
    confidence_score: float = Field(ge=0.0, le=1.0)
    rationale: str


class ReportNarrativeInput(BaseModel):
    summary_payload: dict


class ReportNarrativeResult(BaseModel):
    trading_personality: str
    summary: str
    main_strength: str
    main_weakness: str
    recurring_patterns: list[str] = Field(default_factory=list)
    review_checklist: list[str] = Field(default_factory=list)
    markdown: str

