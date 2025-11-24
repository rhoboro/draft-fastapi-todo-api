from pydantic import PostgresDsn
from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    model_config = SettingsConfigDict(validate_default=False)

    APP_TITLE: str = "todo-api"
    LOG_LEVEL: str = "INFO"
    DB_URI: PostgresDsn
    USE_CONSOLE_LOG: bool = False


settings = Settings()  # type: ignore
