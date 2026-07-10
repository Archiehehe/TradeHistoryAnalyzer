from datetime import date, timedelta
import math
from io import BytesIO
from pathlib import Path
import re

import pandas as pd
from dateutil import parser as date_parser


def parse_date_value(value: object) -> date | None:
    if value is None:
        return None
    if isinstance(value, date):
        return value
    if isinstance(value, float) and math.isnan(value):
        return None
    if isinstance(value, (int, float)) and 20_000 <= float(value) <= 60_000:
        return date(1899, 12, 30) + timedelta(days=int(float(value)))

    text = str(value).strip()
    if not text or text.lower() in {"nan", "nat", "none"}:
        return None

    try:
        return date_parser.parse(text, fuzzy=True).date()
    except (OverflowError, TypeError, ValueError):
        return None


def parse_numeric_value(value: object) -> float | None:
    if value is None:
        return None
    if isinstance(value, (int, float)) and not isinstance(value, bool):
        if isinstance(value, float) and math.isnan(value):
            return None
        return float(value)

    text = str(value).strip()
    if not text or text.lower() in {"nan", "none", "--", "n/a"}:
        return None

    negative = False
    if text.startswith("(") and text.endswith(")"):
        negative = True
        text = text[1:-1]

    text = text.replace(",", "").replace("$", "").replace("₹", "").replace("€", "").replace("£", "")
    text = text.replace("%", "")
    text = re.sub(r"[A-Za-z]{3}$", "", text).strip()
    text = re.sub(r"[^0-9.\-+]", "", text)
    if not text or text in {"-", "+", ".", "-.", "+."}:
        return None

    try:
        number = float(text)
    except ValueError:
        return None
    return -number if negative else number


def normalize_ticker(value: object) -> str | None:
    if value is None:
        return None
    text = str(value).strip().upper()
    if not text or text in {"NAN", "NONE"}:
        return None
    text = re.sub(r"[^A-Z0-9.\-]", "", text)
    return text or None


def normalize_currency(value: object) -> str | None:
    if value is None:
        return None
    text = re.sub(r"[^A-Za-z]", "", str(value).strip()).upper()
    return text[:3] if text else None


def normalize_action(action_raw: object, description: object, quantity: float | None, amount: float | None) -> tuple[str, float]:
    combined = " ".join(str(part or "") for part in [action_raw, description]).lower()
    keyword_groups = [
        ("dividend_tax", ("withholding tax", "dividend tax", "tax withheld", "tax on dividend")),
        ("dividend", ("dividend", "distribution", "cash div", "reinvest dividend")),
        ("interest", ("interest", "yield")),
        ("fee", ("fee", "commission", "brokerage", "charge")),
        ("deposit", ("deposit", "contribution", "cash in", "transfer in", "wire in", "ach credit")),
        ("withdrawal", ("withdrawal", "cash out", "transfer out", "wire out", "ach debit", "disbursement")),
        ("split", ("split", "reverse split")),
        ("transfer", ("transfer", "journal")),
        ("buy", ("buy", "bought", "purchase", "reinvest")),
        ("sell", ("sell", "sold", "redemption", "liquidation")),
    ]

    for normalized, keywords in keyword_groups:
        if any(keyword in combined for keyword in keywords):
            return normalized, 0.92

    if quantity is not None and amount is not None:
        if quantity > 0 and amount < 0:
            return "buy", 0.62
        if quantity > 0 and amount > 0:
            return "sell", 0.62

    if quantity is not None and quantity < 0:
        return "sell", 0.58

    return "unknown", 0.25


def is_meaningful_payload(*values: object) -> bool:
    return any(value not in {None, "", "nan", "NaN"} for value in values)


def read_tabular_dataframe(filename: str, file_bytes: bytes) -> pd.DataFrame:
    extension = Path(filename).suffix.lower()
    if extension in {".xlsx", ".xlsm"}:
        try:
            return pd.read_excel(BytesIO(file_bytes), engine="openpyxl")
        except Exception as exc:  # pragma: no cover - surfaced through upload errors.
            raise ValueError(f"Unable to read uploaded Excel data: {exc}") from exc

    last_error: Exception | None = None
    for encoding in ("utf-8-sig", "utf-8", "latin-1"):
        try:
            return pd.read_csv(BytesIO(file_bytes), encoding=encoding, sep=None, engine="python")
        except Exception as exc:  # pragma: no cover - exercised through fallback cases.
            last_error = exc

    raise ValueError(f"Unable to read uploaded CSV data: {last_error}") from last_error
