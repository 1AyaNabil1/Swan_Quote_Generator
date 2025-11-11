"""
AI client for quote generation using Google Gemini API.
Optimized for Vercel serverless deployment with fast response times.
"""

import asyncio
import logging

import google.generativeai as genai
from fastapi import HTTPException

from app.config import settings


logger = logging.getLogger(__name__)


class AIClient:
    """Client for AI text generation using Google Gemini."""

    def __init__(self):
        """Initialize Google Gemini client."""
        if not settings.gemini_api_key:
            raise RuntimeError("GEMINI_API_KEY not set. Configure in Vercel environment variables.")

        genai.configure(api_key=settings.gemini_api_key)
        # Initialize model with system instruction
        self.model = genai.GenerativeModel(
            settings.default_model,
            system_instruction="You are Swan, a quote generator. Generate one original quote only. Do not include meta-commentary, explanations, translations, or any additional text. Output only the requested quote text in the specified language.",
        )
        self.available = True
        logger.info(f"✓ Gemini initialized: {settings.default_model}")

    async def generate_quote(
        self, prompt: str, max_tokens: int | None = None, temperature: float | None = None
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
                    },
                ),
                timeout=settings.request_timeout,
            )

            # Robust extraction - handle both simple and complex responses
            try:
                # Try simple text accessor first
                quote = response.text.strip().strip("\"'")
            except (ValueError, AttributeError):
                # Fallback: extract from parts if simple text fails
                if response.candidates and response.candidates[0].content.parts:
                    quote = response.candidates[0].content.parts[0].text.strip().strip("\"'")
                else:
                    raise ValueError("No valid quote content in response") from None

            # Clean up unwanted meta-commentary and formatting
            quote = self._clean_quote_response(quote)

            return quote if quote else "Unable to generate quote. Please try again."

        except TimeoutError as e:
            logger.error(f"Gemini request timeout after {settings.request_timeout}s")
            raise HTTPException(504, "Quote generation timed out. Please try again.") from e
        except Exception as e:
            logger.error(f"Gemini error: {e!s}")
            raise HTTPException(500, f"Quote generation failed: {e!s}") from e

    def _clean_quote_response(self, text: str) -> str:
        """
        Clean the AI response to extract only the quote text.

        Removes meta-commentary, markdown formatting, and unwanted prefixes.

        Args:
            text: Raw response from AI

        Returns:
            Cleaned quote text
        """
        # Remove common meta-commentary prefixes
        unwanted_prefixes = [
            "As a large language model,",
            "As an AI,",
            "Here is your quote:",
            "Here's a quote:",
            "**Arabic:**",
            "**English:**",
            "**English Translation:**",
        ]

        for prefix in unwanted_prefixes:
            if text.startswith(prefix):
                # Remove everything up to and including the prefix
                text = text[len(prefix) :].strip()

        # If there are multiple sections (like Arabic + English), take only the first
        if "**English Translation:**" in text:
            text = text.split("**English Translation:**")[0].strip()

        # Remove markdown bold formatting
        text = text.replace("**Arabic:**", "").replace("**English:**", "")

        # Clean up any remaining markdown
        text = text.strip("*").strip()

        return text
