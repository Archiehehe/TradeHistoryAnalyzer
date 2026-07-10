from app.core.config import Settings
from app.core.key_status import build_integration_status


def test_build_integration_status_reflects_missing_keys() -> None:
    status = build_integration_status(
        Settings(
            database_url="sqlite:///memory.db",
            sec_user_agent="TradeHistoryAnalyzer/1.0 test@example.com"
        )
    )

    assert status.database_configured is True
    assert status.gemini_configured is False
    assert any("GEMINI_API_KEY" in feature for feature in status.unavailable_features)


def test_integration_status_endpoint_returns_safe_flags(client) -> None:
    response = client.get("/api/integrations/status")

    assert response.status_code == 200
    payload = response.json()
    assert payload["database_configured"] is True
    assert "unavailable_features" in payload

