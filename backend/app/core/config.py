from enum import StrEnum
from functools import lru_cache

from pydantic import Field, PostgresDsn, model_validator
from pydantic_settings import BaseSettings, SettingsConfigDict


class AppEnvironment(StrEnum):
    LOCAL = "local"
    DEVELOPMENT = "development"
    PRODUCTION = "production"


class Settings(BaseSettings):
    model_config = SettingsConfigDict(
        env_file=".env",
        env_prefix="OMNICORE_",
        case_sensitive=False,
        extra="ignore",
    )

    app_name: str = "OmniCore AI API"
    env: AppEnvironment = AppEnvironment.LOCAL
    debug: bool = False
    api_v1_prefix: str = "/api/v1"
    cors_origins: list[str] = Field(default_factory=lambda: ["http://localhost:3000"])

    database_url: PostgresDsn | str = "postgresql+asyncpg://omnicore:omnicore@localhost:5432/omnicore"
    database_echo: bool = False

    jwt_secret_key: str = "change-me-local-development-only"
    jwt_algorithm: str = "HS256"
    jwt_issuer: str = "omnicore-ai"
    jwt_audience: str = "omnicore-ai-api"
    access_token_expire_minutes: int = 15
    refresh_token_expire_days: int = 14

    log_level: str = "INFO"
    enable_ai: bool = False
    enable_forecasting: bool = False
    phi3_endpoint_url: str | None = None
    phi3_model_name: str = "phi-3"
    phi3_model_version: str = "local"
    chroma_endpoint_url: str | None = None
    chroma_collection_name: str = "omnicore_operations"
    forecasting_model_name: str = "statistical-demand-forecaster"
    forecasting_model_version: str = "holt-linear-v1"

    @model_validator(mode="after")
    def validate_production_secrets(self) -> "Settings":
        if self.env == AppEnvironment.PRODUCTION and self.jwt_secret_key == "change-me-local-development-only":
            raise ValueError("OMNICORE_JWT_SECRET_KEY must be set for production.")
        return self


@lru_cache
def get_settings() -> Settings:
    return Settings()
