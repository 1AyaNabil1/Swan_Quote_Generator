from datetime import datetime
from app.api.models import QuoteRequest, QuoteResponse, QuoteCategory
from app.api.utils import AIClient, PromptBuilder
from tenacity import retry, stop_after_attempt, wait_exponential, retry_if_exception_type
import logging

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

    @retry(
        stop=stop_after_attempt(3),
        wait=wait_exponential(multiplier=1, min=4, max=10),
        retry=retry_if_exception_type(Exception),
        before_sleep=lambda retry_state: logger.warning(
            f"Retrying quote generation (attempt {retry_state.attempt_number})... Last error: {retry_state.outcome.exception()}"
        )
    )
    async def generate_quote(self, request: QuoteRequest) -> QuoteResponse:
        system_prompt = self.prompt_builder.build_system_prompt()
        user_prompt = self.prompt_builder.build_quote_prompt(
            category=request.category.value,
            topic=request.topic,
            style=request.style,
            length=request.length or "medium"
        )
        # Combine system and user prompts for Gemini
        combined_prompt = f"{system_prompt}\n\n{user_prompt}"
        
        quote_text = await self.ai_client.generate_quote(
            prompt=combined_prompt,
            max_tokens=request.max_tokens,
            temperature=request.temperature
        )
        return QuoteResponse(
            quote=quote_text,
            author="Swan",
            category=request.category.value,
            timestamp=datetime.utcnow().isoformat() + "Z"
        )

    async def get_random_quote(self) -> QuoteResponse:
        request = QuoteRequest(category=QuoteCategory.RANDOM)
        return await self.generate_quote(request)