from uuid import UUID

from fastapi import APIRouter

from app.api.deps import AppSettings, DbSession
from app.schemas.reports import ReportDetailResponse, ReportGenerateRequest, ReportGenerateResponse, ReportTransactionsResponse, TickerReportResponse, WarningListResponse
from app.services.reports import fetch_report, fetch_report_transactions, fetch_report_warnings, fetch_ticker_report, generate_report

router = APIRouter()


@router.post("/generate", response_model=ReportGenerateResponse)
async def generate_report_endpoint(payload: ReportGenerateRequest, db: DbSession, settings: AppSettings) -> ReportGenerateResponse:
    return generate_report(payload, db, settings)


@router.get("/{report_id}", response_model=ReportDetailResponse)
async def get_report(report_id: UUID, db: DbSession) -> ReportDetailResponse:
    return fetch_report(str(report_id), db)


@router.get("/{report_id}/transactions", response_model=ReportTransactionsResponse)
async def get_report_transactions(report_id: UUID, db: DbSession) -> ReportTransactionsResponse:
    return fetch_report_transactions(str(report_id), db)


@router.get("/{report_id}/tickers/{ticker}", response_model=TickerReportResponse)
async def get_ticker_report(report_id: UUID, ticker: str, db: DbSession) -> TickerReportResponse:
    return fetch_ticker_report(str(report_id), ticker, db)


@router.get("/{report_id}/warnings", response_model=WarningListResponse)
async def get_report_warnings(report_id: UUID, db: DbSession) -> WarningListResponse:
    return fetch_report_warnings(str(report_id), db)
