"""
Configuration settings for the AI Quote Generator application.
"""
from pydantic_settings import BaseSettings
from typing import List

class Settings(BaseSettings):
    """Application settings loaded from environment variables."""

    # Application Settings
    app_name: str = "Swan"
    app_version: str = "1.0.0"
    debug: bool = True

    # Google Gemini API Configuration
    gemini_api_key: str = ""  # Required: Set in Vercel environment variables
    
    # AI Model Settings
    default_model: str = "gemini-1.5-flash-8b"  # Fastest Gemini model
    max_tokens: int = 150  # Safe for complete quote generation
    temperature: float = 0.8  # Balanced creativity
    request_timeout: int = 10  # Request timeout in seconds

    # CORS Settings (allow all for Vercel)
    allowed_origins: List[str] = ["*"]

    class Config:
        env_file = ".env"
        env_file_encoding = "utf-8"
        case_sensitive = False
        extra = "ignore"

settings = Settings()