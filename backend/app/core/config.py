from functools import lru_cache
from pathlib import Path
from typing import Literal

from pydantic import AnyHttpUrl, Field, SecretStr, computed_field, field_validator
from pydantic_settings import BaseSettings, SettingsConfigDict

PROJECT_ROOT = Path(__file__).resolve().parents[3]
BACKEND_ROOT = Path(__file__).resolve().parents[2]


class Settings(BaseSettings):
    app_name: str = "TradeHistoryAnalyzer"
    app_version: str = "0.1.0"
    environment: Literal["development", "test", "production"] = "development"
    api_prefix: str = "/api"
    backend_cors_origins: list[str] = Field(default_factory=lambda: ["http://localhost:5173"], alias="BACKEND_CORS_ORIGINS")
    local_storage_root: Path = Field(default=PROJECT_ROOT / "backend/.data/uploads", alias="LOCAL_STORAGE_ROOT")

    gemini_api_key: SecretStr | None = Field(default=None, alias="GEMINI_API_KEY")
    groq_api_key: SecretStr | None = Field(default=None, alias="GROQ_API_KEY")
    alpha_vantage_api_key: SecretStr | None = Field(default=None, alias="ALPHA_VANTAGE_API_KEY")
    database_url: str | None = Field(default=None, alias="DATABASE_URL")
    neon_database_url: str | None = Field(default=None, alias="NEON_DATABASE_URL")
    sec_user_agent: str | None = Field(default=None, alias="SEC_USER_AGENT")

    fmp_api_key: SecretStr | None = Field(default=None, alias="FMP_API_KEY")
    r2_account_id: str | None = Field(default=None, alias="R2_ACCOUNT_ID")
    r2_access_key_id: SecretStr | None = Field(default=None, alias="R2_ACCESS_KEY_ID")
    r2_secret_access_key: SecretStr | None = Field(default=None, alias="R2_SECRET_ACCESS_KEY")
    r2_bucket_name: str | None = Field(default=None, alias="R2_BUCKET_NAME")
    r2_public_base_url: AnyHttpUrl | None = Field(default=None, alias="R2_PUBLIC_BASE_URL")

    request_timeout_seconds: float = 20.0
    ai_retry_count: int = 2
    ai_cache_ttl_seconds: int = 60 * 60 * 24

    model_config = SettingsConfigDict(
        env_file=(PROJECT_ROOT / ".env", BACKEND_ROOT / ".env"),
        env_file_encoding="utf-8",
        extra="ignore",
        case_sensitive=False,
    )

    @field_validator("backend_cors_origins", mode="before")
    @classmethod
    def parse_cors_origins(cls, value: str | list[str]) -> list[str]:
        if isinstance(value, list):
            return value
        if isinstance(value, str):
            return [item.strip() for item in value.split(",") if item.strip()]
        return ["http://localhost:5173"]

    @field_validator("local_storage_root", mode="before")
    @classmethod
    def resolve_local_storage_root(cls, value: str | Path) -> Path:
        path = Path(value)
        if path.is_absolute():
            return path
        return PROJECT_ROOT / path

    @field_validator("r2_public_base_url", mode="before")
    @classmethod
    def empty_r2_public_base_url_to_none(cls, value: str | None) -> str | None:
        if isinstance(value, str) and not value.strip():
            return None
        return value

    @computed_field
    @property
    def database_dsn(self) -> str | None:
        dsn = self.database_url or self.neon_database_url
        if dsn is None:
            return None

        # SQLAlchemy defaults plain postgresql:// URLs to the psycopg2 driver.
        # This app ships psycopg v3, so normalize legacy PostgreSQL URLs.
        if dsn.startswith("postgresql://"):
            return dsn.replace("postgresql://", "postgresql+psycopg://", 1)
        if dsn.startswith("postgres://"):
            return dsn.replace("postgres://", "postgresql+psycopg://", 1)
        return dsn

    @computed_field
    @property
    def r2_configured(self) -> bool:
        return all(
            [
                self.r2_account_id,
                self.r2_access_key_id is not None,
                self.r2_secret_access_key is not None,
                self.r2_bucket_name,
            ]
        )


@lru_cache(maxsize=1)
def get_settings() -> Settings:
    return Settings()
