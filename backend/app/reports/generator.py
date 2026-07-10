from datetime import UTC, datetime

from app.ai.router import AIRouter
from app.ai.schemas import ReportNarrativeInput
from app.market_data.router import MarketDataRouter
from app.models.entities import CurrentPosition, ParseWarning, Transaction
from app.reports.metrics import ReportMetricsBundle, compute_report_metrics


def generate_rule_based_report(
    transactions: list[Transaction],
    positions: list[CurrentPosition],
    parse_warnings: list[ParseWarning],
    ai_router: AIRouter | None = None,
    market_data: MarketDataRouter | None = None,
) -> dict:
    metrics = compute_report_metrics(transactions, positions, parse_warnings, market_data)
    report_markdown = _build_rule_based_markdown(metrics)

    narrative = None
    if ai_router is not None:
        narrative = ai_router.generate_behavior_report(ReportNarrativeInput(summary_payload={"summary": metrics.summary, "metrics": metrics.metric_cards}))

    if narrative is not None:
        metrics.summary["trading_personality"] = narrative.trading_personality
        metrics.summary["summary"] = narrative.summary
        metrics.summary["main_strength"] = narrative.main_strength
        metrics.summary["main_weakness"] = narrative.main_weakness
        report_markdown = narrative.markdown

    data_quality = {
        **metrics.data_quality,
        "missing_keys": [],
        "disabled_features": [],
    }

    return {
        "generated_at": datetime.now(UTC).isoformat(),
        "title": f"TradeHistoryAnalyzer behavioral report - {metrics.summary['trading_personality']}",
        "summary": metrics.summary,
        "metric_cards": metrics.metric_cards,
        "capital_flow": metrics.capital_flow,
        "theme_drift": metrics.theme_drift,
        "trade_review_list": metrics.trade_review_list,
        "data_quality": data_quality,
        "ticker_details": metrics.ticker_details,
        "report_markdown": report_markdown,
        "ai_available": narrative is not None,
    }


def _build_rule_based_markdown(metrics: ReportMetricsBundle) -> str:
    lines = [
        f"# {metrics.summary['trading_personality']}",
        "",
        metrics.summary["summary"],
        "",
        "## Scorecards",
    ]
    for card in metrics.metric_cards:
        lines.append(f"- {card['name']}: {card['score']} - {card['explanation']}")
    lines.extend(
        [
            "",
            "## Review Priorities",
        ]
    )
    for item in metrics.trade_review_list[:10]:
        lines.append(f"- {item['ticker']} on {item['trade_date']}: {item['behavioral_signal']} - {item['notes']}")
    lines.extend(
        [
            "",
            "## Data Quality",
            f"- Parsed rows: {metrics.data_quality['parsed_rows']}",
            f"- Warning rows: {metrics.data_quality['warning_rows']}",
            f"- Unknown rows: {metrics.data_quality['unknown_rows']}",
            "",
            "Not a recommendation.",
        ]
    )
    return "\n".join(lines)

