import json

import httpx

from app.ai.schemas import ReportNarrativeInput, ReportNarrativeResult
from app.core.config import Settings


class GeminiClient:
    def __init__(self, settings: Settings):
        self.settings = settings
        self.base_url = "https://generativelanguage.googleapis.com/v1beta/interactions"

    def generate_report_narrative(self, narrative_input: ReportNarrativeInput) -> ReportNarrativeResult | None:
        if self.settings.gemini_api_key is None:
            return None

        payload = {
            "model": "gemini-3.5-flash",
            "system_instruction": (
                "Return strict JSON with trading_personality, summary, main_strength, main_weakness, "
                "recurring_patterns, review_checklist, and markdown. Avoid investment advice and use behavioral language."
            ),
            "input": json.dumps(narrative_input.model_dump(mode="json")),
            "generation_config": {"temperature": 0.2, "thinking_level": "low"},
        }
        headers = {
            "x-goog-api-key": self.settings.gemini_api_key.get_secret_value(),
            "Content-Type": "application/json",
        }

        with httpx.Client(timeout=self.settings.request_timeout_seconds) as client:
            response = client.post(self.base_url, headers=headers, json=payload)
            response.raise_for_status()
            body = response.json()

        output_text = body.get("output_text")
        if not output_text:
            steps = body.get("steps", [])
            text_parts = []
            for step in steps:
                for part in step.get("output", {}).get("content", []):
                    if isinstance(part, dict) and "text" in part:
                        text_parts.append(part["text"])
            output_text = "\n".join(text_parts).strip()
        if not output_text:
            return None

        try:
            parsed = json.loads(output_text)
        except json.JSONDecodeError:
            return None
        return ReportNarrativeResult.model_validate(parsed)

