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
    default_model: str = "gemini-1.5-flash"  # Google Gemini model
    max_tokens: int = 100  # Optimal for quote generation
    temperature: float = 0.7  # Balanced creativity

    # CORS Settings (allow all for Vercel)
    allowed_origins: List[str] = ["*"]

    class Config:
        env_file = ".env"
        env_file_encoding = "utf-8"
        case_sensitive = False
        extra = "ignore"

settings = Settings()