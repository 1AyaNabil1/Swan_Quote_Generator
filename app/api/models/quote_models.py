"""
Pydantic models for quote generation requests and responses.
"""

from enum import Enum
from typing import ClassVar

from pydantic import BaseModel, Field, validator


class QuoteCategory(str, Enum):
    """Available quote categories."""

    MOTIVATION = "motivation"
    INSPIRATION = "inspiration"
    WISDOM = "wisdom"
    HUMOR = "humor"
    LOVE = "love"
    SUCCESS = "success"
    LIFE = "life"
    FRIENDSHIP = "friendship"
    HAPPINESS = "happiness"
    RANDOM = "random"


class QuoteRequest(BaseModel):
    """Request model for generating a quote."""

    category: QuoteCategory = Field(
        default=QuoteCategory.RANDOM, description="Category of the quote to generate"
    )
    topic: str | None = Field(
        default=None, description="Specific topic for the quote (optional)", max_length=100
    )
    style: str | None = Field(
        default=None,
        description="Writing style (e.g., 'Shakespearean', 'modern', 'philosophical')",
        max_length=50,
    )
    language: str | None = Field(
        default="en",
        description="Language for quote generation: 'en' (English) or 'ar' (Arabic)",
        max_length=2,
    )
    length: str | None = Field(
        default="medium",
        description="Desired length: 'short' (10-20 words), 'medium' (20-40 words), or 'long' (40-60 words)",
    )
    temperature: float | None = Field(
        default=0.8,  # Matches config for consistency
        description="Creativity temperature (0.0-1.0)",
        ge=0.0,
        le=1.0,
    )
    max_tokens: int | None = Field(
        default=2048,  # High default for Gemini free tier
        description="Maximum tokens to generate (100-8192)",
        ge=100,
        le=300,
    )

    @validator("language")
    def validate_language(cls, v):
        valid_languages = ["en", "ar"]
        if v not in valid_languages:
            raise ValueError(f"Language must be one of {valid_languages}")
        return v

    @validator("length")
    def validate_length(cls, v):
        valid_lengths = ["short", "medium", "long"]
        if v not in valid_lengths:
            raise ValueError(f"Length must be one of {valid_lengths}")
        return v

    class Config:
        json_schema_extra: ClassVar[dict] = {
            "example": {
                "category": "motivation",
                "topic": "perseverance",
                "style": "modern",
                "language": "en",
                "length": "medium",
                "temperature": 0.8,
                "max_tokens": 2048,
            }
        }


class QuoteResponse(BaseModel):
    """Response model containing the generated quote."""

    quote: str = Field(..., description="The generated quote")
    author: str = Field(default="Swan", description="Author attribution")
    category: str = Field(..., description="Category of the quote")
    timestamp: str = Field(..., description="Generation timestamp")

    class Config:
        json_schema_extra: ClassVar[dict] = {
            "example": {
                "quote": "Keep pushing forward, for perseverance turns dreams into achievements.",
                "author": "Swan",
                "category": "motivation",
                "timestamp": "2025-10-27T18:30:00Z",
            }
        }


class ErrorResponse(BaseModel):
    """Error response model."""

    error: str = Field(..., description="Error message")
    detail: str | None = Field(None, description="Detailed error information")


__all__ = ["ErrorResponse", "QuoteCategory", "QuoteRequest", "QuoteResponse"]
