from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    model_config = SettingsConfigDict(env_file=".env", extra="ignore")

    # Telegram
    telegram_bot_token: str
    telegram_webhook_secret: str

    # OpenAI
    openai_api_key: str
    openai_model: str = "gpt-4o-mini"

    # MongoDB
    mongo_uri: str
    mongo_db_name: str = "chatbot"

    # PostgreSQL
    postgres_uri: str

    # Redis
    redis_uri: str

    # Rate limiting
    rate_limit_messages: int = 10   # máximo de mensagens...
    rate_limit_window: int = 60     # ...por janela em segundos

    # Memória
    memory_window_size: int = 10

    # App
    app_host: str = "0.0.0.0"
    app_port: int = 8000
    webhook_base_url: str


settings = Settings()
