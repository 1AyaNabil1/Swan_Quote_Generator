"""
Shared fixtures. Gemini is replaced by a fake, so the tests need no API key or network.
"""

import os


os.environ.setdefault("GEMINI_API_KEY", "test-key")  # before the app reads its settings

import pytest
from fastapi.testclient import TestClient
from google.genai import types

from app.api.routes import quote_routes
from app.api.utils import ai_client, rate_limit
from app.main import app


def quote_response(text: str, finish=types.FinishReason.STOP) -> types.GenerateContentResponse:
    return types.GenerateContentResponse(
        candidates=[
            types.Candidate(
                content=types.Content(role="model", parts=[types.Part(text=text)]),
                finish_reason=finish,
            )
        ]
    )


class FakeModels:
    """Stands in for `client.aio.models`. Set `result` to a response, an exception to
    raise, or an async function to await."""

    def __init__(self):
        self.calls = []
        self.result = quote_response("Keep going; the road remembers every step.")

    async def generate_content(self, *, model, contents, config):
        self.calls.append({"model": model, "contents": contents, "config": config})
        if isinstance(self.result, BaseException):
            raise self.result
        if callable(self.result):
            return await self.result()
        return self.result


class FakeGemini:
    def __init__(self):
        self.models = FakeModels()
        self.aio = self


@pytest.fixture
def gemini(monkeypatch) -> FakeModels:
    fake = FakeGemini()
    monkeypatch.setattr(ai_client.genai, "Client", lambda **_: fake)
    monkeypatch.setattr(quote_routes, "_controller", None)
    rate_limit.per_client.reset()
    rate_limit.overall.reset()
    return fake.models


@pytest.fixture
def client(gemini) -> TestClient:
    with TestClient(app) as test_client:
        yield test_client
