from dataclasses import dataclass
from datetime import date


@dataclass(slots=True)
class PricePoint:
    trade_date: date
    adjusted_close: float


@dataclass(slots=True)
class TradeTimingContext:
    price_30_days_before: float | None
    price_on_trade_date: float | None
    price_30_days_after: float | None
    price_90_days_after: float | None
    context_note: str

