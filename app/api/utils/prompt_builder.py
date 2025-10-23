"""
Utility for building AI prompts for quote generation.
"""
from typing import Optional


class PromptBuilder:
    """Builds prompts for AI quote generation."""
    
    @staticmethod
    def build_quote_prompt(
        category: str,
        topic: Optional[str] = None,
        style: Optional[str] = None,
        length: str = "medium"
    ) -> str:
        """
        Build a prompt for quote generation.
        
        Args:
            category: The category of quote to generate
            topic: Specific topic (optional)
            style: Writing style (optional)
            length: Desired length (short/medium/long)
            
        Returns:
            A formatted prompt string
        """
        # Base instruction
        prompt = f"Generate an original, inspiring quote about {category}"
        
        # Add topic if provided
        if topic:
            prompt += f", specifically focusing on {topic}"
        
        # Add style if provided
        if style:
            prompt += f" in a {style} style"
        
        # Add length guidance
        length_guidance = {
            "short": "Keep it concise (1 sentence, under 20 words)",
            "medium": "Make it thoughtful (1-2 sentences, 20-40 words)",
            "long": "Make it elaborate (2-3 sentences, 40-60 words)"
        }
        prompt += f". {length_guidance.get(length, length_guidance['medium'])}."
        
        # Final instructions
        prompt += "\n\nProvide ONLY the quote itself, without any attribution, quotation marks, or additional commentary."
        
        return prompt
    
    @staticmethod
    def build_system_prompt() -> str:
        """
        Build the system prompt for the AI model.
        
        Returns:
            System prompt string
        """
        return (
            "You are a creative quote generator. Your task is to create original, "
            "meaningful, and inspiring quotes based on the given category and specifications. "
            "The quotes should be memorable, thought-provoking, and authentic. "
            "Never use existing famous quotes - always create new, original content."
        )
