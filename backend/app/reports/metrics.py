from collections import Counter, defaultdict, deque
from dataclasses import dataclass
from datetime import date
from statistics import median

from app.market_data.router import MarketDataRouter
from app.models.entities import CurrentPosition, ParseWarning, Transaction
from app.reports.theme_rules import classify_theme_from_rules


@dataclass(slots=True)
class ReportMetricsBundle:
    summary: dict
    metric_cards: list[dict]
    capital_flow: list[dict]
    theme_drift: dict
    trade_review_list: list[dict]
    ticker_details: dict
    realized_events: dict[str, list[dict]]
    data_quality: dict


def _trade_amount(transaction: Transaction) -> float:
    if transaction.net_amount is not None:
        return abs(transaction.net_amount)
    if transaction.gross_amount is not None:
        return abs(transaction.gross_amount)
    if transaction.price is not None and transaction.quantity is not None:
        return abs(transaction.price * transaction.quantity)
    return 0.0


def _capital_impact(transaction: Transaction) -> float:
    amount = _trade_amount(transaction)
    if transaction.action_normalized == "buy":
        return -amount
    if transaction.action_normalized == "sell":
        return amount
    if transaction.action_normalized in {"deposit", "dividend", "interest"}:
        return amount
    if transaction.action_normalized in {"withdrawal", "fee"}:
        return -amount
    return 0.0


