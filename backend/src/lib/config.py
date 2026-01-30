"""
Application configuration loaded from environment variables.
"""

from functools import lru_cache
from typing import Literal

from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    """Application settings loaded from environment variables."""

    model_config = SettingsConfigDict(
        env_file=".env",
        env_file_encoding="utf-8",
        case_sensitive=False,
        extra="ignore",
    )

    # Database
    database_url: str

    # Moirai Model
    moirai_model: str = "Salesforce/moirai-1.0-R-base"
    moirai_context_length: int = 100
    moirai_prediction_length: int = 24
    moirai_num_samples: int = 100

    # API
    api_host: str = "0.0.0.0"
    api_port: int = 8000

    # Logging
    log_level: Literal["DEBUG", "INFO", "WARNING", "ERROR", "CRITICAL"] = "INFO"

    # Environment
    environment: Literal["development", "staging", "production"] = "development"

    @property
    def is_production(self) -> bool:
        return self.environment == "production"

    @property
    def async_database_url(self) -> str:
        """Convert postgres:// to postgresql+asyncpg:// for async support."""
        url = self.database_url
        if url.startswith("postgres://"):
            url = url.replace("postgres://", "postgresql+asyncpg://", 1)
        elif url.startswith("postgresql://"):
            url = url.replace("postgresql://", "postgresql+asyncpg://", 1)
        return url

    @property
    def sync_database_url(self) -> str:
        """Ensure URL uses postgresql:// for sync connections."""
        url = self.database_url
        if url.startswith("postgres://"):
            url = url.replace("postgres://", "postgresql://", 1)
        return url


@lru_cache
def get_settings() -> Settings:
    """Get cached settings instance."""
    return Settings()
