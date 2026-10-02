import logging
from datetime import UTC, datetime

from app.api.models import QuoteRequest, QuoteResponse
from app.api.utils import AIClient, PromptBuilder


logger = logging.getLogger(__name__)


class QuoteController:
    def __init__(self):
        self._ai_client = None
        self.prompt_builder = PromptBuilder()

    @property
    def ai_client(self):
        """Lazy initialization of AIClient to avoid startup errors."""
        if self._ai_client is None:
            self._ai_client = AIClient()
        return self._ai_client

    async def generate_quote(self, request: QuoteRequest) -> QuoteResponse:
        """Generate a quote without retry logic for faster response."""
        # The system instruction travels separately, in the Gemini request config
        prompt = self.prompt_builder.build_quote_prompt(
            category=request.category.value,
            topic=request.topic,
            style=request.style,
            length=request.length,
            language=request.language,
        )
        quote_text = await self.ai_client.generate_quote(
            prompt=prompt, max_tokens=request.max_tokens, temperature=request.temperature
        )
        return QuoteResponse(
            quote=quote_text,
            author="Swan",
            category=request.category.value,
            timestamp=datetime.now(UTC).isoformat().replace("+00:00", "Z"),
        )
