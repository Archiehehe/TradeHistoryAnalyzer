from datetime import date, datetime

from sqlalchemy import Date, DateTime, Float, ForeignKey, Integer, JSON, String, Text
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.db.base import Base, TimestampMixin, UUIDPrimaryKeyMixin


class Upload(UUIDPrimaryKeyMixin, TimestampMixin, Base):
    __tablename__ = "uploads"

    upload_type: Mapped[str] = mapped_column(String(32), nullable=False)
    original_filename: Mapped[str] = mapped_column(String(255), nullable=False)
    file_count: Mapped[int] = mapped_column(Integer, default=1, nullable=False)
    status: Mapped[str] = mapped_column(String(32), default="pending", nullable=False)
    parsed_rows: Mapped[int] = mapped_column(Integer, default=0, nullable=False)
    warning_count: Mapped[int] = mapped_column(Integer, default=0, nullable=False)
    error_count: Mapped[int] = mapped_column(Integer, default=0, nullable=False)

    raw_files: Mapped[list["RawFile"]] = relationship(back_populates="upload", cascade="all, delete-orphan")
    transactions: Mapped[list["Transaction"]] = relationship(back_populates="upload", cascade="all, delete-orphan")
    current_positions: Mapped[list["CurrentPosition"]] = relationship(back_populates="upload", cascade="all, delete-orphan")
    reports: Mapped[list["AIReport"]] = relationship(
        back_populates="upload",
        cascade="all, delete-orphan",
        foreign_keys="AIReport.upload_id",
    )
    parse_warnings: Mapped[list["ParseWarning"]] = relationship(back_populates="upload", cascade="all, delete-orphan")


class RawFile(UUIDPrimaryKeyMixin, TimestampMixin, Base):
    __tablename__ = "raw_files"

    upload_id: Mapped[str] = mapped_column(ForeignKey("uploads.id"), nullable=False, index=True)
    filename: Mapped[str] = mapped_column(String(255), nullable=False)
    file_type: Mapped[str] = mapped_column(String(32), nullable=False)
    storage_path: Mapped[str] = mapped_column(String(500), nullable=False)

    upload: Mapped["Upload"] = relationship(back_populates="raw_files")


class Transaction(UUIDPrimaryKeyMixin, TimestampMixin, Base):
    __tablename__ = "transactions"

    upload_id: Mapped[str] = mapped_column(ForeignKey("uploads.id"), nullable=False, index=True)
    source_file_id: Mapped[str | None] = mapped_column(ForeignKey("raw_files.id"), nullable=True, index=True)
    row_number: Mapped[int | None] = mapped_column(Integer, nullable=True)
    date: Mapped[date | None] = mapped_column(Date, nullable=True, index=True)
    ticker: Mapped[str | None] = mapped_column(String(32), nullable=True, index=True)
    security_name: Mapped[str | None] = mapped_column(String(255), nullable=True)
    action_raw: Mapped[str | None] = mapped_column(String(255), nullable=True)
    action_normalized: Mapped[str] = mapped_column(String(32), default="unknown", nullable=False, index=True)
    quantity: Mapped[float | None] = mapped_column(Float, nullable=True)
    price: Mapped[float | None] = mapped_column(Float, nullable=True)
    gross_amount: Mapped[float | None] = mapped_column(Float, nullable=True)
    fees: Mapped[float | None] = mapped_column(Float, nullable=True)
    net_amount: Mapped[float | None] = mapped_column(Float, nullable=True)
    currency: Mapped[str | None] = mapped_column(String(16), nullable=True)
    description: Mapped[str | None] = mapped_column(Text, nullable=True)
    confidence_score: Mapped[float] = mapped_column(Float, default=0.0, nullable=False)
    parse_warnings: Mapped[list[str]] = mapped_column(JSON, default=list, nullable=False)

    upload: Mapped["Upload"] = relationship(back_populates="transactions")


