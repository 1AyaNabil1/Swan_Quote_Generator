"""
Configuration settings for the AI Quote Generator application.
"""

from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    """Application settings loaded from environment variables."""

    model_config = SettingsConfigDict(
        env_file=".env",
        env_file_encoding="utf-8",
        case_sensitive=False,
        extra="ignore",
        env_parse_none_str="none",  # THINKING_BUDGET=none
    )

    # Application Settings
    app_name: str = "Swan"
    app_version: str = "2.0.0"
    debug: bool = True

    # Google Gemini API Configuration
    gemini_api_key: str = ""  # Required: set GEMINI_API_KEY in the environment

    # AI Model Settings
    default_model: str = "gemini-2.5-flash"
    max_tokens: int = 300  # Room for a 45-word quote in Arabic
    temperature: float = 0.8  # Balanced creativity
    request_timeout: float = 30  # total seconds per request, across retries and fallbacks
    # Thinking tokens to allow; 0 turns thinking off on 2.5 Flash. THINKING_BUDGET=none
    # leaves it to the model, e.g. for models that can't turn thinking off.
    thinking_budget: int | None = 0

    # Models tried in order when the default model is rate limited, down or slow, as a
    # JSON list of specs: "name", "name@<thinking budget>" or "name@<thinking level>",
    # e.g. FALLBACK_MODELS='["gemini-3.5-flash-lite@minimal"]'. A refusal is never
    # retried on another model.
    fallback_models: list[str] = []
    llm_retries: int = 1  # extra tries on the same model after an outage or dropped connection
    llm_backoff: float = 0.25  # seconds before the first retry; doubles each time
    llm_attempt_timeout: float = 15  # cap per model call, so a hanging model leaves time
    circuit_breaker_threshold: int = 5  # failures in a row before a model is skipped
    circuit_breaker_cooldown: float = 30  # seconds a skipped model stays skipped

    # Guardrails: prompt-injection checks on the topic and style, checks on the answer
    guardrails_enabled: bool = True
    max_generation_attempts: int = 2  # an answer that fails the checks is regenerated once

    # Rate limits, per process (multiply by the number of uvicorn workers)
    rate_limit_enabled: bool = True
    rate_limit_per_client: int = 10  # quotes per client per minute
    rate_limit_global: int = 120  # quotes per minute across all clients

    # Extra origins allowed to call the API from a browser, as a JSON list, e.g.
    # ALLOWED_ORIGINS='["https://example.com"]'. The bundled frontend is same-origin
    # and needs none.
    allowed_origins: list[str] = []


settings = Settings()
