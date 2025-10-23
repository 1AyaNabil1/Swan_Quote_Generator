#!/usr/bin/env python3
"""
Quick test script to verify Ollama integration.
Run this to test your setup without starting the full server.
"""
import asyncio
import sys
from app.api.utils import AIClient, PromptBuilder


async def test_ollama():
    """Test the Ollama integration."""
    print("🧪 Testing Ollama Integration\n")
    
    # Initialize components
    try:
        client = AIClient()
        builder = PromptBuilder()
        
        if not client.available:
            print("❌ ERROR: Ollama is not available!")
            print("   Please ensure Ollama is running")
            print("   Start it with: ollama serve")
            print("   Or check: ollama list")
            return False
        
        print("✅ Ollama client initialized")
        print(f"   Model: {client.model_name}")
        print(f"   Base URL: {client.base_url}\n")
        
        # Build test prompt
        system_prompt = builder.build_system_prompt()
        user_prompt = builder.build_quote_prompt(
            category="motivation",
            topic="success",
            length="short"
        )
        
        print("📝 Generating test quote...")
        print(f"   Category: motivation")
        print(f"   Topic: success")
        print(f"   Length: short\n")
        
        # Generate quote
        quote = await client.generate_quote(
            prompt=user_prompt,
            system_prompt=system_prompt
        )
        
        print("✅ SUCCESS! Quote generated:\n")
        print("─" * 60)
        print(f"  {quote}")
        print("─" * 60)
        print("\n🎉 Your Ollama integration is working perfectly!")
        print("   ✅ 100% Free - runs locally on your MacBook")
        print("   ✅ No API keys needed")
        print("   ✅ No rate limits")
        print("\n   You can now start the server with: python3 main.py")
        print("   Or visit: http://localhost:8000/docs\n")
        
        return True
        
    except ValueError as e:
        print(f"❌ Configuration Error: {e}")
        return False
    except Exception as e:
        print(f"❌ Error: {e}")
        return False


if __name__ == "__main__":
    try:
        result = asyncio.run(test_ollama())
        sys.exit(0 if result else 1)
    except KeyboardInterrupt:
        print("\n\n⚠️  Test interrupted by user")
        sys.exit(1)
