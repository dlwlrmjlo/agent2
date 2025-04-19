from pydantic_settings import BaseSettings

class Settings(BaseSettings):
    OLLAMA_API: str = "http://localhost:11434/api/generate"
    MODEL_NAME: str = "mistral"
    TIMEOUT: int = 120

settings = Settings()
