"""initial schema"""

from alembic import op
import sqlalchemy as sa


revision = "20260711_0001"
down_revision = None
branch_labels = None
depends_on = None


def upgrade() -> None:
    op.create_table(
        "uploads",
        sa.Column("upload_type", sa.String(length=32), nullable=False),
        sa.Column("original_filename", sa.String(length=255), nullable=False),
        sa.Column("file_count", sa.Integer(), nullable=False),
        sa.Column("status", sa.String(length=32), nullable=False),
        sa.Column("parsed_rows", sa.Integer(), nullable=False),
        sa.Column("warning_count", sa.Integer(), nullable=False),
        sa.Column("error_count", sa.Integer(), nullable=False),
        sa.Column("created_at", sa.DateTime(timezone=True), nullable=False),
        sa.Column("id", sa.String(length=36), nullable=False),
        sa.PrimaryKeyConstraint("id"),
    )
    op.create_table(
        "ticker_profiles",
        sa.Column("ticker", sa.String(length=32), nullable=False),
        sa.Column("company_name", sa.String(length=255), nullable=True),
        sa.Column("sector", sa.String(length=128), nullable=True),
        sa.Column("industry", sa.String(length=128), nullable=True),
        sa.Column("country", sa.String(length=128), nullable=True),
        sa.Column("source", sa.String(length=64), nullable=False),
        sa.Column("updated_at", sa.DateTime(timezone=True), nullable=True),
        sa.Column("created_at", sa.DateTime(timezone=True), nullable=False),
        sa.PrimaryKeyConstraint("ticker"),
    )
    op.create_table(
        "ticker_theme_map",
        sa.Column("ticker", sa.String(length=32), nullable=False),
        sa.Column("primary_theme", sa.String(length=128), nullable=True),
        sa.Column("secondary_themes", sa.JSON(), nullable=False),
        sa.Column("confidence_score", sa.Float(), nullable=False),
        sa.Column("source", sa.String(length=64), nullable=False),
        sa.Column("updated_at", sa.DateTime(timezone=True), nullable=True),
        sa.Column("created_at", sa.DateTime(timezone=True), nullable=False),
        sa.PrimaryKeyConstraint("ticker"),
    )
    op.create_table(
        "raw_files",
        sa.Column("upload_id", sa.String(length=36), nullable=False),
        sa.Column("filename", sa.String(length=255), nullable=False),
        sa.Column("file_type", sa.String(length=32), nullable=False),
        sa.Column("storage_path", sa.String(length=500), nullable=False),
        sa.Column("created_at", sa.DateTime(timezone=True), nullable=False),
        sa.Column("id", sa.String(length=36), nullable=False),
        sa.ForeignKeyConstraint(["upload_id"], ["uploads.id"]),
        sa.PrimaryKeyConstraint("id"),
    )
    op.create_index(op.f("ix_raw_files_upload_id"), "raw_files", ["upload_id"], unique=False)
    op.create_table(
        "current_positions",
        sa.Column("upload_id", sa.String(length=36), nullable=False),
        sa.Column("ticker", sa.String(length=32), nullable=False),
        sa.Column("security_name", sa.String(length=255), nullable=True),
        sa.Column("shares", sa.Float(), nullable=True),
        sa.Column("average_cost", sa.Float(), nullable=True),
        sa.Column("total_invested", sa.Float(), nullable=True),
        sa.Column("current_value", sa.Float(), nullable=True),
        sa.Column("portfolio_weight", sa.Float(), nullable=True),
        sa.Column("sector", sa.String(length=128), nullable=True),
        sa.Column("notes", sa.Text(), nullable=True),
        sa.Column("source", sa.String(length=64), nullable=False),
        sa.Column("created_at", sa.DateTime(timezone=True), nullable=False),
        sa.Column("id", sa.String(length=36), nullable=False),
        sa.ForeignKeyConstraint(["upload_id"], ["uploads.id"]),
        sa.PrimaryKeyConstraint("id"),
    )
    op.create_index(op.f("ix_current_positions_ticker"), "current_positions", ["ticker"], unique=False)
    op.create_index(op.f("ix_current_positions_upload_id"), "current_positions", ["upload_id"], unique=False)
    op.create_table(
        "parse_warnings",
        sa.Column("upload_id", sa.String(length=36), nullable=False),
        sa.Column("source_file_id", sa.String(length=36), nullable=True),
        sa.Column("row_number", sa.Integer(), nullable=True),
        sa.Column("warning_type", sa.String(length=64), nullable=False),
        sa.Column("warning_message", sa.Text(), nullable=False),
        sa.Column("raw_payload", sa.JSON(), nullable=False),
        sa.Column("created_at", sa.DateTime(timezone=True), nullable=False),
        sa.Column("id", sa.String(length=36), nullable=False),
        sa.ForeignKeyConstraint(["source_file_id"], ["raw_files.id"]),
        sa.ForeignKeyConstraint(["upload_id"], ["uploads.id"]),
        sa.PrimaryKeyConstraint("id"),
    )
    op.create_index(op.f("ix_parse_warnings_source_file_id"), "parse_warnings", ["source_file_id"], unique=False)
    op.create_index(op.f("ix_parse_warnings_upload_id"), "parse_warnings", ["upload_id"], unique=False)
    op.create_table(
        "transactions",
        sa.Column("upload_id", sa.String(length=36), nullable=False),
        sa.Column("source_file_id", sa.String(length=36), nullable=True),
        sa.Column("row_number", sa.Integer(), nullable=True),
        sa.Column("date", sa.Date(), nullable=True),
        sa.Column("ticker", sa.String(length=32), nullable=True),
        sa.Column("security_name", sa.String(length=255), nullable=True),
        sa.Column("action_raw", sa.String(length=255), nullable=True),
        sa.Column("action_normalized", sa.String(length=32), nullable=False),
        sa.Column("quantity", sa.Float(), nullable=True),
        sa.Column("price", sa.Float(), nullable=True),
        sa.Column("gross_amount", sa.Float(), nullable=True),
        sa.Column("fees", sa.Float(), nullable=True),
        sa.Column("net_amount", sa.Float(), nullable=True),
        sa.Column("currency", sa.String(length=16), nullable=True),
        sa.Column("description", sa.Text(), nullable=True),
        sa.Column("confidence_score", sa.Float(), nullable=False),
        sa.Column("parse_warnings", sa.JSON(), nullable=False),
        sa.Column("created_at", sa.DateTime(timezone=True), nullable=False),
        sa.Column("id", sa.String(length=36), nullable=False),
        sa.ForeignKeyConstraint(["source_file_id"], ["raw_files.id"]),
        sa.ForeignKeyConstraint(["upload_id"], ["uploads.id"]),
        sa.PrimaryKeyConstraint("id"),
    )
    op.create_index(op.f("ix_transactions_action_normalized"), "transactions", ["action_normalized"], unique=False)
    op.create_index(op.f("ix_transactions_date"), "transactions", ["date"], unique=False)
    op.create_index(op.f("ix_transactions_source_file_id"), "transactions", ["source_file_id"], unique=False)
    op.create_index(op.f("ix_transactions_ticker"), "transactions", ["ticker"], unique=False)
    op.create_index(op.f("ix_transactions_upload_id"), "transactions", ["upload_id"], unique=False)
    op.create_table(
        "ai_reports",
        sa.Column("upload_id", sa.String(length=36), nullable=False),
        sa.Column("portfolio_upload_id", sa.String(length=36), nullable=True),
        sa.Column("title", sa.String(length=255), nullable=False),
        sa.Column("trading_personality", sa.String(length=128), nullable=True),
        sa.Column("overall_behavior_score", sa.Float(), nullable=True),
        sa.Column("main_strength", sa.String(length=255), nullable=True),
        sa.Column("main_weakness", sa.String(length=255), nullable=True),
        sa.Column("report_json", sa.JSON(), nullable=False),
        sa.Column("report_markdown", sa.Text(), nullable=True),
        sa.Column("created_at", sa.DateTime(timezone=True), nullable=False),
        sa.Column("id", sa.String(length=36), nullable=False),
        sa.ForeignKeyConstraint(["portfolio_upload_id"], ["uploads.id"]),
        sa.ForeignKeyConstraint(["upload_id"], ["uploads.id"]),
        sa.PrimaryKeyConstraint("id"),
    )
    op.create_index(op.f("ix_ai_reports_upload_id"), "ai_reports", ["upload_id"], unique=False)
    op.create_table(
        "behavior_metrics",
        sa.Column("report_id", sa.String(length=36), nullable=False),
        sa.Column("metric_name", sa.String(length=128), nullable=False),
        sa.Column("metric_value", sa.JSON(), nullable=True),
        sa.Column("metric_payload", sa.JSON(), nullable=False),
        sa.Column("created_at", sa.DateTime(timezone=True), nullable=False),
        sa.Column("id", sa.String(length=36), nullable=False),
        sa.ForeignKeyConstraint(["report_id"], ["ai_reports.id"]),
        sa.PrimaryKeyConstraint("id"),
    )
    op.create_index(op.f("ix_behavior_metrics_report_id"), "behavior_metrics", ["report_id"], unique=False)