def compute_report_metrics(
    transactions: list[Transaction],
    positions: list[CurrentPosition],
    parse_warnings: list[ParseWarning],
    market_data: MarketDataRouter | None = None,
) -> ReportMetricsBundle:
    ordered = sorted([transaction for transaction in transactions if transaction.date], key=lambda item: item.date or date.min)
    trade_transactions = [transaction for transaction in ordered if transaction.action_normalized in {"buy", "sell"}]
    trade_count = len(trade_transactions)

    months = Counter(transaction.date.strftime("%Y-%m") for transaction in trade_transactions if transaction.date)
    active_months = len(months)
    average_trades_per_active_month = trade_count / active_months if active_months else 0.0

    capital_by_ticker = defaultdict(float)
    entries_by_ticker = Counter()
    exits_by_ticker = Counter()
    themes_by_month = defaultdict(Counter)
    theme_totals = Counter()
    one_off_tickers = set()
    accumulated_tickers = set()
    timeline_by_ticker = defaultdict(list)
    realized_events = defaultdict(list)
    large_trade_threshold = 0.0

    trade_sizes = [_trade_amount(transaction) for transaction in trade_transactions]
    if trade_sizes:
        sorted_sizes = sorted(trade_sizes)
        large_trade_threshold = sorted_sizes[max(0, int(len(sorted_sizes) * 0.9) - 1)]

    lots_by_ticker: dict[str, deque[dict]] = defaultdict(deque)
    holding_periods: list[int] = []
    quick_exits = 0
    long_holds = 0
    full_exits = 0
    partial_exits = 0

    for transaction in ordered:
        ticker = transaction.ticker or "UNKNOWN"
        timeline_by_ticker[ticker].append(transaction)
        amount = _trade_amount(transaction)
        capital_by_ticker[ticker] += amount if transaction.action_normalized == "buy" else 0.0

        theme, _, _ = classify_theme_from_rules(transaction.ticker, transaction.security_name)
        if transaction.date:
            month_key = transaction.date.strftime("%Y-%m")
            themes_by_month[month_key][theme] += 1
            theme_totals[theme] += 1

        if transaction.action_normalized == "buy":
            entries_by_ticker[ticker] += 1
            accumulated_tickers.add(ticker) if entries_by_ticker[ticker] >= 2 else None
            lots_by_ticker[ticker].append(
                {
                    "quantity": transaction.quantity or 0.0,
                    "date": transaction.date,
                    "price": transaction.price,
                }
            )
        elif transaction.action_normalized == "sell":
            exits_by_ticker[ticker] += 1
            remaining = transaction.quantity or 0.0
            matched = 0.0
            while remaining > 0 and lots_by_ticker[ticker]:
                lot = lots_by_ticker[ticker][0]
                available = lot["quantity"] or 0.0
                if available <= 0:
                    lots_by_ticker[ticker].popleft()
                    continue
                matched_quantity = min(available, remaining)
                lot["quantity"] = available - matched_quantity
                remaining -= matched_quantity
                matched += matched_quantity
                if transaction.date and lot["date"]:
                    holding_days = (transaction.date - lot["date"]).days
                    holding_periods.append(holding_days)
                    if holding_days < 30:
                        quick_exits += 1
                    if holding_days > 180:
                        long_holds += 1
                    realized_events[ticker].append(
                        {
                            "entry_date": lot["date"].isoformat(),
                            "exit_date": transaction.date.isoformat(),
                            "quantity": matched_quantity,
                            "holding_days": holding_days,
                            "entry_price": lot["price"],
                            "exit_price": transaction.price,
                        }
                    )
                if lot["quantity"] <= 0:
                    lots_by_ticker[ticker].popleft()

            if matched and not lots_by_ticker[ticker]:
                full_exits += 1
            elif matched:
                partial_exits += 1

    for ticker, count in entries_by_ticker.items():
        if count == 1 and exits_by_ticker[ticker] <= 1:
            one_off_tickers.add(ticker)

    total_capital = sum(capital_by_ticker.values()) or 1.0
    capital_concentration = sum((value / total_capital) ** 2 for value in capital_by_ticker.values())
    one_off_ratio = len(one_off_tickers) / max(1, len(entries_by_ticker))
    accumulation_ratio = len(accumulated_tickers) / max(1, len(entries_by_ticker))
    rotation_events = 0
    cross_theme_rotations = 0

    for index, transaction in enumerate(ordered):
        if transaction.action_normalized != "sell" or not transaction.date:
            continue
        for candidate in ordered[index + 1 : index + 6]:
            if not candidate.date or (candidate.date - transaction.date).days > 7:
                break
            if candidate.action_normalized != "buy":
                continue
            rotation_events += 1
            sale_theme, _, _ = classify_theme_from_rules(transaction.ticker, transaction.security_name)
            entry_theme, _, _ = classify_theme_from_rules(candidate.ticker, candidate.security_name)
            if sale_theme != entry_theme:
                cross_theme_rotations += 1
            break

    overtrading_score = max(0.0, min(100.0, 100 - (average_trades_per_active_month * 8) - (one_off_ratio * 20)))
    conviction_score = max(0.0, min(100.0, 45 + (accumulation_ratio * 35) + ((1 - one_off_ratio) * 20)))
    rotation_score = max(0.0, min(100.0, 80 - (rotation_events * 4) - (cross_theme_rotations * 3)))
    concentration_score = max(0.0, min(100.0, 100 - (capital_concentration * 100)))
    consistency_score = max(0.0, min(100.0, 35 + (accumulation_ratio * 35) + ((1 - max(one_off_ratio, 0.1)) * 30)))

    timing_samples = []
    if market_data is not None:
        for transaction in trade_transactions:
            if not transaction.date or not transaction.ticker:
                continue
            context = market_data.build_timing_context(transaction.ticker, transaction.date)
            if context is None or context.price_on_trade_date is None:
                continue
            price_then = context.price_on_trade_date
            price_after = context.price_30_days_after
            if price_after is None or price_then == 0:
                continue
            move = ((price_after - price_then) / price_then) * 100
            timing_samples.append(move if transaction.action_normalized == "buy" else -move)
    timing_score = 50.0
    timing_explanation = "Price-based timing was not calculated because market data is unavailable."
    if timing_samples:
        average_timing = sum(timing_samples) / len(timing_samples)
        timing_score = max(0.0, min(100.0, 50 + average_timing))
        timing_explanation = "Timing context reflects 30-day follow-through after each entry or exit activity."

    metric_cards = [
        {
            "name": "Overtrading Score",
            "score": round(overtrading_score, 2),
            "explanation": f"Based on {trade_count} trade rows across {active_months or 0} active months, with {average_trades_per_active_month:.1f} trades per active month.",
            "payload": {
                "total_trades": trade_count,
                "active_months": active_months,
                "average_trades_per_active_month": round(average_trades_per_active_month, 2),
                "busiest_month": months.most_common(1)[0][0] if months else None,
                "quietest_month": min(months, key=months.get) if months else None,
            },
        },
        {
            "name": "Conviction Score",
            "score": round(conviction_score, 2),
            "explanation": f"Repeated entries appeared in {len(accumulated_tickers)} tickers, while {len(one_off_tickers)} tickers were touched only once.",
            "payload": {
                "repeated_entry_tickers": sorted(accumulated_tickers),
                "one_off_tickers": sorted(one_off_tickers),
            },
        },
        {
            "name": "Timing Score",
            "score": round(timing_score, 2),
            "explanation": timing_explanation,
            "payload": {"samples_used": len(timing_samples)},
        },
        {
            "name": "Rotation Score",
            "score": round(rotation_score, 2),
            "explanation": f"Detected {rotation_events} possible near-date rotations, including {cross_theme_rotations} moves across different themes.",
            "payload": {
                "rotation_events": rotation_events,
                "cross_theme_rotations": cross_theme_rotations,
            },
        },
        {
            "name": "Concentration Score",
            "score": round(concentration_score, 2),
            "explanation": "Capital concentration reflects how heavily your entry activity clustered into a small set of tickers.",
            "payload": {
                "top_allocations": sorted(
                    [{"ticker": ticker, "capital": round(value, 2)} for ticker, value in capital_by_ticker.items()],
                    key=lambda item: item["capital"],
                    reverse=True,
                )[:10],
            },
        },
        {
            "name": "Consistency Score",
            "score": round(consistency_score, 2),
            "explanation": "Consistency increases when activity repeats through familiar tickers and themes instead of scattering into one-off experiments.",
            "payload": {
                "accumulation_ratio": round(accumulation_ratio, 2),
                "one_off_ratio": round(one_off_ratio, 2),
            },
        },
    ]

    monthly_flow = defaultdict(float)
    for transaction in ordered:
        if transaction.date:
            monthly_flow[transaction.date.strftime("%Y-%m")] += _capital_impact(transaction)

    capital_flow = [
        {
            "label": month,
            "value": round(value, 2),
            "detail": "Positive values indicate more exit-side capital than entry-side capital for the month.",
        }
        for month, value in sorted(monthly_flow.items())
    ]

    repeated_themes = [theme for theme, count in theme_totals.items() if count >= 3]
    abandoned_themes = []
    if len(themes_by_month) >= 2:
        months_sorted = sorted(themes_by_month)
        first_themes = set(themes_by_month[months_sorted[0]].keys())
        last_themes = set(themes_by_month[months_sorted[-1]].keys())
        abandoned_themes = sorted(first_themes - last_themes)

    theme_drift = {
        "themes_over_time": {month: dict(counter) for month, counter in sorted(themes_by_month.items())},
        "top_added_themes": [theme for theme, _ in theme_totals.most_common(5)],
        "top_abandoned_themes": abandoned_themes,
        "repeated_themes": repeated_themes,
        "theme_concentration": dict(theme_totals),
    }

    review_items = []
    for ticker, timeline in timeline_by_ticker.items():
        for transaction in timeline:
            amount = _trade_amount(transaction)
            if transaction.action_normalized == "buy" and entries_by_ticker[ticker] >= 3:
                review_items.append(
                    {
                        "ticker": ticker,
                        "trade_date": transaction.date,
                        "review_priority": "medium",
                        "behavioral_signal": "Repeated accumulation",
                        "notes": "This ticker shows repeated entry activity consistent with an accumulation pattern.",
                    }
                )
            if transaction.action_normalized == "sell":
                for event in realized_events[ticker]:
                    if transaction.date and event["exit_date"] == transaction.date.isoformat() and event["holding_days"] < 30:
                        review_items.append(
                            {
                                "ticker": ticker,
                                "trade_date": transaction.date,
                                "review_priority": "high",
                                "behavioral_signal": "Quick exit",
                                "notes": "This position moved from entry to exit quickly and is worth reviewing for impulse or risk-control behavior.",
                            }
                        )
                        break
            if large_trade_threshold and amount >= large_trade_threshold:
                review_items.append(
                    {
                        "ticker": ticker,
                        "trade_date": transaction.date,
                        "review_priority": "medium",
                        "behavioral_signal": "Large capital move",
                        "notes": "This row is unusually large compared with the rest of the dataset and may deserve a second look.",
                    }
                )

    ticker_details = {}
    position_lookup = {position.ticker: position for position in positions}
    for ticker, timeline in timeline_by_ticker.items():
        buys = [transaction for transaction in timeline if transaction.action_normalized == "buy" and transaction.date]
        sells = [transaction for transaction in timeline if transaction.action_normalized == "sell" and transaction.date]
        total_bought = sum(transaction.quantity or 0.0 for transaction in buys)
        total_sold = sum(transaction.quantity or 0.0 for transaction in sells)
        invested = sum(_capital_impact(transaction) for transaction in timeline)
        average_buy_price = None
        if total_bought:
            weighted_cost = sum((transaction.price or 0.0) * (transaction.quantity or 0.0) for transaction in buys)
            average_buy_price = weighted_cost / total_bought if weighted_cost else None
        theme, _, _ = classify_theme_from_rules(ticker, timeline[0].security_name if timeline else None)
        ticker_details[ticker] = {
            "first_buy_date": min((transaction.date for transaction in buys), default=None),
            "latest_buy_date": max((transaction.date for transaction in buys), default=None),
            "latest_sell_date": max((transaction.date for transaction in sells), default=None),
            "total_bought": round(total_bought, 4) if total_bought else None,
            "total_sold": round(total_sold, 4) if total_sold else None,
            "net_invested": round(invested, 2),
            "current_shares": position_lookup[ticker].shares if ticker in position_lookup else None,
            "average_buy_price": round(average_buy_price, 4) if average_buy_price is not None else None,
            "realized_events": realized_events[ticker],
            "behavioral_note": f"{ticker} most often mapped to the {theme} theme and is worth reviewing in the context of your broader rotation behavior.",
        }

    personality = "Experimental Basket Builder"
    if conviction_score >= 70 and overtrading_score >= 60:
        personality = "Conviction Accumulator"
    elif rotation_score < 45:
        personality = "Capital Rotator"
    elif overtrading_score < 40:
        personality = "Momentum Chaser"
    elif quick_exits > max(2, len(realized_events) // 2):
        personality = "Quick Cutter"

    overall_behavior_score = round(
        (overtrading_score + conviction_score + timing_score + rotation_score + concentration_score + consistency_score) / 6,
        2,
    )
    summary = {
        "trading_personality": personality,
        "overall_behavior_score": overall_behavior_score,
        "main_strength": (
            "Your activity often returns to prior tickers or themes, which suggests a repeatable framework rather than random drift."
            if conviction_score >= 60
            else "You spread attention across multiple ideas, which can surface patterns that deserve follow-up."
        ),
        "main_weakness": (
            "A high pace of trade activity suggests possible overtrading and makes it harder to separate process from noise."
            if overtrading_score < 50
            else "Capital dispersion across many small positions may dilute conviction and make review harder."
        ),
        "summary": (
            f"Your history shows {trade_count} trade rows across {active_months or 0} active months. "
            f"The strongest behavioral signal is {personality.lower()}, with {len(accumulated_tickers)} tickers showing repeat entries "
            f"and {quick_exits} quick exits worth reviewing. This output is educational and not a recommendation."
        ),
    }

    data_quality = {
        "parsed_rows": len(transactions),
        "warning_rows": len(parse_warnings),
        "unknown_rows": sum(1 for transaction in transactions if transaction.action_normalized == "unknown"),
        "unsupported_files": [warning.warning_message for warning in parse_warnings if warning.warning_type == "unsupported_file"],
    }

    return ReportMetricsBundle(
        summary=summary,
        metric_cards=metric_cards,
        capital_flow=capital_flow,
        theme_drift=theme_drift,
        trade_review_list=review_items[:50],
        ticker_details=ticker_details,
        realized_events=dict(realized_events),
        data_quality=data_quality,
    )

