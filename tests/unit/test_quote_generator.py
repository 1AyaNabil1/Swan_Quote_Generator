"""
Basic unit tests for the AI Quote Generator.
Run with: pytest tests/unit/
"""
import pytest
from app.api.models import QuoteRequest, QuoteResponse, QuoteCategory
from app.api.utils import PromptBuilder


class TestQuoteModels:
    """Test Pydantic models."""
    
    def test_quote_request_creation(self):
        """Test creating a QuoteRequest."""
        request = QuoteRequest(
            category=QuoteCategory.MOTIVATION,
            topic="success",
            style="modern",
            length="medium"
        )
        assert request.category == QuoteCategory.MOTIVATION
        assert request.topic == "success"
        assert request.style == "modern"
        assert request.length == "medium"
    
    def test_quote_request_defaults(self):
        """Test QuoteRequest default values."""
        request = QuoteRequest()
        assert request.category == QuoteCategory.RANDOM
        assert request.topic is None
        assert request.style is None
        assert request.length == "medium"
    
    def test_quote_response_creation(self):
        """Test creating a QuoteResponse."""
        response = QuoteResponse(
            quote="Test quote",
            author="Ayō",
            category="motivation",
            timestamp="2025-10-23T10:30:00Z"
        )
        assert response.quote == "Test quote"
        assert response.author == "Ayō"
        assert response.category == "motivation"


class TestPromptBuilder:
    """Test PromptBuilder utility."""
    
    def test_build_quote_prompt_basic(self):
        """Test basic prompt building."""
        prompt = PromptBuilder.build_quote_prompt(
            category="motivation"
        )
        assert "motivation" in prompt
        assert "Generate" in prompt
    
    def test_build_quote_prompt_with_topic(self):
        """Test prompt building with topic."""
        prompt = PromptBuilder.build_quote_prompt(
            category="motivation",
            topic="perseverance"
        )
        assert "motivation" in prompt
        assert "perseverance" in prompt
    
    def test_build_quote_prompt_with_style(self):
        """Test prompt building with style."""
        prompt = PromptBuilder.build_quote_prompt(
            category="wisdom",
            style="philosophical"
        )
        assert "wisdom" in prompt
        assert "philosophical" in prompt
    
    def test_build_quote_prompt_length_short(self):
        """Test prompt building with short length."""
        prompt = PromptBuilder.build_quote_prompt(
            category="inspiration",
            length="short"
        )
        assert "concise" in prompt or "short" in prompt
    
    def test_build_system_prompt(self):
        """Test system prompt generation."""
        system_prompt = PromptBuilder.build_system_prompt()
        assert "quote" in system_prompt.lower()
        assert "original" in system_prompt.lower()


class TestQuoteCategories:
    """Test quote categories."""
    
    def test_all_categories_exist(self):
        """Test that all expected categories exist."""
        expected_categories = [
            "motivation", "inspiration", "wisdom", "humor",
            "love", "success", "life", "friendship", "happiness", "random"
        ]
        for cat in expected_categories:
            assert hasattr(QuoteCategory, cat.upper())
    
    def test_category_values(self):
        """Test category enum values."""
        assert QuoteCategory.MOTIVATION.value == "motivation"
        assert QuoteCategory.INSPIRATION.value == "inspiration"
        assert QuoteCategory.WISDOM.value == "wisdom"
