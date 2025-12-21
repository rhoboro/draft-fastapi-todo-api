from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    model_config = SettingsConfigDict(validate_default=False)

    APP_TITLE: str = "todo-api"
    LOG_LEVEL: str = "INFO"
    DB_URI: str
    USE_CONSOLE_LOG: bool = False
    WEBHOOK_URL: str = "https://api.rhoboro.com/echo/webhook"


settings = Settings()  # type: ignore
