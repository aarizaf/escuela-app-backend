from functools import lru_cache
from typing import Literal

from pydantic import Field
from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    model_config = SettingsConfigDict(env_file=".env", extra="ignore")

    app_env: Literal["development", "production"] = "development"
    cors_origins: list[str] = Field(default_factory=list)

    database_url: str
    database_direct_url: str
    database_ssl: Literal["disable", "require"] = "require"
    database_pooler_transaction_mode: bool = False

    jwt_secret: str = Field(min_length=32)
    jwt_expire_minutes: int = 30


@lru_cache
def get_settings() -> Settings:
    return Settings()  # type: ignore[call-arg]
