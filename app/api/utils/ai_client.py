"""
AI client for quote generation using Google Gemini API.
"""
from typing import Optional
import logging
from app.config import settings
from fastapi import HTTPException

logger = logging.getLogger(__name__)

class AIClient:
    """Client for AI text generation using Google Gemini."""
    
    def __init__(self):
        """Initialize Google Gemini client."""
        self.model_name = settings.default_model
        self.available = False
        self._init_gemini()
        
        if not self.available:
            raise RuntimeError("Failed to initialize Google Gemini. Check configuration and logs.")

    def _init_gemini(self) -> None:
        """Initialize Google Gemini client."""
        try:
            import google.generativeai as genai
            
            if not settings.gemini_api_key:
                logger.error("GEMINI_API_KEY not found in settings. Set it in .env")
                return
            
            # Configure Gemini with API key
            genai.configure(api_key=settings.gemini_api_key)
            
            # Initialize Gemini model
            # Note: system_instruction requires SDK v0.4.0+, so we'll add it to user prompts instead
            self.gemini_model = genai.GenerativeModel(self.model_name)
            
            logger.info(f"Google Gemini initialized successfully with model: {self.model_name}")
            self.available = True
            
        except ImportError:
            logger.error("google-generativeai not installed. Run: pip install google-generativeai")
        except Exception as e:
            logger.error(f"Failed to initialize Gemini: {str(e)}")

    async def generate_quote(
        self,
        prompt: str,
        system_prompt: str,
        model: Optional[str] = None,
        max_tokens: Optional[int] = None,
        temperature: Optional[float] = None
    ) -> str:
        """
        Generate a quote using Google Gemini API.

        Args:
            prompt: The user prompt
            system_prompt: The system prompt (instructions/context)
            model: Model to use (optional, uses default if not specified)
            max_tokens: Maximum tokens to generate
            temperature: Creativity temperature (0.0-1.0)

        Returns:
            Generated quote text (cleaned, without surrounding quotes)

        Raises:
            HTTPException: If generation fails or backend is unavailable
        """
        if not self.available:
            raise HTTPException(
                status_code=503,
                detail="Gemini API is not available. Check server logs and configuration."
            )

        # Use defaults from settings if not provided
        temperature = temperature if temperature is not None else settings.temperature
        max_tokens = max_tokens or settings.max_tokens
        full_prompt = prompt  # Don't combine with system_prompt for Gemini

        try:
            return await self._generate_with_gemini(full_prompt, temperature, max_tokens)
                
        except HTTPException:
            raise  # Re-raise HTTP exceptions as-is
        except Exception as e:
            logger.error(f"Unexpected error during quote generation: {str(e)}")
            raise HTTPException(
                status_code=500,
                detail=f"Failed to generate quote: {str(e)}"
            )

    async def _generate_with_gemini(
        self,
        prompt: str,
        temperature: float,
        max_tokens: int
    ) -> str:
        try:
            import google.generativeai as genai

            logger.debug(f"=== GEMINI REQUEST ===")
            logger.debug(f"Prompt: {prompt}")
            logger.debug(f"Temp: {temperature}, Max tokens: {max_tokens}")

            # Generation configuration
            generation_config = genai.types.GenerationConfig(
                temperature=temperature,
                max_output_tokens=max_tokens,
                top_p=0.95,
                top_k=40,
            )

            # Disable all safety filters for quote generation
            safety_settings = [
                {"category": k, "threshold": "BLOCK_NONE"} for k in [
                    "HARM_CATEGORY_DANGEROUS_CONTENT",
                    "HARM_CATEGORY_HARASSMENT",
                    "HARM_CATEGORY_HATE_SPEECH",
                    "HARM_CATEGORY_SEXUALLY_EXPLICIT",
                ]
            ]

            # Generate content
            response = await self.gemini_model.generate_content_async(
                prompt,
                generation_config=generation_config,
                safety_settings=safety_settings
            )

            logger.debug(f"=== GEMINI RESPONSE ===")
            logger.debug(f"Response type: {type(response)}")
            logger.debug(f"Has candidates: {hasattr(response, 'candidates')}")
            
            # Check if response has candidates
            if not hasattr(response, 'candidates') or not response.candidates:
                logger.error("No candidates in response")
                logger.debug(f"Full response: {response}")
                raise ValueError("Gemini returned no candidates - content may be blocked")

            candidate = response.candidates[0]
            logger.debug(f"Candidate: {candidate}")
            logger.debug(f"Finish reason: {candidate.finish_reason}")
            
            # Check finish reason
            finish_reason = candidate.finish_reason
            
            if finish_reason == 3:  # SAFETY
                logger.error("Content blocked by safety filters")
                if hasattr(candidate, 'safety_ratings'):
                    logger.error(f"Safety ratings: {candidate.safety_ratings}")
                raise ValueError("Content blocked by safety filters")
            
            if finish_reason == 4:  # RECITATION
                logger.error("Content blocked for recitation/copyright")
                raise ValueError("Content blocked for copyright concerns")
            
            if finish_reason == 2:  # MAX_TOKENS
                logger.warning(f"MAX_TOKENS reached ({max_tokens}) - output may be truncated")
            if finish_reason not in [1, 2]:  # Not STOP or MAX_TOKENS
                logger.error(f"Unexpected finish_reason: {finish_reason}")
                raise ValueError(f"Generation failed with reason code: {finish_reason}")
            
            # === BULLETPROOF TEXT EXTRACTION ===
            quote = ""
            
            # METHOD 1: Try response.text (simplest)
            try:
                quote = response.text
                if quote:
                    quote = quote.strip()
                    logger.debug(f"✓ Method 1 (response.text): '{quote[:80]}...'")
            except (ValueError, AttributeError) as e:
                logger.debug(f"✗ Method 1 failed: {e}")
            
            # METHOD 2: Extract from candidate.content.parts
            if not quote:
                logger.debug("Trying Method 2 (candidate.content.parts)...")
                try:
                    if hasattr(candidate, 'content'):
                        content = candidate.content
                        logger.debug(f"Content object: {content}")
                        
                        if hasattr(content, 'parts'):
                            parts = content.parts
                            logger.debug(f"Parts count: {len(list(parts))}")
                            
                            text_parts = []
                            for i, part in enumerate(parts):
                                logger.debug(f"Part {i}: {part}")
                                if hasattr(part, 'text'):
                                    part_text = part.text
                                    if part_text:
                                        text_parts.append(part_text)
                                        logger.debug(f"  Part {i} text: '{part_text[:50]}...'")
                            
                            if text_parts:
                                quote = " ".join(text_parts).strip()
                                logger.debug(f"✓ Method 2: Extracted {len(text_parts)} parts")
                            else:
                                logger.warning("Parts exist but no text found in any part")
                        else:
                            logger.warning("Content has no 'parts' attribute")
                    else:
                        logger.warning("Candidate has no 'content' attribute")
                except Exception as e2:
                    logger.error(f"✗ Method 2 failed: {e2}", exc_info=True)
            
            # METHOD 3: Check response.candidates[0].text directly
            if not quote:
                logger.debug("Trying Method 3 (candidate.text)...")
                try:
                    if hasattr(candidate, 'text'):
                        quote = candidate.text
                        if quote:
                            quote = quote.strip()
                            logger.debug(f"✓ Method 3 (candidate.text): '{quote[:80]}...'")
                except Exception as e3:
                    logger.debug(f"✗ Method 3 failed: {e3}")
            
            # Final check
            if not quote:
                logger.error("=== ALL EXTRACTION METHODS FAILED ===")
                logger.error(f"Response structure: {dir(response)}")
                logger.error(f"Candidate structure: {dir(candidate)}")
                if hasattr(candidate, 'content'):
                    logger.error(f"Content structure: {dir(candidate.content)}")
                
                # If finish_reason is MAX_TOKENS but no content, it's actually blocked
                if finish_reason == 2:
                    raise ValueError(
                        "Gemini returned MAX_TOKENS with empty content - likely blocked by safety filter. "
                        "Try a different prompt or category."
                    )
                else:
                    raise ValueError(
                        f"Could not extract text from Gemini response. "
                        f"Finish reason: {finish_reason}. "
                        f"This may indicate content blocking or API issues."
                    )
            
            # Clean up the quote
            quote = quote.strip()
            quote = quote.strip('"\'')  # Remove surrounding quotes
            quote = quote.strip()  # Trim again after quote removal
            
            if not quote:
                raise ValueError("Quote is empty after cleanup")
            
            logger.info(f"✓ Successfully generated quote ({len(quote)} chars): {quote[:100]}...")
            return quote

        except ImportError:
            raise HTTPException(
                status_code=503,
                detail="Gemini SDK not installed. Run: pip install google-generativeai"
            )
        except HTTPException:
            raise  # Re-raise HTTP exceptions as-is
        except ValueError as e:
            # Convert ValueError to HTTPException
            raise HTTPException(status_code=500, detail=str(e))
        except Exception as e:
            logger.error(f"Unexpected Gemini error: {str(e)}", exc_info=True)
            raise HTTPException(status_code=500, detail=f"Gemini API error: {str(e)}")