from pydantic import SecretStr
from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    model_config = SettingsConfigDict(env_file=".env", extra="ignore")

    openai_api_key: SecretStr = SecretStr("")
    openai_model: str = "gpt-6.1-sol"
    openai_reasoning_effort: str = "low"
    intake_timeout_seconds: float = 25.0
    round_seconds: int = 0
    warmup_rounds: int = 24