def downgrade() -> None:
    op.drop_index(op.f("ix_behavior_metrics_report_id"), table_name="behavior_metrics")
    op.drop_table("behavior_metrics")
    op.drop_index(op.f("ix_ai_reports_upload_id"), table_name="ai_reports")
    op.drop_table("ai_reports")
    op.drop_index(op.f("ix_transactions_upload_id"), table_name="transactions")
    op.drop_index(op.f("ix_transactions_ticker"), table_name="transactions")
    op.drop_index(op.f("ix_transactions_source_file_id"), table_name="transactions")
    op.drop_index(op.f("ix_transactions_date"), table_name="transactions")
    op.drop_index(op.f("ix_transactions_action_normalized"), table_name="transactions")
    op.drop_table("transactions")
    op.drop_index(op.f("ix_parse_warnings_upload_id"), table_name="parse_warnings")
    op.drop_index(op.f("ix_parse_warnings_source_file_id"), table_name="parse_warnings")
    op.drop_table("parse_warnings")
    op.drop_index(op.f("ix_current_positions_upload_id"), table_name="current_positions")
    op.drop_index(op.f("ix_current_positions_ticker"), table_name="current_positions")
    op.drop_table("current_positions")
    op.drop_index(op.f("ix_raw_files_upload_id"), table_name="raw_files")
    op.drop_table("raw_files")
    op.drop_table("ticker_theme_map")
    op.drop_table("ticker_profiles")
    op.drop_table("uploads")

