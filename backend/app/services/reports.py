from datetime import datetime
from uuid import uuid4

from fastapi import HTTPException
from fastapi.encoders import jsonable_encoder
from sqlalchemy import select
from sqlalchemy.orm import Session

from app.ai.router import AIRouter
from app.core.config import Settings
from app.core.key_status import build_integration_status
from app.market_data.router import MarketDataRouter
from app.models.entities import AIReport, BehaviorMetric, CurrentPosition, ParseWarning, Transaction, Upload
from app.reports.generator import generate_rule_based_report
from app.schemas.reports import DataQualitySection, MetricCard, ReportDetailResponse, ReportGenerateRequest, ReportGenerateResponse, ReportSummary, ReportTransactionsResponse, TickerReportResponse, TickerTimelineEntry, TradeReviewItem, WarningListResponse


def generate_report(payload: ReportGenerateRequest, db: Session, settings: Settings) -> ReportGenerateResponse:
    upload = db.get(Upload, str(payload.upload_id))
    if upload is None:
        raise HTTPException(status_code=404, detail="Transaction upload not found.")

    transactions = db.scalars(select(Transaction).where(Transaction.upload_id == str(payload.upload_id))).all()
    parse_warnings = db.scalars(select(ParseWarning).where(ParseWarning.upload_id == str(payload.upload_id))).all()
    positions: list[CurrentPosition] = []
    if payload.portfolio_upload_id:
        positions = db.scalars(select(CurrentPosition).where(CurrentPosition.upload_id == str(payload.portfolio_upload_id))).all()

    ai_router = AIRouter(settings)
    market_data = MarketDataRouter(settings)
    report_payload = generate_rule_based_report(
        transactions=transactions,
        positions=positions,
        parse_warnings=parse_warnings,
        ai_router=ai_router,
        market_data=market_data,
    )
    integration_status = build_integration_status(settings)
    report_payload["data_quality"]["missing_keys"] = [
        key
        for key, configured in {
            "GEMINI_API_KEY": integration_status.gemini_configured,
            "GROQ_API_KEY": integration_status.groq_configured,
            "ALPHA_VANTAGE_API_KEY": integration_status.alpha_vantage_configured,
            "FMP_API_KEY": integration_status.fmp_configured,
            "SEC_USER_AGENT": integration_status.sec_user_agent_configured,
        }.items()
        if not configured
    ]
    report_payload["data_quality"]["disabled_features"] = integration_status.unavailable_features
    report_payload = jsonable_encoder(report_payload)

    report = AIReport(
        id=str(uuid4()),
        upload_id=str(payload.upload_id),
        portfolio_upload_id=str(payload.portfolio_upload_id) if payload.portfolio_upload_id else None,
        title=report_payload["title"],
        trading_personality=report_payload["summary"]["trading_personality"],
        overall_behavior_score=report_payload["summary"]["overall_behavior_score"],
        main_strength=report_payload["summary"]["main_strength"],
        main_weakness=report_payload["summary"]["main_weakness"],
        report_json=report_payload,
        report_markdown=report_payload["report_markdown"],
    )
    db.add(report)
    db.flush()

    for card in report_payload["metric_cards"]:
        db.add(
            BehaviorMetric(
                id=str(uuid4()),
                report_id=report.id,
                metric_name=card["name"],
                metric_value=card["score"],
                metric_payload=card["payload"],
            )
        )

    db.commit()
    return ReportGenerateResponse(
        report_id=report.id,
        status="generated",
        ai_available=report_payload["ai_available"],
        message="Behavior report generated successfully.",
    )


def fetch_report(report_id: str, db: Session) -> ReportDetailResponse:
    report = db.get(AIReport, report_id)
    if report is None:
        raise HTTPException(status_code=404, detail="Report not found.")

    payload = report.report_json
    return ReportDetailResponse(
        report_id=report.id,
        upload_id=report.upload_id,
        portfolio_upload_id=report.portfolio_upload_id,
        generated_at=datetime.fromisoformat(payload["generated_at"]),
        title=report.title,
        summary=ReportSummary(**payload["summary"]),
        metric_cards=[MetricCard(**card) for card in payload["metric_cards"]],
        capital_flow=payload["capital_flow"],
        theme_drift=payload["theme_drift"],
        trade_review_list=[TradeReviewItem(**item) for item in payload["trade_review_list"]],
        data_quality=DataQualitySection(**payload["data_quality"]),
        report_markdown=report.report_markdown or "",
        ai_available=payload.get("ai_available", False),
    )


def fetch_report_transactions(report_id: str, db: Session) -> ReportTransactionsResponse:
    report = db.get(AIReport, report_id)
    if report is None:
        raise HTTPException(status_code=404, detail="Report not found.")
    transactions = db.scalars(select(Transaction).where(Transaction.upload_id == report.upload_id).order_by(Transaction.date.asc())).all()
    return ReportTransactionsResponse(
        report_id=report.id,
        transactions=[
            {
                "date": transaction.date.isoformat() if transaction.date else None,
                "ticker": transaction.ticker,
                "action_normalized": transaction.action_normalized,
                "quantity": transaction.quantity,
                "price": transaction.price,
                "net_amount": transaction.net_amount,
                "currency": transaction.currency,
                "confidence_score": transaction.confidence_score,
            }
            for transaction in transactions
        ],
    )


def fetch_ticker_report(report_id: str, ticker: str, db: Session) -> TickerReportResponse:
    report = db.get(AIReport, report_id)
    if report is None:
        raise HTTPException(status_code=404, detail="Report not found.")

    payload = report.report_json
    ticker_key = ticker.upper()
    detail = payload.get("ticker_details", {}).get(ticker_key)
    if detail is None:
        raise HTTPException(status_code=404, detail=f"Ticker {ticker_key} not found in this report.")

    transactions = db.scalars(
        select(Transaction)
        .where(Transaction.upload_id == report.upload_id, Transaction.ticker == ticker_key)
        .order_by(Transaction.date.asc())
    ).all()

    return TickerReportResponse(
        report_id=report.id,
        ticker=ticker_key,
        first_buy_date=detail["first_buy_date"],
        latest_buy_date=detail["latest_buy_date"],
        latest_sell_date=detail["latest_sell_date"],
        total_bought=detail["total_bought"],
        total_sold=detail["total_sold"],
        net_invested=detail["net_invested"],
        current_shares=detail["current_shares"],
        average_buy_price=detail["average_buy_price"],
        realized_events=detail["realized_events"],
        behavioral_note=detail["behavioral_note"],
        timeline=[
            TickerTimelineEntry(
                date=transaction.date,
                action_normalized=transaction.action_normalized,
                quantity=transaction.quantity,
                price=transaction.price,
                net_amount=transaction.net_amount,
                description=transaction.description,
            )
            for transaction in transactions
        ],
    )


def fetch_report_warnings(report_id: str, db: Session) -> WarningListResponse:
    report = db.get(AIReport, report_id)
    if report is None:
        raise HTTPException(status_code=404, detail="Report not found.")
    warnings = db.scalars(select(ParseWarning).where(ParseWarning.upload_id == report.upload_id)).all()
    return WarningListResponse(
        report_id=report.id,
        warnings=[
            {
                "row_number": warning.row_number,
                "warning_type": warning.warning_type,
                "warning_message": warning.warning_message,
                "raw_payload": warning.raw_payload,
            }
            for warning in warnings
        ],
    )
