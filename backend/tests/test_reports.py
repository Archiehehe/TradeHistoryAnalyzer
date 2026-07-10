from datetime import UTC, date, datetime

from app.models.entities import CurrentPosition, Transaction
from app.reports.generator import generate_rule_based_report


def build_transaction(**overrides) -> Transaction:
    defaults = {
        "id": "txn-1",
        "upload_id": "upload-1",
        "source_file_id": None,
        "row_number": 2,
        "date": date(2024, 1, 5),
        "ticker": "NVDA",
        "security_name": "NVIDIA Corporation",
        "action_raw": "Buy",
        "action_normalized": "buy",
        "quantity": 10.0,
        "price": 50.0,
        "gross_amount": -500.0,
        "fees": 1.0,
        "net_amount": -500.0,
        "currency": "USD",
        "description": "Entry activity",
        "confidence_score": 0.95,
        "parse_warnings": [],
        "created_at": datetime.now(UTC)
    }
    defaults.update(overrides)
    return Transaction(**defaults)


def test_rule_based_report_generation_works_without_ai_or_market_data() -> None:
    transactions = [
        build_transaction(),
        build_transaction(
            id="txn-2",
            row_number=3,
            date=date(2024, 2, 14),
            action_raw="Sell",
            action_normalized="sell",
            quantity=5.0,
            price=70.0,
            gross_amount=350.0,
            net_amount=350.0,
            description="Exit activity"
        )
    ]
    positions = [
        CurrentPosition(
            id="pos-1",
            upload_id="portfolio-1",
            ticker="NVDA",
            security_name="NVIDIA Corporation",
            shares=5.0,
            average_cost=55.0,
            total_invested=275.0,
            current_value=810.0,
            portfolio_weight=20.0,
            sector="Semiconductors",
            notes="core winner",
            source="portfolio_upload",
            created_at=datetime.now(UTC)
        )
    ]

    report = generate_rule_based_report(transactions, positions, [], ai_router=None, market_data=None)

    assert report["ai_available"] is False
    assert report["summary"]["trading_personality"]
    assert len(report["metric_cards"]) == 6
    assert "Not a recommendation." in report["report_markdown"]
