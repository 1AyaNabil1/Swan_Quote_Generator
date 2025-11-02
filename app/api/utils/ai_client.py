"""
AI client for quote generation using Google Gemini API.
Optimized for Vercel serverless deployment.
"""
import logging
from fastapi import HTTPException
import google.generativeai as genai
from app.config import settings

logger = logging.getLogger(__name__)

class AIClient:
    """Client for AI text generation using Google Gemini."""
    
    def __init__(self):
        """Initialize Google Gemini client."""
        if not settings.gemini_api_key:
            raise RuntimeError("GEMINI_API_KEY not set. Configure in Vercel environment variables.")
        
        genai.configure(api_key=settings.gemini_api_key)
        self.model = genai.GenerativeModel(settings.default_model)
        self.available = True
        logger.info(f"✓ Gemini initialized: {settings.default_model}")

    async def generate_quote(
        self,
        prompt: str,
        max_tokens: int = None,
        temperature: float = None
    ) -> str:
        """
        Generate a quote using Google Gemini API.

        Args:
            prompt: The generation prompt
            max_tokens: Maximum tokens (default from settings)
            temperature: Creativity level 0.0-1.0 (default from settings)

        Returns:
            Generated quote text (cleaned)

        Raises:
            HTTPException: If generation fails
        """
        if not self.available:
            raise HTTPException(503, "Gemini API unavailable")

        try:
            response = await self.model.generate_content_async(
                prompt,
                generation_config=genai.types.GenerationConfig(
                    max_output_tokens=max_tokens or settings.max_tokens,
                    temperature=temperature or settings.temperature,
                    top_p=0.95,
                ),
                safety_settings=[
                    {"category": cat, "threshold": "BLOCK_NONE"}
                    for cat in [
                        "HARM_CATEGORY_DANGEROUS_CONTENT",
                        "HARM_CATEGORY_HARASSMENT",
                        "HARM_CATEGORY_HATE_SPEECH",
                        "HARM_CATEGORY_SEXUALLY_EXPLICIT",
                    ]
                ]
            )
            
            # Extract and clean the quote
            quote = response.text.strip().strip('"\'')
            return quote if quote else "Unable to generate quote. Please try again."
            
        except Exception as e:
            logger.error(f"Gemini error: {str(e)}")
            raise HTTPException(500, f"Quote generation failed: {str(e)}")
