from io import BytesIO

import pandas as pd

from app.parsers.column_mapping import PORTFOLIO_ALIASES, detect_column_mapping
from app.parsers.common import normalize_ticker, parse_numeric_value
from app.schemas.domain import ParseIssue, ParsedPortfolioFile, PortfolioPositionRecord


def parse_portfolio_csv_bytes(filename: str, file_bytes: bytes) -> ParsedPortfolioFile:
    last_error: Exception | None = None
    dataframe = None
    for encoding in ("utf-8-sig", "utf-8", "latin-1"):
        try:
            dataframe = pd.read_csv(BytesIO(file_bytes), encoding=encoding, sep=None, engine="python")
            break
        except Exception as exc:  # pragma: no cover - fallback path.
            last_error = exc
    if dataframe is None:
        raise ValueError(f"Unable to read uploaded portfolio file: {last_error}") from last_error
    dataframe = dataframe.fillna(value=pd.NA)
    mapping = detect_column_mapping(dataframe.columns, PORTFOLIO_ALIASES)

    positions: list[PortfolioPositionRecord] = []
    warnings: list[ParseIssue] = []

    for row_number, (_, row) in enumerate(dataframe.iterrows(), start=2):
        raw_row = {str(key): (None if pd.isna(value) else value) for key, value in row.to_dict().items()}
        ticker = normalize_ticker(raw_row.get(mapping.get("ticker"))) if mapping.get("ticker") else None
        if ticker is None:
            warnings.append(
                ParseIssue(
                    source_file=filename,
                    row_number=row_number,
                    warning_type="missing_ticker",
                    warning_message="Portfolio row skipped because no ticker could be detected.",
                    raw_payload=raw_row,
                )
            )
            continue

        position = PortfolioPositionRecord(
            ticker=ticker,
            security_name=str(raw_row.get(mapping.get("security_name"))).strip() if mapping.get("security_name") and raw_row.get(mapping.get("security_name")) not in {None, ""} else None,
            shares=parse_numeric_value(raw_row.get(mapping.get("shares"))) if mapping.get("shares") else None,
            average_cost=parse_numeric_value(raw_row.get(mapping.get("average_cost"))) if mapping.get("average_cost") else None,
            total_invested=parse_numeric_value(raw_row.get(mapping.get("total_invested"))) if mapping.get("total_invested") else None,
            current_value=parse_numeric_value(raw_row.get(mapping.get("current_value"))) if mapping.get("current_value") else None,
            portfolio_weight=parse_numeric_value(raw_row.get(mapping.get("portfolio_weight"))) if mapping.get("portfolio_weight") else None,
            sector=str(raw_row.get(mapping.get("sector"))).strip() if mapping.get("sector") and raw_row.get(mapping.get("sector")) not in {None, ""} else None,
            notes=str(raw_row.get(mapping.get("notes"))).strip() if mapping.get("notes") and raw_row.get(mapping.get("notes")) not in {None, ""} else None,
        )
        positions.append(position)

    return ParsedPortfolioFile(source_file=filename, detected_columns=mapping, positions=positions, warnings=warnings)
