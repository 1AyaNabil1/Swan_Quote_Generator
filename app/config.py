"""
Configuration settings for the AI Quote Generator application.
"""
from pydantic_settings import BaseSettings
from typing import Optional


class Settings(BaseSettings):
    """Application settings loaded from environment variables."""
    
    # Ollama Settings
    ollama_base_url: str = "http://localhost:11434"
    
    # Application Settings
    app_name: str = "AI Quote Generator"
    app_version: str = "1.0.0"
    debug: bool = True
    host: str = "0.0.0.0"
    port: int = 8000
    
    # AI Model Settings
    default_model: str = "gemma3:270m"
    max_tokens: int = 150
    temperature: float = 0.8
    
    # CORS Settings
    allowed_origins: list = ["*"]
    
    class Config:
        env_file = ".env"
        case_sensitive = False


# Create a global settings instance
settings = Settings()
