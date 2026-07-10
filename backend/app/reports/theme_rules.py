THEME_KEYWORDS: dict[str, tuple[str, ...]] = {
    "Semiconductors": ("NVDA", "AMD", "TSM", "MU", "AVGO", "ASML", "SOXX", "SMH"),
    "Artificial Intelligence": ("AI", "PLTR", "C3AI", "MSFT", "GOOGL", "QQQ"),
    "Cloud Software": ("CRM", "NOW", "ORCL", "ADBE", "WDAY"),
    "Electric Vehicles": ("TSLA", "RIVN", "LCID", "NIO"),
    "Biotech": ("XBI", "IBB", "MRNA", "VRTX", "REGN"),
    "Financials": ("JPM", "GS", "BAC", "XLF", "SCHW"),
    "Energy": ("XOM", "CVX", "OXY", "XLE"),
    "Crypto Exposure": ("COIN", "MSTR", "BITO", "IBIT"),
    "Broad Market ETF": ("SPY", "VOO", "VTI", "QQQ", "DIA", "IWM"),
    "Defensive": ("XLV", "XLP", "JNJ", "PG", "KO"),
    "Metals and Gold": ("GLD", "SLV", "NEM", "GDX"),
    "Real Estate": ("VNQ", "O", "PLD", "SPG"),
}

NAME_HINTS: dict[str, tuple[str, ...]] = {
    "Semiconductors": ("semiconductor", "chip", "foundry"),
    "Artificial Intelligence": ("artificial intelligence", "ai", "machine learning"),
    "Cloud Software": ("cloud", "software", "saas"),
    "Electric Vehicles": ("electric vehicle", "battery"),
    "Biotech": ("biotech", "pharma", "therapeutics"),
    "Financials": ("bank", "financial", "capital"),
    "Energy": ("energy", "oil", "gas"),
    "Crypto Exposure": ("bitcoin", "crypto", "blockchain"),
    "Broad Market ETF": ("s&p", "index", "etf"),
    "Defensive": ("consumer staples", "health care", "healthcare"),
    "Metals and Gold": ("gold", "silver", "miner"),
    "Real Estate": ("reit", "real estate", "property"),
}


def classify_theme_from_rules(ticker: str | None, security_name: str | None) -> tuple[str, list[str], float]:
    if ticker:
        for theme, tickers in THEME_KEYWORDS.items():
            if ticker.upper() in tickers:
                return theme, [], 0.9
    lowered_name = (security_name or "").lower()
    for theme, hints in NAME_HINTS.items():
        if any(hint in lowered_name for hint in hints):
            return theme, [], 0.7
    return "Unclassified", [], 0.2

