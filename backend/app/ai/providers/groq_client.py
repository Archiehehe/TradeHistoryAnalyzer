import json

import httpx

from app.ai.schemas import ThemeClassificationResult, TransactionClassificationInput, TransactionClassificationResult
from app.core.config import Settings


class GroqClient:
    def __init__(self, settings: Settings):
        self.settings = settings
        self.base_url = "https://api.groq.com/openai/v1/chat/completions"

    def _request_json(self, system_prompt: str, user_payload: dict) -> dict | None:
        if self.settings.groq_api_key is None:
            return None

        payload = {
            "model": "llama-3.3-70b-versatile",
            "temperature": 0.1,
            "messages": [
                {"role": "system", "content": system_prompt},
                {"role": "user", "content": json.dumps(user_payload)},
            ],
        }
        headers = {
            "Authorization": f"Bearer {self.settings.groq_api_key.get_secret_value()}",
            "Content-Type": "application/json",
        }

        with httpx.Client(timeout=self.settings.request_timeout_seconds) as client:
            response = client.post(self.base_url, headers=headers, json=payload)
            response.raise_for_status()
            body = response.json()
        text = body["choices"][0]["message"]["content"]
        try:
            return json.loads(text)
        except json.JSONDecodeError:
            return None

    def classify_transaction(self, tx_input: TransactionClassificationInput) -> TransactionClassificationResult | None:
        result = self._request_json(
            "Classify the transaction into one supported normalized action and return strict JSON with action_normalized, confidence_score, rationale, trade_tag.",
            tx_input.model_dump(mode="json"),
        )
        if result is None:
            return None
        return TransactionClassificationResult.model_validate(result)

    def classify_theme(self, ticker: str, security_name: str | None) -> ThemeClassificationResult | None:
        result = self._request_json(
            "Classify the ticker into a single primary investing theme and return strict JSON with primary_theme, secondary_themes, confidence_score, rationale.",
            {"ticker": ticker, "security_name": security_name},
        )
        if result is None:
            return None
        return ThemeClassificationResult.model_validate(result)

