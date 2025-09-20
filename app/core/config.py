# app/core/config.py
from pydantic_settings import BaseSettings

class Settings(BaseSettings):
    OLLAMA_API: str = "http://localhost:11434/api/generate"
    MODEL_NAME: str = "mistral"
    TIMEOUT: int = 120
    TELEGRAM_BOT_TOKEN: str = "7555617579:AAGUom_03MEY1vYkXFgmkzyen0j5v9rIDyg"
    TELEGRAM_CHAT_ID: str = "7937625287"

settings = Settings()
