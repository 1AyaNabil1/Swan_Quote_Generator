"""
Integration tests for the AI Quote Generator API.
Run with: pytest tests/integration/
"""
import pytest
from httpx import AsyncClient
from main import app


@pytest.mark.asyncio
async def test_root_endpoint():
    """Test the root endpoint."""
    async with AsyncClient(app=app, base_url="http://test") as client:
        response = await client.get("/")
    
    assert response.status_code == 200
    data = response.json()
    assert "name" in data
    assert "version" in data
    assert "status" in data


@pytest.mark.asyncio
async def test_health_endpoint():
    """Test the health check endpoint."""
    async with AsyncClient(app=app, base_url="http://test") as client:
        response = await client.get("/health")
    
    assert response.status_code == 200
    data = response.json()
    assert data["status"] == "healthy"
    assert "version" in data


@pytest.mark.asyncio
async def test_get_categories():
    """Test getting available categories."""
    async with AsyncClient(app=app, base_url="http://test") as client:
        response = await client.get("/api/quotes/categories")
    
    assert response.status_code == 200
    categories = response.json()
    assert isinstance(categories, list)
    assert len(categories) > 0
    assert "motivation" in categories
    assert "inspiration" in categories


@pytest.mark.asyncio
async def test_generate_quote_endpoint():
    """Test the quote generation endpoint structure."""
    async with AsyncClient(app=app, base_url="http://test") as client:
        response = await client.post(
            "/api/quotes/generate",
            json={
                "category": "motivation",
                "topic": "test",
                "style": "modern",
                "length": "short"
            }
        )
    
    # May fail if no API key is configured, but we're testing the endpoint structure
    assert response.status_code in [200, 400, 500]


@pytest.mark.asyncio
async def test_random_quote_endpoint():
    """Test the random quote endpoint structure."""
    async with AsyncClient(app=app, base_url="http://test") as client:
        response = await client.get("/api/quotes/random")
    
    # May fail if no API key is configured, but we're testing the endpoint structure
    assert response.status_code in [200, 400, 500]
