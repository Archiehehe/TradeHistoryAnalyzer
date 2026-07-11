from app.core.config import Settings
from app.core.key_status import build_integration_status


def test_build_integration_status_reflects_missing_keys() -> None:
    status = build_integration_status(
        Settings(
            _env_file=None,
            DATABASE_URL="sqlite:///memory.db",
            SEC_USER_AGENT="TradeHistoryAnalyzer/1.0 test@example.com",
            GEMINI_API_KEY=None,
            GROQ_API_KEY=None,
            ALPHA_VANTAGE_API_KEY=None,
            FMP_API_KEY=None,
            R2_ACCOUNT_ID=None,
            R2_ACCESS_KEY_ID=None,
            R2_SECRET_ACCESS_KEY=None,
            R2_BUCKET_NAME=None,
            R2_PUBLIC_BASE_URL=None,
        )
    )

    assert status.database_configured is True
    assert status.gemini_configured is False
    assert any("GEMINI_API_KEY" in feature for feature in status.unavailable_features)


def test_database_dsn_normalizes_legacy_postgresql_urls() -> None:
    settings = Settings(
        _env_file=None,
        DATABASE_URL="postgresql://example.test/db",
        SEC_USER_AGENT="TradeHistoryAnalyzer/1.0 test@example.com",
    )

    assert settings.database_dsn == "postgresql+psycopg://example.test/db"


def test_integration_status_endpoint_returns_safe_flags(client) -> None:
    response = client.get("/api/integrations/status")

    assert response.status_code == 200
    payload = response.json()
    assert payload["database_configured"] is True
    assert "unavailable_features" in payload
