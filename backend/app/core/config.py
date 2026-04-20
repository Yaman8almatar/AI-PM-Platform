from pydantic_settings import BaseSettings
from functools import lru_cache

class Settings(BaseSettings):
    environment: str = "development"
    api_v1_prefix: str = "/api"
    use_ai_mock: bool = True
    openai_api_key: str = ""
    openai_model: str = "gpt-4-turbo-preview"

    class Config:
        env_file = ".env"
        extra = "ignore"

@lru_cache()
def get_settings():
    return Settings()