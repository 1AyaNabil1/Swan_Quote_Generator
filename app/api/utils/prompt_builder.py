"""
Utility for building AI prompts for quote generation.
"""

import logging
from typing import ClassVar

from app.api.models import QuoteCategory
from app.config import settings


logger = logging.getLogger(__name__)


class PromptBuilder:
    """Builds optimized prompts for AI quote generation"""

    # Mapping of styles to specific tone instructions
    STYLE_GUIDANCE: ClassVar[dict[str, str]] = {
        "shakespearean": "Use Elizabethan English with poetic and dramatic flair, as in Shakespeare's works.",
        "modern": "Use clear, contemporary language suitable for today's audience.",
        "philosophical": "Use deep, reflective language inspired by philosophers like Plato or Nietzsche.",
        "poetic": "Use vivid imagery and rhythmic language, like a modern poet.",
        "witty": "Use clever, humorous language with a sharp, playful tone.",
    }

    # Category-specific instructions to guide quote tone
    CATEGORY_GUIDANCE: ClassVar[dict[str, str]] = {
        QuoteCategory.MOTIVATION.value: "Create an uplifting quote to inspire action and determination.",
        QuoteCategory.INSPIRATION.value: "Craft a quote that sparks creativity and hope.",
        QuoteCategory.WISDOM.value: "Generate a profound quote about life or knowledge.",
        QuoteCategory.HUMOR.value: "Produce a witty, lighthearted quote to evoke laughter.",
        QuoteCategory.LOVE.value: "Create a heartfelt quote about love and connection.",
        QuoteCategory.SUCCESS.value: "Craft a quote that celebrates achievement and ambition.",
        QuoteCategory.LIFE.value: "Generate a reflective quote about the human experience.",
        QuoteCategory.FRIENDSHIP.value: "Produce a warm quote about camaraderie and loyalty.",
        QuoteCategory.HAPPINESS.value: "Create a joyful quote that promotes positivity.",
        QuoteCategory.RANDOM.value: "Generate a creative quote on any theme, ensuring originality.",
    }

    # Example quotes for each category
    EXAMPLE_QUOTES: ClassVar[dict[str, str]] = {
        QuoteCategory.MOTIVATION.value: "Perseverance turns dreams into reality with every bold step.",
        QuoteCategory.INSPIRATION.value: "Dreams soar like stars guiding you through darkness.",
        QuoteCategory.WISDOM.value: "Wisdom is knowing the limits of one's own knowledge.",
        QuoteCategory.HUMOR.value: "Life's too short to match every sock.",
        QuoteCategory.LOVE.value: "Love is the melody that warms every heart.",
        QuoteCategory.SUCCESS.value: "Success is courage taking the next step.",
        QuoteCategory.LIFE.value: "Life is a canvas painted with bold choices.",
        QuoteCategory.FRIENDSHIP.value: "Friends are anchors in life's stormy seas.",
        QuoteCategory.HAPPINESS.value: "Happiness grows where kindness is sown.",
        QuoteCategory.RANDOM.value: "Embrace the unknown for its hidden wonders.",
    }

    @staticmethod
    def validate_style(style: str | None) -> str:
        """
        Validate and normalize the style input.

        Args:
            style (Optional[str]): The requested style (e.g., 'shakespearean', 'modern').

        Returns:
            str: The validated style, defaulting to 'modern' if invalid or None.

        Example:
            >>> PromptBuilder.validate_style("Shakespearean")
            'shakespearean'
        """
        if not style:
            return "modern"
        style = style.lower()
        if style not in PromptBuilder.STYLE_GUIDANCE:
            logger.warning(f"Unknown style: {style}. Defaulting to 'modern'.")
            return "modern"
        return style

    @staticmethod
    def build_quote_prompt(
        category: str,
        topic: str | None = None,
        style: str | None = None,
        length: str = "medium",
        language: str = "en",
    ) -> str:
        """
        Build a prompt for quote generation optimized.

        Args:
            category (str): The category of quote (e.g., 'motivation', 'inspiration').
            topic (Optional[str]): Specific topic for the quote (e.g., 'perseverance').
            style (Optional[str]): Writing style (e.g., 'shakespearean', 'modern').
            length (str): Desired length ('short', 'medium', 'long').
            language (str): Language for the quote ('en' for English, 'ar' for Arabic).

        Returns:
            str: A formatted prompt string optimized.

        Raises:
            ValueError: If length is invalid.

        Example:
            >>> builder = PromptBuilder()
            >>> builder.build_quote_prompt(
            ...     category="motivation",
            ...     topic="perseverance",
            ...     style="modern",
            ...     length="medium"
            ... )
            'Create a motivation quote about "perseverance" in about 25 words. Use clear, contemporary language suitable for today\'s audience. Write ONLY in English. Output only the quote text.'
        """
        # Validate inputs
        if category not in [c.value for c in QuoteCategory]:
            logger.warning(f"Invalid category: {category}. Defaulting to 'random'.")
            category = QuoteCategory.RANDOM.value
        if length not in ["short", "medium", "long"]:
            logger.error(f"Invalid length: {length}")
            raise ValueError("Length must be 'short', 'medium', or 'long'")

        # Log input parameters if debug mode is enabled
        if settings.debug:
            logger.debug(
                f"Building prompt with category={category}, topic={topic}, style={style}, length={length}, language={language}"
            )

        # Keep the prompt short. Topic and style are user text, so they are quoted and
        # the system instruction tells Gemini to treat them as subject matter only.
        prompt = f"Create a {category} quote"

        if topic:
            prompt += f' about "{topic}"'

        # Word count only
        word_count = "15" if length == "short" else "25" if length == "medium" else "45"
        prompt += f" in about {word_count} words."

        if style:
            known = style.lower()
            if known in PromptBuilder.STYLE_GUIDANCE:
                prompt += f" {PromptBuilder.STYLE_GUIDANCE[known]}"
            else:
                prompt += f' Write it in this style: "{style}".'

        # Add language specification with clear instructions
        if language == "ar":
            prompt += " Write ONLY in Arabic. Do not include English translation or explanations. Output only the Arabic quote text."
        else:
            prompt += " Write ONLY in English. Output only the quote text."

        if settings.debug:
            logger.debug(f"Generated prompt: {prompt}")
        return prompt
