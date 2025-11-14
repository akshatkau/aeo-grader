from pydantic_settings import BaseSettings
import os

class Settings(BaseSettings):
    OPENAI_API_KEY: str | None = None
    ANTHROPIC_API_KEY: str | None = None
    GOOGLE_API_KEY: str | None = None
    TIMEOUT_SECS: int = 25

    class Config:
        env_file = ".env"
        env_file_encoding = "utf-8"

settings = Settings()
