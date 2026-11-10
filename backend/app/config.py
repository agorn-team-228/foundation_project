import os
from pydantic_settings import BaseSettings

class Settings(BaseSettings):
    DEEPSEEK_API_KEY: str = os.getenv("DEEPSEEK_API_KEY", "mock-deepseek-key")
    DEEPSEEK_BASE_URL: str = os.getenv("DEEPSEEK_BASE_URL", "https://deepseek.com") # Официальный эндпоинт
    OPENAI_API_KEY: str = os.getenv("OPENAI_API_KEY", "mock-key")
    DATABASE_URL: str = "sqlite:///./legal_assistant.db"

settings = Settings()