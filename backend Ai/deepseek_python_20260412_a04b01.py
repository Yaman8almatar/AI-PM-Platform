from pydantic_settings import BaseSettings
from functools import lru_cache

class Settings(BaseSettings):
    environment: str = "development"
    log_level: str = "INFO"
    api_v1_prefix: str = "/api"
    use_ai_real: bool = False
    gemini_api_key: str = ""
    mock_response_delay_seconds: float = 0

    class Config:
        env_file = ".env"
        extra = "ignore"

@lru_cache()
def get_settings():
    return Settings()