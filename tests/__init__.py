"""
Test configuration and fixtures.
"""
import pytest


@pytest.fixture
def sample_quote_request():
    """Sample quote request for testing."""
    return {
        "category": "motivation",
        "topic": "success",
        "style": "modern",
        "length": "medium"
    }


@pytest.fixture
def sample_quote_response():
    """Sample quote response for testing."""
    return {
        "quote": "Success is the result of preparation and opportunity.",
        "author": "Ayō",
        "category": "motivation",
        "timestamp": "2025-10-23T10:30:00Z"
    }
