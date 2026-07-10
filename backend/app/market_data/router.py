from bisect import bisect_left
from collections.abc import Sequence
from datetime import date, timedelta
from functools import lru_cache

from app.core.config import Settings
from app.market_data.alpha_vantage import AlphaVantageClient
from app.market_data.fmp import FMPClient
from app.market_data.types import PricePoint, TradeTimingContext


class MarketDataRouter:
    def __init__(self, settings: Settings):
        self.settings = settings
        self.alpha = AlphaVantageClient(settings)
        self.fmp = FMPClient(settings)

    @lru_cache(maxsize=128)
    def get_price_series(self, ticker: str) -> tuple[PricePoint, ...]:
        try:
            alpha_series = self.alpha.get_daily_adjusted(ticker)
        except Exception:
            alpha_series = []
        if alpha_series:
            return tuple(alpha_series)

        try:
            return tuple(self.fmp.get_daily_history(ticker))
        except Exception:
            return tuple()

    def build_timing_context(self, ticker: str, trade_date: date) -> TradeTimingContext | None:
        if self.settings.alpha_vantage_api_key is None and self.settings.fmp_api_key is None:
            return None

        series = self.get_price_series(ticker)
        if not series:
            return None

        return TradeTimingContext(
            price_30_days_before=self._nearest(series, trade_date - timedelta(days=30)),
            price_on_trade_date=self._nearest(series, trade_date),
            price_30_days_after=self._nearest(series, trade_date + timedelta(days=30)),
            price_90_days_after=self._nearest(series, trade_date + timedelta(days=90)),
            context_note="Timing context is based on nearest available trading days and is not a recommendation.",
        )

    @staticmethod
    def _nearest(series: Sequence[PricePoint], target: date) -> float | None:
        dates = [point.trade_date for point in series]
        index = bisect_left(dates, target)
        candidates: list[PricePoint] = []
        if index < len(series):
            candidates.append(series[index])
        if index > 0:
            candidates.append(series[index - 1])
        if not candidates:
            return None
        nearest = min(candidates, key=lambda point: abs((point.trade_date - target).days))
        return nearest.adjusted_close

