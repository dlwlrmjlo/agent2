# app/core/config.py
from pydantic_settings import BaseSettings, SettingsConfigDict

class Settings(BaseSettings):
    OLLAMA_API: str = "http://localhost:11434/api/generate"
    MODEL_NAME: str = "mistral"
    TIMEOUT: int = 120
    TELEGRAM_BOT_TOKEN: str = "7555617579:AAGUom_03MEY1vYkXFgmkzyen0j5v9rIDyg"
    TELEGRAM_CHAT_ID: str = "7937625287"
    WEBHOOK_SECRET: str | None = None
    NEWS_CACHE_TTL_S: int = 300
    NEWS_MAX_ITEMS: int = 8
    SCHED_INTERVAL_S: int = 60
    DATABASE_URL: str = "sqlite:///./alertas.db"
    model_config = SettingsConfigDict(env_file=".env", extra="ignore")

settings = Settings()


# C:\Users\joako>curl "https://api.telegram.org/bot7555617579:AAGUom_03MEY1vYkXFgmkzyen0j5v9rIDyg/setWebhook" ^
# ¿Más?   -d "url=https://7ac92b610887.ngrok-free.app/webhook/telegram?token=<WEBHOOK_SECRET>" ^
# ¿Más?   -d "drop_pending_updates=true" ^
# ¿Más?   -d "allowed_updates=message,callback_query"
# {"ok":true,"result":true,"description":"Webhook was set"}
