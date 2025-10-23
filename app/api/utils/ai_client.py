"""
AI client for interacting with language models.
"""
from typing import Optional
import ollama
from app.config import settings


class AIClient:
    """Client for AI model interactions."""
    
    def __init__(self):
        """Initialize the AI client with Ollama."""
        self.base_url = settings.ollama_base_url
        self.model_name = settings.default_model
        # Test if Ollama is available
        try:
            ollama.list()
            self.available = True
        except Exception:
            self.available = False
    
    async def generate_quote(
        self,
        prompt: str,
        system_prompt: str,
        model: Optional[str] = None,
        max_tokens: Optional[int] = None,
        temperature: Optional[float] = None
    ) -> str:
        """
        Generate a quote using the AI model.
        
        Args:
            prompt: The user prompt
            system_prompt: The system prompt
            model: Model to use (defaults to settings.default_model)
            max_tokens: Maximum tokens to generate
            temperature: Creativity temperature (0-1)
            
        Returns:
            Generated quote text
            
        Raises:
            Exception: If Ollama is not available or generation fails
        """
        if not self.available:
            raise ValueError(
                "Ollama is not available. Please ensure Ollama is running.\n"
                "Start it with: ollama serve\n"
                "Or check if it's running: ollama list"
            )
        
        # Use defaults from settings if not provided
        model = model or self.model_name
        temperature = temperature or settings.temperature
        
        try:
            # Combine system prompt and user prompt
            full_prompt = f"{system_prompt}\n\n{prompt}"
            
            # Generate content using Ollama
            response = ollama.generate(
                model=model,
                prompt=full_prompt,
                options={
                    'temperature': temperature,
                    'num_predict': max_tokens or settings.max_tokens,
                }
            )
            
            # Extract and return the generated text
            if not response or 'response' not in response:
                raise Exception("No content generated")
            
            quote = response['response'].strip()
            
            # Remove any quotation marks that might have been added
            quote = quote.strip('"\'')
            
            return quote
            
        except Exception as e:
            error_msg = str(e)
            if "not found" in error_msg.lower() or "model" in error_msg.lower():
                raise ValueError(
                    f"Model '{model}' not found in Ollama. "
                    f"Available models: Run 'ollama list' to see installed models.\n"
                    f"To install a model: ollama pull {model}"
                )
            elif "connection" in error_msg.lower() or "refused" in error_msg.lower():
                raise Exception(
                    "Cannot connect to Ollama. Please ensure Ollama is running.\n"
                    "Start it with: ollama serve"
                )
            else:
                raise Exception(f"Error generating quote: {error_msg}")
