import pytest
from pydantic import ValidationError

from app.ai.schemas import ReportNarrativeResult, TransactionClassificationResult


def test_transaction_classification_schema_accepts_valid_payload() -> None:
    result = TransactionClassificationResult.model_validate(
        {
            "action_normalized": "buy",
            "confidence_score": 0.88,
            "rationale": "The description clearly indicates an entry trade.",
            "trade_tag": "accumulation"
        }
    )

    assert result.action_normalized == "buy"


def test_report_narrative_schema_rejects_invalid_confidence() -> None:
    with pytest.raises(ValidationError):
        TransactionClassificationResult.model_validate(
            {
                "action_normalized": "sell",
                "confidence_score": 1.4,
                "rationale": "Too high."
            }
        )

    narrative = ReportNarrativeResult.model_validate(
        {
            "trading_personality": "Conviction Accumulator",
            "summary": "Summary text",
            "main_strength": "Repeated focus",
            "main_weakness": "Fast turnover",
            "recurring_patterns": ["Repeated adds"],
            "review_checklist": ["Review quick exits"],
            "markdown": "# Report"
        }
    )
    assert narrative.trading_personality == "Conviction Accumulator"

