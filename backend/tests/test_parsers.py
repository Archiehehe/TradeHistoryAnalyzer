from pathlib import Path

from app.parsers.column_mapping import detect_column_mapping
from app.parsers.common import normalize_action, parse_date_value
from app.parsers.portfolio import parse_portfolio_csv_bytes
from app.parsers.transactions import parse_transaction_csv_bytes


FIXTURES = Path(__file__).parent / "fixtures"


def test_column_detection_matches_common_variants() -> None:
    mapping = detect_column_mapping(["Trade Date", "Symbol", "Description", "Shares", "Execution Price", "Net Amount", "Commission", "Currency"])

    assert mapping["date"] == "Trade Date"
    assert mapping["ticker"] == "Symbol"
    assert mapping["price"] == "Execution Price"


def test_date_parsing_handles_excel_serials_and_strings() -> None:
    assert parse_date_value("2024-03-20").isoformat() == "2024-03-20"
    assert parse_date_value(45275).year == 2023


def test_action_normalization_covers_buy_sell_dividend_and_fee() -> None:
    assert normalize_action("Buy", "NVIDIA Corporation", 10, -500)[0] == "buy"
    assert normalize_action("Sell", "NVIDIA Corporation", 10, 500)[0] == "sell"
    assert normalize_action("Dividend", "Cash dividend", None, 15)[0] == "dividend"
    assert normalize_action("Fee", "Monthly account fee", None, -10)[0] == "fee"


def test_unknown_rows_are_retained_in_parse_preview() -> None:
    payload = (FIXTURES / "sample_transactions.csv").read_bytes()
    parsed = parse_transaction_csv_bytes("sample_transactions.csv", payload)

    assert len(parsed.transactions) == 4
    assert parsed.unparsed_rows
    assert any(warning.warning_type == "unparsed_row" for warning in parsed.warnings)


def test_seeking_alpha_portfolio_parser_reads_core_fields() -> None:
    payload = (FIXTURES / "sample_portfolio.csv").read_bytes()
    parsed = parse_portfolio_csv_bytes("sample_portfolio.csv", payload)

    assert len(parsed.positions) == 2
    assert parsed.positions[0].ticker == "NVDA"
    assert parsed.positions[0].portfolio_weight == 20
