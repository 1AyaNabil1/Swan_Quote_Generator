from datetime import datetime
from app.api.models import QuoteRequest, QuoteResponse
from app.api.utils import AIClient, PromptBuilder


class QuoteController:
    def __init__(self):
        self.ai_client = AIClient()
        self.prompt_builder = PromptBuilder()
    
    async def generate_quote(self, request: QuoteRequest) -> QuoteResponse:
        system_prompt = self.prompt_builder.build_system_prompt()
        user_prompt = self.prompt_builder.build_quote_prompt(
            category=request.category.value,
            topic=request.topic,
            style=request.style,
            length=request.length or "medium"
        )
        quote_text = await self.ai_client.generate_quote(
            prompt=user_prompt,
            system_prompt=system_prompt
        )
        return QuoteResponse(
            quote=quote_text,
            author="Ayō",
            category=request.category.value,
            timestamp=datetime.utcnow().isoformat() + "Z"
        )
    
    async def get_random_quote(self) -> QuoteResponse:
        from app.api.models import QuoteCategory
        request = QuoteRequest(category=QuoteCategory.RANDOM)
        return await self.generate_quote(request)
