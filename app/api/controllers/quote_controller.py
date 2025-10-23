"""
Controller for quote generation logic.
"""
from datetime import datetime
from app.api.models import QuoteRequest, QuoteResponse
from app.api.utils import AIClient, PromptBuilder


class QuoteController:
    """Controller for handling quote generation."""
    
    def __init__(self):
        """Initialize the controller with AI client and prompt builder."""
        self.ai_client = AIClient()
        self.prompt_builder = PromptBuilder()
    
    async def generate_quote(self, request: QuoteRequest) -> QuoteResponse:
        """
        Generate a quote based on the request parameters.
        
        Args:
            request: QuoteRequest containing generation parameters
            
        Returns:
            QuoteResponse containing the generated quote
            
        Raises:
            Exception: If quote generation fails
        """
        # Build the prompts
        system_prompt = self.prompt_builder.build_system_prompt()
        user_prompt = self.prompt_builder.build_quote_prompt(
            category=request.category.value,
            topic=request.topic,
            style=request.style,
            length=request.length or "medium"
        )
        
        # Generate the quote using AI
        quote_text = await self.ai_client.generate_quote(
            prompt=user_prompt,
            system_prompt=system_prompt
        )
        
        # Create and return the response
        return QuoteResponse(
            quote=quote_text,
            author="Ayō",
            category=request.category.value,
            timestamp=datetime.utcnow().isoformat() + "Z"
        )
    
    async def get_random_quote(self) -> QuoteResponse:
        """
        Generate a random quote without specific parameters.
        
        Returns:
            QuoteResponse containing a randomly generated quote
        """
        from app.api.models import QuoteCategory
        # Create a default request
        request = QuoteRequest(category=QuoteCategory.RANDOM)
        return await self.generate_quote(request)