class CurrentPosition(UUIDPrimaryKeyMixin, TimestampMixin, Base):
    __tablename__ = "current_positions"

    upload_id: Mapped[str] = mapped_column(ForeignKey("uploads.id"), nullable=False, index=True)
    ticker: Mapped[str] = mapped_column(String(32), nullable=False, index=True)
    security_name: Mapped[str | None] = mapped_column(String(255), nullable=True)
    shares: Mapped[float | None] = mapped_column(Float, nullable=True)
    average_cost: Mapped[float | None] = mapped_column(Float, nullable=True)
    total_invested: Mapped[float | None] = mapped_column(Float, nullable=True)
    current_value: Mapped[float | None] = mapped_column(Float, nullable=True)
    portfolio_weight: Mapped[float | None] = mapped_column(Float, nullable=True)
    sector: Mapped[str | None] = mapped_column(String(128), nullable=True)
    notes: Mapped[str | None] = mapped_column(Text, nullable=True)
    source: Mapped[str] = mapped_column(String(64), default="portfolio_upload", nullable=False)

    upload: Mapped["Upload"] = relationship(back_populates="current_positions")


class TickerProfile(TimestampMixin, Base):
    __tablename__ = "ticker_profiles"

    ticker: Mapped[str] = mapped_column(String(32), primary_key=True)
    company_name: Mapped[str | None] = mapped_column(String(255), nullable=True)
    sector: Mapped[str | None] = mapped_column(String(128), nullable=True)
    industry: Mapped[str | None] = mapped_column(String(128), nullable=True)
    country: Mapped[str | None] = mapped_column(String(128), nullable=True)
    source: Mapped[str] = mapped_column(String(64), default="local", nullable=False)
    updated_at: Mapped[datetime | None] = mapped_column(DateTime(timezone=True), nullable=True)


class TickerThemeMap(TimestampMixin, Base):
    __tablename__ = "ticker_theme_map"

    ticker: Mapped[str] = mapped_column(String(32), primary_key=True)
    primary_theme: Mapped[str | None] = mapped_column(String(128), nullable=True)
    secondary_themes: Mapped[list[str]] = mapped_column(JSON, default=list, nullable=False)
    confidence_score: Mapped[float] = mapped_column(Float, default=0.0, nullable=False)
    source: Mapped[str] = mapped_column(String(64), default="rules", nullable=False)
    updated_at: Mapped[datetime | None] = mapped_column(DateTime(timezone=True), nullable=True)


class AIReport(UUIDPrimaryKeyMixin, TimestampMixin, Base):
    __tablename__ = "ai_reports"

    upload_id: Mapped[str] = mapped_column(ForeignKey("uploads.id"), nullable=False, index=True)
    portfolio_upload_id: Mapped[str | None] = mapped_column(ForeignKey("uploads.id"), nullable=True)
    title: Mapped[str] = mapped_column(String(255), nullable=False)
    trading_personality: Mapped[str | None] = mapped_column(String(128), nullable=True)
    overall_behavior_score: Mapped[float | None] = mapped_column(Float, nullable=True)
    main_strength: Mapped[str | None] = mapped_column(String(255), nullable=True)
    main_weakness: Mapped[str | None] = mapped_column(String(255), nullable=True)
    report_json: Mapped[dict] = mapped_column(JSON, default=dict, nullable=False)
    report_markdown: Mapped[str | None] = mapped_column(Text, nullable=True)

    upload: Mapped["Upload"] = relationship(back_populates="reports", foreign_keys=[upload_id])
    metrics: Mapped[list["BehaviorMetric"]] = relationship(back_populates="report", cascade="all, delete-orphan")


class BehaviorMetric(UUIDPrimaryKeyMixin, TimestampMixin, Base):
    __tablename__ = "behavior_metrics"

    report_id: Mapped[str] = mapped_column(ForeignKey("ai_reports.id"), nullable=False, index=True)
    metric_name: Mapped[str] = mapped_column(String(128), nullable=False)
    metric_value: Mapped[float | int | str | None] = mapped_column(JSON, nullable=True)
    metric_payload: Mapped[dict] = mapped_column(JSON, default=dict, nullable=False)

    report: Mapped["AIReport"] = relationship(back_populates="metrics")


class ParseWarning(UUIDPrimaryKeyMixin, TimestampMixin, Base):
    __tablename__ = "parse_warnings"

    upload_id: Mapped[str] = mapped_column(ForeignKey("uploads.id"), nullable=False, index=True)
    source_file_id: Mapped[str | None] = mapped_column(ForeignKey("raw_files.id"), nullable=True, index=True)
    row_number: Mapped[int | None] = mapped_column(Integer, nullable=True)
    warning_type: Mapped[str] = mapped_column(String(64), nullable=False)
    warning_message: Mapped[str] = mapped_column(Text, nullable=False)
    raw_payload: Mapped[dict] = mapped_column(JSON, default=dict, nullable=False)

    upload: Mapped["Upload"] = relationship(back_populates="parse_warnings")
