"""
Configuration settings for the AI Quote Generator application.
"""
from pydantic_settings import BaseSettings
from typing import List

class Settings(BaseSettings):
    """Application settings loaded from environment variables."""

    # Google Gemini API Configuration
    gemini_api_key: str  # Required API key for Google Gemini
    
    # Application Settings
    app_name: str = "Swan"
    app_version: str = "1.0.0"
    debug: bool = True
    host: str = "0.0.0.0"
    port: int = 8000

    # AI Model Settings
    default_model: str = "gemini-1.5-flash"  # Google Gemini model (free tier)
    max_tokens: int = 2048  # Free tier max for gemini-1.5-flash is 8192, using 2048 for safety
    temperature: float = 0.7

    # CORS Settings
    allowed_origins: List[str] = [
        "http://localhost:8000",
        "http://127.0.0.1:8000",
        "https://your-production-domain.com"
    ]

    # Retry Settings
    enable_retries: bool = True
    max_retry_attempts: int = 3
    retry_min_wait: int = 4
    retry_max_wait: int = 10

    class Config:
        env_file = ".env"
        env_file_encoding = "utf-8"
        case_sensitive = False
        extra = "ignore"  # Ignore extra fields in .env file

    def model_dump(self):
        """Override model_dump to exclude sensitive fields like API key."""
        data = super().model_dump()
        return data

settings = Settings()