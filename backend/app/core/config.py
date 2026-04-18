from functools import lru_cache

from pydantic import Field
from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    app_name: str = "AI PM Platform Backend"
    app_version: str = "1.0.0"
    environment: str = "development"

    host: str = "0.0.0.0"
    port: int = 8000

    gemini_api_key: str = Field(default="", alias="GEMINI_API_KEY")
    ai_model_name: str = Field(default="gemini-2.5-flash", alias="AI_MODEL_NAME")
    ai_temperature: float = Field(default=0.1, alias="AI_TEMPERATURE")
    ai_timeout_seconds: int = Field(default=60, alias="AI_TIMEOUT_SECONDS")

    cors_origins: str = Field(
        default="http://localhost:5173,http://127.0.0.1:5173",
        alias="CORS_ORIGINS",
    )

    log_level: str = Field(default="INFO", alias="LOG_LEVEL")

    model_config = SettingsConfigDict(
        env_file=".env",
        env_file_encoding="utf-8",
        case_sensitive=False,
        extra="ignore",
    )

    @property
    def cors_origins_list(self) -> list[str]:
        return [origin.strip() for origin in self.cors_origins.split(",") if origin.strip()]


@lru_cache
def get_settings() -> Settings:
    return Settings()
