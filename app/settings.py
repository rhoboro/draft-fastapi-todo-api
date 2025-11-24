from pydantic import PostgresDsn
from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    model_config = SettingsConfigDict(validate_default=False)

    APP_TITLE: str = "todo-api"
    LOG_LEVEL: str = "INFO"
    ECHO_SQL: bool = False
    DB_URI: PostgresDsn


settings = Settings()  # type: ignore
