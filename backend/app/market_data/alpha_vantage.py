from datetime import date

import httpx

from app.core.config import Settings
from app.market_data.types import PricePoint


class AlphaVantageClient:
    def __init__(self, settings: Settings):
        self.settings = settings
        self.base_url = "https://www.alphavantage.co/query"

    def get_daily_adjusted(self, ticker: str) -> list[PricePoint]:
        if self.settings.alpha_vantage_api_key is None:
            return []

        params = {
            "function": "TIME_SERIES_DAILY_ADJUSTED",
            "symbol": ticker,
            "outputsize": "full",
            "apikey": self.settings.alpha_vantage_api_key.get_secret_value(),
        }
        with httpx.Client(timeout=self.settings.request_timeout_seconds) as client:
            response = client.get(self.base_url, params=params)
            response.raise_for_status()
            payload = response.json()

        series = payload.get("Time Series (Daily)", {})
        results: list[PricePoint] = []
        for day, values in series.items():
            adjusted_close = values.get("5. adjusted close") or values.get("4. close")
            if adjusted_close is None:
                continue
            results.append(PricePoint(trade_date=date.fromisoformat(day), adjusted_close=float(adjusted_close)))
        return sorted(results, key=lambda item: item.trade_date)

