from pathlib import Path

from pydantic import SecretStr
from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    model_config = SettingsConfigDict(env_file=".env", extra="ignore")

    openai_api_key: SecretStr = SecretStr("")
    openai_model: str = "gpt-6.1-sol"
    openai_reasoning_effort: str = "low"
    ai_timeout_seconds: float = 20.0
    ai_daily_limit: int = 1500
    ai_per_user_limit: int = 40
    data_dir: Path = Path("data")
