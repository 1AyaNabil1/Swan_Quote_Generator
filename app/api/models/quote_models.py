"""
Pydantic models for quote generation requests and responses.
"""
from pydantic import BaseModel, Field, validator
from typing import Optional, List
from enum import Enum


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
        default=QuoteCategory.RANDOM,
        description="Category of the quote to generate"
    )
    topic: Optional[str] = Field(
        default=None,
        description="Specific topic for the quote (optional)",
        max_length=100
    )
    style: Optional[str] = Field(
        default=None,
        description="Writing style (e.g., 'Shakespearean', 'modern', 'philosophical')",
        max_length=50
    )
    length: Optional[str] = Field(
        default="medium",
        description="Desired length: 'short' (10-20 words), 'medium' (20-40 words), or 'long' (40-60 words)"
    )
    temperature: Optional[float] = Field(
        default=0.8,  # Matches config for consistency
        description="Creativity temperature (0.0-1.0)",
        ge=0.0,
        le=1.0
    )
    max_tokens: Optional[int] = Field(
        default=2048,  # High default for Gemini free tier
        description="Maximum tokens to generate (100-8192)",
        ge=100,
        le=300
    )

    @validator("length")
    def validate_length(cls, v):
        valid_lengths = ["short", "medium", "long"]
        if v not in valid_lengths:
            raise ValueError(f"Length must be one of {valid_lengths}")
        return v

    class Config:
        json_schema_extra = {
            "example": {
                "category": "motivation",
                "topic": "perseverance",
                "style": "modern",
                "length": "medium",
                "temperature": 0.8,
                "max_tokens": 2048
            }
        }


class QuoteResponse(BaseModel):
    """Response model containing the generated quote."""
    quote: str = Field(..., description="The generated quote")
    author: str = Field(default="Swan", description="Author attribution")
    category: str = Field(..., description="Category of the quote")
    timestamp: str = Field(..., description="Generation timestamp")
    
    class Config:
        json_schema_extra = {
            "example": {
                "quote": "Keep pushing forward, for perseverance turns dreams into achievements.",
                "author": "Swan",
                "category": "motivation",
                "timestamp": "2025-10-27T18:30:00Z"
            }
        }


class ErrorResponse(BaseModel):
    """Error response model."""
    error: str = Field(..., description="Error message")
    detail: Optional[str] = Field(None, description="Detailed error information")


__all__ = ["QuoteRequest", "QuoteResponse", "QuoteCategory", "ErrorResponse"]
