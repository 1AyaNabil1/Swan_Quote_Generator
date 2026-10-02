"""
Google Gemini, through the Google Gen AI SDK.
"""

import asyncio
import logging
import time
from dataclasses import dataclass

from google import genai
from google.genai import errors, types

from app.llm.base import (
    BadRequest,
    LLMRequest,
    LLMResult,
    RateLimited,
    Refused,
    TimedOut,
    Unavailable,
)


logger = logging.getLogger(__name__)

# Block content that Gemini rates as medium risk or higher, in every category.
SAFETY_SETTINGS = [
    types.SafetySetting(
        category=category, threshold=types.HarmBlockThreshold.BLOCK_MEDIUM_AND_ABOVE
    )
    for category in (
        types.HarmCategory.HARM_CATEGORY_HARASSMENT,
        types.HarmCategory.HARM_CATEGORY_HATE_SPEECH,
        types.HarmCategory.HARM_CATEGORY_SEXUALLY_EXPLICIT,
        types.HarmCategory.HARM_CATEGORY_DANGEROUS_CONTENT,
    )
]

# Finish reasons that mean the request was refused, not that something broke
BLOCKED_FINISH_REASONS = {
    types.FinishReason.SAFETY,
    types.FinishReason.PROHIBITED_CONTENT,
    types.FinishReason.BLOCKLIST,
    types.FinishReason.SPII,
}


@dataclass(frozen=True)
class ModelSpec:
    """A model and how much it may think.

    Written as "name", "name@<budget>" (2.5 models, e.g. "gemini-2.5-flash@0" turns
    thinking off) or "name@<level>" (3.x models, e.g. "gemini-3.5-flash-lite@minimal").
    """

    name: str
    thinking_budget: int | None = None
    thinking_level: str | None = None

    @classmethod
    def parse(cls, text: str) -> "ModelSpec":
        name, _, thinking = text.strip().partition("@")
        if not name:
            raise ValueError(f"Model spec without a model name: {text!r}")
        if not thinking or thinking.lower() == "none":
            return cls(name)
        if thinking.isdigit():
            return cls(name, thinking_budget=int(thinking))
        level = thinking.upper()
        if level not in types.ThinkingLevel.__members__:
            raise ValueError(f"Unknown thinking level in model spec: {text!r}")
        return cls(name, thinking_level=level)

    def thinking_config(self) -> types.ThinkingConfig | None:
        if self.thinking_budget is not None:
            return types.ThinkingConfig(thinking_budget=self.thinking_budget)
        if self.thinking_level is not None:
            return types.ThinkingConfig(thinking_level=types.ThinkingLevel[self.thinking_level])
        return None


class GeminiProvider:
    """One Gemini model. Maps the SDK's responses and errors to the types in base.py."""

    def __init__(self, client: genai.Client, spec: ModelSpec):
        self._client = client
        self.spec = spec
        self.name = spec.name

    def _config(self, request: LLMRequest) -> types.GenerateContentConfig:
        schema = {}
        if request.response_schema is not None:
            schema = {
                "response_mime_type": "application/json",
                "response_schema": request.response_schema,
            }
        return types.GenerateContentConfig(
            system_instruction=request.system,
            max_output_tokens=request.max_tokens,
            temperature=request.temperature,
            top_p=0.95,
            top_k=40,
            safety_settings=SAFETY_SETTINGS,
            thinking_config=self.spec.thinking_config(),
            # No tools are declared, so the SDK's function-calling loop has nothing to do
            automatic_function_calling=types.AutomaticFunctionCallingConfig(disable=True),
            **schema,
        )

    async def generate(self, request: LLMRequest, timeout: float) -> LLMResult:
        started = time.monotonic()
        try:
            response = await asyncio.wait_for(
                self._client.aio.models.generate_content(
                    model=self.name, contents=request.prompt, config=self._config(request)
                ),
                timeout=timeout,
            )
        except TimeoutError as e:
            raise TimedOut(f"{self.name}: no response within {timeout:.1f}s") from e
        except errors.APIError as e:
            detail = f"{self.name}: API error {e.code}: {e.message}"
            if e.code == 429:
                raise RateLimited(detail) from e
            if e.code and e.code >= 500:
                raise Unavailable(detail) from e
            raise BadRequest(detail) from e
        except Exception as e:  # connection errors and anything else from the transport
            raise Unavailable(f"{self.name}: {type(e).__name__}: {e}") from e

        feedback = response.prompt_feedback
        if feedback and feedback.block_reason:
            raise Refused(f"{self.name}: prompt blocked: {feedback.block_reason}")

        candidate = response.candidates[0] if response.candidates else None
        finish = candidate.finish_reason if candidate is not None else None
        if finish in BLOCKED_FINISH_REASONS:
            raise Refused(f"{self.name}: response blocked: {finish}")

        usage = response.usage_metadata
        return LLMResult(
            text=response.text or "",
            model=self.name,
            finish_reason=finish.name.lower() if finish is not None else "no_candidates",
            input_tokens=(usage.prompt_token_count or 0) if usage else 0,
            output_tokens=(
                (usage.candidates_token_count or 0) + (usage.thoughts_token_count or 0)
                if usage
                else 0
            ),
            latency=time.monotonic() - started,
        )
