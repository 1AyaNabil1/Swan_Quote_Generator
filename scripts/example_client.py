"""
Example client script for the AI Quote Generator API.
Demonstrates how to interact with the API endpoints.
"""
import requests
import json
from typing import Optional


class QuoteClient:
    """Client for interacting with the AI Quote Generator API."""
    
    def __init__(self, base_url: str = "http://localhost:8000"):
        """
        Initialize the client.
        
        Args:
            base_url: Base URL of the API
        """
        self.base_url = base_url.rstrip('/')
    
    def get_random_quote(self) -> dict:
        """
        Get a random quote.
        
        Returns:
            Quote response dictionary
        """
        response = requests.get(f"{self.base_url}/api/quotes/random")
        response.raise_for_status()
        return response.json()
    
    def generate_quote(
        self,
        category: str = "motivation",
        topic: Optional[str] = None,
        style: Optional[str] = None,
        length: str = "medium"
    ) -> dict:
        """
        Generate a custom quote.
        
        Args:
            category: Category of the quote
            topic: Specific topic (optional)
            style: Writing style (optional)
            length: Length ('short', 'medium', or 'long')
            
        Returns:
            Quote response dictionary
        """
        payload = {
            "category": category,
            "length": length
        }
        if topic:
            payload["topic"] = topic
        if style:
            payload["style"] = style
        
        response = requests.post(
            f"{self.base_url}/api/quotes/generate",
            json=payload
        )
        response.raise_for_status()
        return response.json()
    
    def get_categories(self) -> list:
        """
        Get available quote categories.
        
        Returns:
            List of category strings
        """
        response = requests.get(f"{self.base_url}/api/quotes/categories")
        response.raise_for_status()
        return response.json()
    
    def check_health(self) -> dict:
        """
        Check API health.
        
        Returns:
            Health status dictionary
        """
        response = requests.get(f"{self.base_url}/health")
        response.raise_for_status()
        return response.json()


def print_quote(quote_data: dict):
    """Pretty print a quote."""
    print("\n" + "="*60)
    print(f"📝 {quote_data['quote']}")
    print(f"\n   — {quote_data['author']}")
    print(f"   Category: {quote_data['category']}")
    print(f"   Generated: {quote_data['timestamp']}")
    print("="*60 + "\n")


def main():
    """Main example function."""
    # Initialize client
    client = QuoteClient()
    
    print("🎯 AI Quote Generator - Example Client\n")
    
    # Check API health
    try:
        health = client.check_health()
        print(f"✅ API Status: {health['status']}")
        print(f"   Version: {health['version']}\n")
    except Exception as e:
        print(f"❌ Error connecting to API: {e}")
        print("   Make sure the server is running at http://localhost:8000")
        return
    
    # Get available categories
    print("📚 Available Categories:")
    try:
        categories = client.get_categories()
        print(f"   {', '.join(categories)}\n")
    except Exception as e:
        print(f"❌ Error getting categories: {e}\n")
    
    # Example 1: Get a random quote
    print("Example 1: Random Quote")
    try:
        quote = client.get_random_quote()
        print_quote(quote)
    except Exception as e:
        print(f"❌ Error: {e}\n")
    
    # Example 2: Generate a motivational quote
    print("Example 2: Motivational Quote about Success")
    try:
        quote = client.generate_quote(
            category="motivation",
            topic="success",
            style="modern",
            length="medium"
        )
        print_quote(quote)
    except Exception as e:
        print(f"❌ Error: {e}\n")
    
    # Example 3: Generate a short wisdom quote
    print("Example 3: Short Wisdom Quote")
    try:
        quote = client.generate_quote(
            category="wisdom",
            length="short"
        )
        print_quote(quote)
    except Exception as e:
        print(f"❌ Error: {e}\n")
    
    # Example 4: Generate a philosophical quote about life
    print("Example 4: Philosophical Quote about Life")
    try:
        quote = client.generate_quote(
            category="life",
            topic="happiness",
            style="philosophical",
            length="long"
        )
        print_quote(quote)
    except Exception as e:
        print(f"❌ Error: {e}\n")


if __name__ == "__main__":
    main()
