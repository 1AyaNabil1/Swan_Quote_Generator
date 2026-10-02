"""
Builds the model chain from the settings.
"""

from google import genai

from app.config import settings
from app.llm.gemini import GeminiProvider, ModelSpec
from app.llm.resilience import ResilientLLM


def primary_spec() -> ModelSpec:
    spec = ModelSpec.parse(settings.default_model)
    # THINKING_BUDGET predates model specs and only means something to 2.5 models;
    # 3.x models reject a budget or ignore it, and take "name@<level>" instead
    unset = spec.thinking_budget is None and spec.thinking_level is None
    if unset and settings.thinking_budget is not None and spec.name.startswith("gemini-2"):
        return ModelSpec(spec.name, thinking_budget=settings.thinking_budget)
    return spec


def model_specs() -> list[ModelSpec]:
    """The primary model, then the fallbacks, in the order they are tried."""
    return [primary_spec(), *(ModelSpec.parse(spec) for spec in settings.fallback_models)]


def build_llm() -> ResilientLLM:
    if not settings.gemini_api_key:
        raise RuntimeError("GEMINI_API_KEY not set. Configure it in the environment.")
    client = genai.Client(api_key=settings.gemini_api_key)
    return ResilientLLM(
        [GeminiProvider(client, spec) for spec in model_specs()],
        retries=settings.llm_retries,
        backoff=settings.llm_backoff,
        attempt_timeout=settings.llm_attempt_timeout,
        breaker_threshold=settings.circuit_breaker_threshold,
        breaker_cooldown=settings.circuit_breaker_cooldown,
    )
