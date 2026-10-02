"""
What a model provider takes, returns and raises, independent of any SDK.
"""

from dataclasses import dataclass
from typing import Protocol

from pydantic import BaseModel


@dataclass(frozen=True)
class LLMRequest:
    prompt: str
    system: str
    max_tokens: int
    temperature: float
    # When set, the provider constrains the output to JSON matching this model
    response_schema: type[BaseModel] | None = None


@dataclass(frozen=True)
class LLMResult:
    text: str
    model: str
    finish_reason: str  # lowercase: "stop", "max_tokens", "recitation", ...
    input_tokens: int = 0
    output_tokens: int = 0  # including any thinking tokens, since those are billed too
    latency: float = 0.0  # seconds


class LLMError(Exception):
    """A failed model call.

    `retryable`: trying the same model again may work (an outage, a dropped connection).
    `fallback`: a different model may work (a rate limit, a timeout, a misconfigured model).
    """

    retryable = False
    fallback = False


class Refused(LLMError):
    """The model's safety system refused. Never retried on another model: that would be
    a way around the safety filters."""


class RateLimited(LLMError):
    fallback = True


class Unavailable(LLMError):
    retryable = True
    fallback = True


class TimedOut(LLMError):
    fallback = True


class BadRequest(LLMError):
    """Rejected by the API: a bad key, an unknown model, an unsupported setting."""

    fallback = True


class CircuitOpen(LLMError):
    """The model failed repeatedly and is being skipped for a while."""

    fallback = True


class LLMProvider(Protocol):
    name: str

    async def generate(self, request: LLMRequest, timeout: float) -> LLMResult: ...
