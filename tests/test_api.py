"""
API behaviour, with Gemini faked out.
"""

import asyncio

from conftest import quote_response
from google.genai import errors, types

from app.api.utils import ai_client, rate_limit
from app.config import settings


def generate(client, headers=None, **body):
    return client.post("/api/quotes/generate", json={"category": "wisdom", **body}, headers=headers)


# --- happy path ---


def test_health_reports_version_and_model(client):
    body = client.get("/health").json()
    assert body["status"] == "healthy"
    assert body["model"] == settings.default_model


def test_categories(client):
    assert "motivation" in client.get("/api/quotes/categories").json()


def test_generate_returns_the_quote(client):
    response = generate(client)
    assert response.status_code == 200
    body = response.json()
    assert body["quote"] == "Keep going; the road remembers every step."
    assert body["author"] == "Swan"
    assert body["category"] == "wisdom"
    assert body["timestamp"].endswith("Z")


def test_random_quote(client, gemini):
    response = client.get("/api/quotes/random")
    assert response.status_code == 200
    assert gemini.calls[0]["contents"].startswith("Create a random quote")


# --- what is sent to Gemini ---


def test_safety_filters_are_on_for_every_category(client, gemini):
    generate(client)
    config = gemini.calls[0]["config"]
    thresholds = {s.category: s.threshold for s in config.safety_settings}
    assert thresholds == {
        types.HarmCategory.HARM_CATEGORY_HARASSMENT: types.HarmBlockThreshold.BLOCK_MEDIUM_AND_ABOVE,
        types.HarmCategory.HARM_CATEGORY_HATE_SPEECH: types.HarmBlockThreshold.BLOCK_MEDIUM_AND_ABOVE,
        types.HarmCategory.HARM_CATEGORY_SEXUALLY_EXPLICIT: types.HarmBlockThreshold.BLOCK_MEDIUM_AND_ABOVE,
        types.HarmCategory.HARM_CATEGORY_DANGEROUS_CONTENT: types.HarmBlockThreshold.BLOCK_MEDIUM_AND_ABOVE,
    }


def test_request_defaults(client, gemini):
    generate(client)
    call = gemini.calls[0]
    assert call["model"] == settings.default_model
    assert call["config"].system_instruction == ai_client.SYSTEM_INSTRUCTION
    assert call["config"].max_output_tokens == settings.max_tokens
    assert call["config"].temperature == settings.temperature
    assert call["config"].thinking_config.thinking_budget == 0
    assert call["config"].automatic_function_calling.disable is True


def test_temperature_zero_is_not_replaced_by_the_default(client, gemini):
    generate(client, temperature=0.0)
    assert gemini.calls[0]["config"].temperature == 0.0


def test_thinking_config_can_be_left_to_the_model(client, gemini, monkeypatch):
    monkeypatch.setattr(settings, "thinking_budget", None)
    generate(client)
    assert gemini.calls[0]["config"].thinking_config is None


def test_prompt_carries_topic_style_and_language(client, gemini):
    generate(client, topic="patience", style="Shakespearean", language="ar", length="short")
    prompt = gemini.calls[0]["contents"]
    assert 'about "patience"' in prompt
    assert "Elizabethan English" in prompt
    assert "about 15 words" in prompt
    assert "Write ONLY in Arabic" in prompt


def test_unknown_style_is_passed_as_quoted_text(client, gemini):
    generate(client, style="like a sports commentator")
    assert 'Write it in this style: "like a sports commentator"' in gemini.calls[0]["contents"]


# --- validation ---


def test_invalid_language_is_rejected_before_gemini(client, gemini):
    assert generate(client, language="fr").status_code == 422
    assert gemini.calls == []


def test_invalid_length_is_rejected(client, gemini):
    assert generate(client, length="epic").status_code == 422
    assert gemini.calls == []


def test_max_tokens_over_the_limit_is_rejected(client, gemini):
    assert generate(client, max_tokens=2048).status_code == 422
    assert gemini.calls == []


# --- Gemini refusals and failures ---


def test_blocked_prompt_returns_a_friendly_422(client, gemini):
    gemini.result = types.GenerateContentResponse(
        prompt_feedback=types.GenerateContentResponsePromptFeedback(
            block_reason=types.BlockedReason.SAFETY
        )
    )
    response = generate(client, topic="something harmful")
    assert response.status_code == 422
    assert response.json()["detail"] == ai_client.BLOCKED_MESSAGE


