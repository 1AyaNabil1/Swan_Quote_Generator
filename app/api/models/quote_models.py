"""
Pydantic models for quote generation requests and responses.
"""
from pydantic import BaseModel, Field
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
        description="Writing style (e.g., 'Shakespeare', 'modern', 'philosophical')",
        max_length=50
    )
    length: Optional[str] = Field(
        default="medium",
        description="Desired length: 'short', 'medium', or 'long'"
    )
    
    class Config:
        json_schema_extra = {
            "example": {
                "category": "motivation",
                "topic": "perseverance",
                "style": "modern",
                "length": "medium"
            }
        }


class QuoteResponse(BaseModel):
    """Response model containing the generated quote."""
    quote: str = Field(..., description="The generated quote")
    author: str = Field(default="Ayō", description="Author attribution")
    category: str = Field(..., description="Category of the quote")
    timestamp: str = Field(..., description="Generation timestamp")
    
    class Config:
        json_schema_extra = {
            "example": {
                "quote": "Success is not final, failure is not fatal: it is the courage to continue that counts.",
                "author": "Ayō",
                "category": "motivation",
                "timestamp": "2025-10-23T10:30:00Z"
            }
        }


class ErrorResponse(BaseModel):
    """Error response model."""
    error: str = Field(..., description="Error message")
    detail: Optional[str] = Field(None, description="Detailed error information")


__all__ = ["QuoteRequest", "QuoteResponse", "QuoteCategory", "ErrorResponse"]
