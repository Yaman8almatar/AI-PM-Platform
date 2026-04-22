from functools import lru_cache
from pathlib import Path

from pydantic import AliasChoices, Field, model_validator
from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    model_config = SettingsConfigDict(
        env_file=Path(__file__).resolve().parents[2] / ".env",
        env_file_encoding="utf-8",
        extra="ignore",
    )

    environment: str = "development"
    api_v1_prefix: str = "/api"

    # Backward compatibility with old env key + support for current key.
    use_ai_mock: bool = Field(
        default=True,
        validation_alias=AliasChoices("USE_AI_MOCK", "use_ai_mock"),
    )
    use_ai_real: bool = Field(
        default=False,
        validation_alias=AliasChoices("USE_AI_REAL", "use_ai_real"),
    )

    # Gemini (current project setup)
    gemini_api_key: str = Field(
        default="",
        validation_alias=AliasChoices("GEMINI_API_KEY", "gemini_api_key"),
    )
    ai_model_name: str = Field(
        default="gemini-2.5-flash",
        validation_alias=AliasChoices("AI_MODEL_NAME", "ai_model_name"),
    )
    ai_temperature: float = Field(
        default=0.1,
        validation_alias=AliasChoices("AI_TEMPERATURE", "ai_temperature"),
    )

    # Legacy OpenAI fields (kept for compatibility)
    openai_api_key: str = Field(
        default="",
        validation_alias=AliasChoices("OPENAI_API_KEY", "openai_api_key"),
    )
    openai_model: str = Field(
        default="gpt-4-turbo-preview",
        validation_alias=AliasChoices("OPENAI_MODEL", "openai_model"),
    )

    @model_validator(mode="after")
    def normalize_ai_mode(self) -> "Settings":
        # If USE_AI_REAL=true is present, force-disable mock mode.
        if self.use_ai_real:
            self.use_ai_mock = False
        return self


@lru_cache()
def get_settings() -> Settings:
    return Settings()
