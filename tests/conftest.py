"""
Shared fixtures. Gemini is replaced by a fake, so the tests need no API key or network.
"""

import json
import os


os.environ.setdefault("GEMINI_API_KEY", "test-key")  # before the app reads its settings

import pytest
from fastapi.testclient import TestClient
from google.genai import types

from app.api.routes import quote_routes
from app.api.utils import rate_limit
from app.config import settings
from app.llm import factory
from app.main import app


QUOTE = "Keep going; the road remembers every step."
ARABIC_QUOTE = "الصبر مفتاح الفرج، والخطوة الصغيرة تصنع طريقًا طويلًا."


def quote_json(quote: str) -> str:
    return json.dumps({"quote": quote}, ensure_ascii=False)


def quote_response(
    text: str, finish=types.FinishReason.STOP, input_tokens=20, output_tokens=12
) -> types.GenerateContentResponse:
    return types.GenerateContentResponse(
        candidates=[
            types.Candidate(
                content=types.Content(role="model", parts=[types.Part(text=text)]),
                finish_reason=finish,
            )
        ],
        usage_metadata=types.GenerateContentResponseUsageMetadata(
            prompt_token_count=input_tokens, candidates_token_count=output_tokens
        ),
    )


class FakeModels:
    """Stands in for `client.aio.models`.

    Each call is answered by `by_model[model]` if set, else the next item of `script`,
    else `result`. An answer is a response, an exception to raise, or an async function
    to await.
    """

    def __init__(self):
        self.calls = []
        self.result = quote_response(quote_json(QUOTE))
        self.script = []
        self.by_model = {}

    async def generate_content(self, *, model, contents, config):
        self.calls.append({"model": model, "contents": contents, "config": config})
        if model in self.by_model:
            answer = self.by_model[model]
        elif self.script:
            answer = self.script.pop(0)
        else:
            answer = self.result
        if isinstance(answer, BaseException):
            raise answer
        if callable(answer):
            return await answer()
        return answer


class FakeGemini:
    def __init__(self):
        self.models = FakeModels()
        self.aio = self


@pytest.fixture
def gemini(monkeypatch) -> FakeModels:
    fake = FakeGemini()
    monkeypatch.setattr(factory.genai, "Client", lambda **_: fake)
    monkeypatch.setattr(quote_routes, "_controller", None)
    monkeypatch.setattr(settings, "llm_backoff", 0)
    rate_limit.per_client.reset()
    rate_limit.overall.reset()
    return fake.models


@pytest.fixture
def client(gemini) -> TestClient:
    with TestClient(app) as test_client:
        yield test_client
