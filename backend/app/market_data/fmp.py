from datetime import date

import httpx

from app.core.config import Settings
from app.market_data.types import PricePoint


class FMPClient:
    def __init__(self, settings: Settings):
        self.settings = settings
        self.base_url = "https://financialmodelingprep.com/stable/historical-price-eod/light"

    def get_daily_history(self, ticker: str) -> list[PricePoint]:
        if self.settings.fmp_api_key is None:
            return []

        params = {"symbol": ticker, "apikey": self.settings.fmp_api_key.get_secret_value()}
        with httpx.Client(timeout=self.settings.request_timeout_seconds) as client:
            response = client.get(self.base_url, params=params)
            response.raise_for_status()
            payload = response.json()

        history = payload if isinstance(payload, list) else payload.get("historical", [])
        results: list[PricePoint] = []
        for item in history:
            day = item.get("date")
            close = item.get("close") or item.get("adjClose")
            if day is None or close is None:
                continue
            results.append(PricePoint(trade_date=date.fromisoformat(day), adjusted_close=float(close)))
        return sorted(results, key=lambda item: item.trade_date)