def test_blocked_response_returns_a_friendly_422(client, gemini):
    gemini.result = quote_response("", finish=types.FinishReason.SAFETY)
    response = generate(client)
    assert response.status_code == 422
    assert response.json()["detail"] == ai_client.BLOCKED_MESSAGE


def test_empty_response_returns_502(client, gemini):
    gemini.result = quote_response("   ")
    response = generate(client)
    assert response.status_code == 502
    assert response.json()["detail"] == ai_client.FAILED_MESSAGE


def test_quota_exhausted_returns_503(client, gemini):
    gemini.result = errors.APIError(
        429,
        {"error": {"code": 429, "message": "Resource exhausted", "status": "RESOURCE_EXHAUSTED"}},
    )
    response = generate(client)
    assert response.status_code == 503
    assert response.json()["detail"] == ai_client.BUSY_MESSAGE


def test_api_error_details_are_not_shown_to_the_user(client, gemini):
    gemini.result = errors.APIError(
        400,
        {"error": {"code": 400, "message": "API key not valid: AIza-secret", "status": "INVALID"}},
    )
    response = generate(client)
    assert response.status_code == 502
    assert response.json()["detail"] == ai_client.FAILED_MESSAGE
    assert "AIza" not in response.text


def test_unexpected_error_is_generic(client, gemini):
    gemini.result = RuntimeError("connection pool exhausted at 10.0.0.3")
    response = generate(client)
    assert response.status_code == 502
    assert "10.0.0.3" not in response.text


def test_timeout_returns_504(client, gemini, monkeypatch):
    monkeypatch.setattr(settings, "request_timeout", 0.05)

    async def slow():
        await asyncio.sleep(1)

    gemini.result = slow
    response = generate(client)
    assert response.status_code == 504
    assert response.json()["detail"] == ai_client.TIMEOUT_MESSAGE


# --- rate limits ---


def test_rate_limit_per_client(client, monkeypatch):
    monkeypatch.setattr(rate_limit.per_client, "limit", 3)
    me = {"cf-connecting-ip": "203.0.113.7"}
    assert [generate(client, me).status_code for _ in range(3)] == [200, 200, 200]

    blocked = generate(client, me)
    assert blocked.status_code == 429
    assert int(blocked.headers["retry-after"]) >= 1

    assert generate(client, {"cf-connecting-ip": "198.51.100.2"}).status_code == 200


def test_rate_limit_reads_x_forwarded_for(client, monkeypatch):
    monkeypatch.setattr(rate_limit.per_client, "limit", 1)
    first = {"x-forwarded-for": "203.0.113.9, 10.0.0.1"}
    assert generate(client, first).status_code == 200
    assert generate(client, first).status_code == 429
    assert generate(client, {"x-forwarded-for": "203.0.113.10, 10.0.0.1"}).status_code == 200


def test_global_rate_limit(client, monkeypatch):
    monkeypatch.setattr(rate_limit.overall, "limit", 2)
    codes = [generate(client, {"cf-connecting-ip": f"203.0.113.{n}"}).status_code for n in range(3)]
    assert codes == [200, 200, 429]


def test_random_endpoint_is_rate_limited(client, monkeypatch):
    monkeypatch.setattr(rate_limit.per_client, "limit", 1)
    assert client.get("/api/quotes/random").status_code == 200
    assert client.get("/api/quotes/random").status_code == 429


def test_categories_are_not_rate_limited(client, monkeypatch):
    monkeypatch.setattr(rate_limit.per_client, "limit", 1)
    assert [client.get("/api/quotes/categories").status_code for _ in range(3)] == [200, 200, 200]


def test_rate_limit_can_be_turned_off(client, monkeypatch):
    monkeypatch.setattr(settings, "rate_limit_enabled", False)
    monkeypatch.setattr(rate_limit.per_client, "limit", 1)
    assert [generate(client).status_code for _ in range(3)] == [200, 200, 200]


# --- CORS ---


def test_no_cors_for_other_origins_by_default(client):
    response = client.get("/api/quotes/categories", headers={"origin": "https://evil.example"})
    assert "access-control-allow-origin" not in response.headers
