from functools import lru_cache

from app.ai.providers.gemini_client import GeminiClient
from app.ai.providers.groq_client import GroqClient
from app.ai.schemas import ReportNarrativeInput, ReportNarrativeResult, ThemeClassificationResult, TransactionClassificationInput, TransactionClassificationResult
from app.core.config import Settings


class AIRouter:
    def __init__(self, settings: Settings):
        self.settings = settings
        self.groq_client = GroqClient(settings)
        self.gemini_client = GeminiClient(settings)

    def classify_transaction(self, tx_input: TransactionClassificationInput) -> TransactionClassificationResult | None:
        if self.settings.groq_api_key is None:
            return None
        try:
            return self.groq_client.classify_transaction(tx_input)
        except Exception:
            return None

    @lru_cache(maxsize=256)
    def classify_ticker_theme(self, ticker: str, security_name: str | None) -> ThemeClassificationResult | None:
        if self.settings.groq_api_key is None:
            return None
        try:
            return self.groq_client.classify_theme(ticker, security_name)
        except Exception:
            return None

    def generate_behavior_report(self, narrative_input: ReportNarrativeInput) -> ReportNarrativeResult | None:
        if self.settings.gemini_api_key is None:
            return None
        try:
            return self.gemini_client.generate_report_narrative(narrative_input)
        except Exception:
            return None

