"""
Pydantic models for quote generation requests and responses.
"""

from enum import StrEnum
from typing import Literal

from pydantic import BaseModel, ConfigDict, Field


class QuoteCategory(StrEnum):
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

    model_config = ConfigDict(
        json_schema_extra={
            "example": {
                "category": "motivation",
                "topic": "perseverance",
                "style": "modern",
                "language": "en",
                "length": "medium",
                "temperature": 0.8,
            }
        }
    )

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
    language: Literal["en", "ar"] = Field(
        default="en", description="Language for quote generation: 'en' (English) or 'ar' (Arabic)"
    )
    length: Literal["short", "medium", "long"] = Field(
        default="medium",
        description="Desired length: 'short' (about 15 words), 'medium' (about 25), or 'long' (about 45)",
    )
    temperature: float | None = Field(
        default=None,
        description="Creativity temperature (0.0-1.0); the server default when omitted",
        ge=0.0,
        le=1.0,
    )
    max_tokens: int | None = Field(
        default=None,
        description="Maximum output tokens (100-300); the server default when omitted",
        ge=100,
        le=300,
    )


class QuoteResponse(BaseModel):
    """Response model containing the generated quote."""

    model_config = ConfigDict(
        json_schema_extra={
            "example": {
                "quote": "Keep pushing forward, for perseverance turns dreams into achievements.",
                "author": "Swan",
                "category": "motivation",
                "timestamp": "2025-10-27T18:30:00Z",
            }
        }
    )

    quote: str = Field(..., description="The generated quote")
    author: str = Field(default="Swan", description="Author attribution")
    category: str = Field(..., description="Category of the quote")
    timestamp: str = Field(..., description="Generation timestamp")


class ErrorResponse(BaseModel):
    """Error response model."""

    detail: str = Field(..., description="Error message, safe to show to the user")


__all__ = ["ErrorResponse", "QuoteCategory", "QuoteRequest", "QuoteResponse"]
