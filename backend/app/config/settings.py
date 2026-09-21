from pydantic_settings import BaseSettings
from functools import lru_cache


class Settings(BaseSettings):
    # Database
    DATABASE_URL: str = "postgresql://agromind:agromind@localhost:5432/agromind"

    # Hugging Face
    HF_API_KEY: str = ""
    HF_MODEL_ID: str = "meta-llama/Llama-3.1-8B-Instruct"
    HF_EMBEDDING_MODEL: str = "sentence-transformers/all-MiniLM-L6-v2"

    # Weather
    WEATHER_API_KEY: str = ""
    WEATHER_API_URL: str = "https://api.openweathermap.org/data/2.5"

    # Market
    MARKET_API_URL: str = "https://api.kamis.co.ke/v1"
    MARKET_API_KEY: str = ""

    # App
    APP_ENV: str = "development"
    APP_PORT: int = 8000
    FRONTEND_URL: str = "http://localhost:5173"

    # Languages
    DEFAULT_LANGUAGE: str = "sw"
    SUPPORTED_LANGUAGES: str = "en,sw"

    class Config:
        env_file = ".env"
        extra = "ignore"


@lru_cache
def get_settings():
    return Settings()


settings = get_settings()
