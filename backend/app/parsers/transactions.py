from typing import Any

import pandas as pd

from app.ai.router import AIRouter
from app.ai.schemas import TransactionClassificationInput
from app.parsers.column_mapping import FIELD_ALIASES, detect_column_mapping
from app.parsers.common import is_meaningful_payload, normalize_action, normalize_currency, normalize_ticker, parse_date_value, parse_numeric_value, read_tabular_dataframe
from app.schemas.domain import NormalizedTransactionRecord, ParseIssue, ParsedTransactionFile


def normalize_transaction_row(
    row: dict[str, Any],
    mapping: dict[str, str | None],
    row_number: int,
    source_file: str,
    ai_router: AIRouter | None = None,
) -> tuple[NormalizedTransactionRecord | None, list[ParseIssue], dict | None]:
    warnings: list[ParseIssue] = []
    date_value = parse_date_value(row.get(mapping.get("date"))) if mapping.get("date") else None
    quantity = parse_numeric_value(row.get(mapping.get("quantity"))) if mapping.get("quantity") else None
    price = parse_numeric_value(row.get(mapping.get("price"))) if mapping.get("price") else None
    amount = parse_numeric_value(row.get(mapping.get("amount"))) if mapping.get("amount") else None
    fees = parse_numeric_value(row.get(mapping.get("fees"))) if mapping.get("fees") else None
    action_raw = row.get(mapping.get("action")) if mapping.get("action") else None
    description = row.get(mapping.get("security_name")) if mapping.get("security_name") else None
    ticker = normalize_ticker(row.get(mapping.get("ticker"))) if mapping.get("ticker") else None
    currency = normalize_currency(row.get(mapping.get("currency"))) if mapping.get("currency") else None
    security_name = str(description).strip() if description not in {None, ""} else None
    action_normalized, action_confidence = normalize_action(action_raw, description, quantity, amount)

    if action_normalized == "unknown" and ai_router is not None:
        ai_result = ai_router.classify_transaction(
            TransactionClassificationInput(
                source_file=source_file,
                row_number=row_number,
                action_raw=str(action_raw or ""),
                description=str(description or ""),
                ticker=ticker,
                quantity=quantity,
                amount=amount,
            )
        )
        if ai_result is not None:
            action_normalized = ai_result.action_normalized
            action_confidence = max(action_confidence, ai_result.confidence_score)

    gross_amount = amount
    if gross_amount is None and quantity is not None and price is not None:
        gross_amount = round(quantity * price, 4)

    net_amount = amount
    if net_amount is None and gross_amount is not None:
        net_amount = gross_amount
        if fees is not None and action_normalized in {"buy", "fee", "withdrawal"}:
            net_amount = gross_amount + fees

    payload = {
        "date": row.get(mapping.get("date")) if mapping.get("date") else None,
        "ticker": row.get(mapping.get("ticker")) if mapping.get("ticker") else None,
        "action": row.get(mapping.get("action")) if mapping.get("action") else None,
        "description": row.get(mapping.get("security_name")) if mapping.get("security_name") else None,
        "quantity": row.get(mapping.get("quantity")) if mapping.get("quantity") else None,
        "price": row.get(mapping.get("price")) if mapping.get("price") else None,
        "amount": row.get(mapping.get("amount")) if mapping.get("amount") else None,
        "fees": row.get(mapping.get("fees")) if mapping.get("fees") else None,
        "currency": row.get(mapping.get("currency")) if mapping.get("currency") else None,
        "raw_row": row,
    }

    if not is_meaningful_payload(date_value, ticker, action_raw, description, quantity, amount):
        warning = ParseIssue(
            source_file=source_file,
            row_number=row_number,
            warning_type="unparsed_row",
            warning_message="Row did not contain enough structured data to normalize.",
            raw_payload=payload,
        )
        return None, [warning], payload

    if date_value is None:
        warnings.append(
            ParseIssue(
                source_file=source_file,
                row_number=row_number,
                warning_type="missing_date",
                warning_message="The row could not be assigned a trade date.",
                raw_payload=payload,
            )
        )

    if ticker is None:
        warnings.append(
            ParseIssue(
                source_file=source_file,
                row_number=row_number,
                warning_type="missing_ticker",
                warning_message="The row could not be linked to a ticker symbol.",
                raw_payload=payload,
            )
        )

    if action_normalized == "unknown":
        warnings.append(
            ParseIssue(
                source_file=source_file,
                row_number=row_number,
                warning_type="unknown_action",
                warning_message="The row could not be confidently mapped to a supported transaction type.",
                raw_payload=payload,
            )
        )

    confidence_score = 0.18
    if date_value is not None:
        confidence_score += 0.22
    if ticker is not None:
        confidence_score += 0.18
    if quantity is not None:
        confidence_score += 0.12
    if price is not None or gross_amount is not None:
        confidence_score += 0.12
    confidence_score += action_confidence * 0.28
    if warnings:
        confidence_score -= min(0.2, 0.05 * len(warnings))

    record = NormalizedTransactionRecord(
        source_file=source_file,
        row_number=row_number,
        date=date_value,
        ticker=ticker,
        security_name=security_name,
        action_raw=str(action_raw).strip() if action_raw not in {None, ""} else None,
        action_normalized=action_normalized,
        quantity=quantity,
        price=price,
        gross_amount=gross_amount,
        fees=fees,
        net_amount=net_amount,
        currency=currency,
        description=str(description).strip() if description not in {None, ""} else None,
        confidence_score=max(0.01, min(0.99, round(confidence_score, 4))),
        parse_warnings=[warning.warning_message for warning in warnings],
        raw_payload=row,
    )
    return record, warnings, None


def parse_transaction_dataframe(
    dataframe: pd.DataFrame,
    source_file: str,
    file_type: str,
    ai_router: AIRouter | None = None,
) -> ParsedTransactionFile:
    dataframe = dataframe.fillna(value=pd.NA)
    mapping = detect_column_mapping(dataframe.columns, FIELD_ALIASES)

    parsed_rows: list[NormalizedTransactionRecord] = []
    warnings: list[ParseIssue] = []
    unparsed_rows: list[dict] = []

    for row_number, (_, row) in enumerate(dataframe.iterrows(), start=2):
        raw_row = {str(key): (None if pd.isna(value) else value) for key, value in row.to_dict().items()}
        record, row_warnings, unparsed_payload = normalize_transaction_row(raw_row, mapping, row_number, source_file, ai_router)
        warnings.extend(row_warnings)
        if record is not None:
            parsed_rows.append(record)
        if unparsed_payload is not None:
            unparsed_rows.append(unparsed_payload)

    return ParsedTransactionFile(
        source_file=source_file,
        file_type=file_type,
        detected_columns=mapping,
        transactions=parsed_rows,
        warnings=warnings,
        unparsed_rows=unparsed_rows,
    )


def parse_transaction_tabular_bytes(filename: str, file_bytes: bytes, ai_router: AIRouter | None = None) -> ParsedTransactionFile:
    dataframe = read_tabular_dataframe(filename, file_bytes)
    file_type = filename.rsplit(".", 1)[-1].lower() if "." in filename else "csv"
    return parse_transaction_dataframe(dataframe, filename, file_type, ai_router)


def parse_transaction_csv_bytes(filename: str, file_bytes: bytes, ai_router: AIRouter | None = None) -> ParsedTransactionFile:
    return parse_transaction_tabular_bytes(filename, file_bytes, ai_router)
