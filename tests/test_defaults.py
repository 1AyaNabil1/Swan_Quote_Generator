"""
The settings Swan ships with, as a fresh deployment would see them.
"""

from app.config import Settings
from app.llm.gemini import ModelSpec


def test_default_model_has_thinking_turned_down():
    spec = ModelSpec.parse(Settings().default_model)
    # gemini-2.5-flash is no longer offered to new API projects
    assert not spec.name.startswith("gemini-2.5-flash@")
    assert spec.name != "gemini-2.5-flash"
    assert spec.thinking_level == "MINIMAL" or spec.thinking_budget == 0


def test_default_fallbacks_parse():
    for text in Settings().fallback_models:
        ModelSpec.parse(text)


def test_time_budget_leaves_room_for_a_retry_and_a_fallback():
    settings = Settings()
    assert settings.request_timeout >= 3 * settings.llm_attempt_timeout
