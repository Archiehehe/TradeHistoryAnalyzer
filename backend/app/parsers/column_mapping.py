import re
from collections.abc import Iterable

FIELD_ALIASES: dict[str, tuple[str, ...]] = {
    "date": ("date", "trade date", "transaction date", "settlement date", "activity date"),
    "ticker": ("symbol", "ticker", "security", "instrument", "stock", "asset"),
    "security_name": ("security name", "description", "instrument name", "company", "name"),
    "action": ("action", "type", "transaction type", "activity", "description", "details"),
    "quantity": ("quantity", "shares", "units", "qty"),
    "price": ("price", "avg price", "average price", "execution price", "fill price"),
    "amount": ("amount", "net amount", "value", "total", "gross amount", "proceeds", "cost"),
    "fees": ("fees", "commission", "charges", "brokerage"),
    "currency": ("currency", "fx", "settlement currency"),
}

PORTFOLIO_ALIASES: dict[str, tuple[str, ...]] = {
    "ticker": ("ticker", "symbol"),
    "shares": ("shares", "quantity", "units"),
    "average_cost": ("average cost", "avg cost", "cost basis"),
    "total_invested": ("total invested", "cost", "invested", "market value at cost"),
    "current_value": ("current value", "market value", "value"),
    "portfolio_weight": ("portfolio weight", "weight", "% portfolio", "allocation"),
    "sector": ("sector", "theme"),
    "notes": ("notes", "comment", "thesis"),
    "security_name": ("name", "security name", "company"),
}


def canonicalize_header(value: object) -> str:
    text = re.sub(r"[^a-z0-9]+", " ", str(value).strip().lower())
    return re.sub(r"\s+", " ", text).strip()


def score_header_match(header: str, alias: str) -> float:
    if header == alias:
        return 1.0
    if alias in header or header in alias:
        return 0.85
    header_tokens = set(header.split())
    alias_tokens = set(alias.split())
    if not header_tokens or not alias_tokens:
        return 0.0
    overlap = len(header_tokens & alias_tokens)
    if overlap == 0:
        return 0.0
    return overlap / max(len(header_tokens), len(alias_tokens))


def detect_column_mapping(columns: Iterable[object], alias_map: dict[str, tuple[str, ...]] = FIELD_ALIASES) -> dict[str, str | None]:
    indexed_columns = {str(column): canonicalize_header(column) for column in columns}
    mapping: dict[str, str | None] = {}
    used_columns: set[str] = set()

    for field_name, aliases in alias_map.items():
        best_column: str | None = None
        best_score = 0.0
        for original, canonical in indexed_columns.items():
            if original in used_columns:
                continue
            for alias in aliases:
                score = score_header_match(canonical, alias)
                if score > best_score:
                    best_score = score
                    best_column = original
        if best_score >= 0.5 and best_column is not None:
            mapping[field_name] = best_column
            used_columns.add(best_column)
        else:
            mapping[field_name] = None

    return mapping

