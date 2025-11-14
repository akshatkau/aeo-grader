import os
from pydantic import BaseModel



class Settings(BaseModel):
    ENV: str = os.getenv("ENV", "dev")
    OPENAI_API_KEY: str | None = os.getenv("OPENAI_API_KEY")
    GOOGLE_API_KEY: str | None = os.getenv("GOOGLE_API_KEY")
    TIMEOUT_SECS: int = int(os.getenv("TIMEOUT_SECS", "25"))

settings = Settings()
