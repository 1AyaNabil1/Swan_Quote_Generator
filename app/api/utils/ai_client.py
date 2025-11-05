"""
AI client for quote generation using Google Gemini API.
Optimized for Vercel serverless deployment with fast response times.
"""
import logging
import asyncio
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
        Generate a quote using Google Gemini API with speed optimizations.

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
            # Use timeout to prevent hanging requests
            response = await asyncio.wait_for(
                self.model.generate_content_async(
                    prompt,
                    generation_config=genai.types.GenerationConfig(
                        max_output_tokens=max_tokens or settings.max_tokens,
                        temperature=temperature or settings.temperature,
                        top_p=0.95,
                        top_k=40,  # Speed optimization
                    ),
                    # Simplified safety settings for speed
                    safety_settings={
                        "HARM_CATEGORY_DANGEROUS_CONTENT": "BLOCK_NONE",
                        "HARM_CATEGORY_HARASSMENT": "BLOCK_NONE",
                        "HARM_CATEGORY_HATE_SPEECH": "BLOCK_NONE",
                        "HARM_CATEGORY_SEXUALLY_EXPLICIT": "BLOCK_NONE",
                    }
                ),
                timeout=settings.request_timeout
            )
            
            # Robust extraction - handle both simple and complex responses
            try:
                # Try simple text accessor first
                quote = response.text.strip().strip('"\'')
            except (ValueError, AttributeError):
                # Fallback: extract from parts if simple text fails
                if response.candidates and response.candidates[0].content.parts:
                    quote = response.candidates[0].content.parts[0].text.strip().strip('"\'')
                else:
                    raise ValueError("No valid quote content in response")
            
            return quote if quote else "Unable to generate quote. Please try again."
            
        except asyncio.TimeoutError:
            logger.error(f"Gemini request timeout after {settings.request_timeout}s")
            raise HTTPException(504, "Quote generation timed out. Please try again.")
        except Exception as e:
            logger.error(f"Gemini error: {str(e)}")
            raise HTTPException(500, f"Quote generation failed: {str(e)}")
