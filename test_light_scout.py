"""
Test Light Scout - Multimodal News Agent
"""

import asyncio
import sys
import os

# Add to path
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

# Now import
from src.agents.light_scout import LightScout
from src.notifications import GOOGLE_API_KEY, LIGHT_SCOUT_WEBHOOK_URL
import json


async def main():
    """Test Light Scout"""
    print("[Test] Starting Light Scout...")
    
    # Load sources
    with open('data/sources.json', 'r') as f:
        sources = json.load(f)
    
    print(f"[Test] Loaded {len(sources)} sources")
    print(f"[Test] Gemini API Key: {GOOGLE_API_KEY[:20]}...")
    print(f"[Test] Webhook configured: {bool(LIGHT_SCOUT_WEBHOOK_URL)}")
    
    # Initialize Light Scout
    scout = LightScout(
        gemini_api_key=GOOGLE_API_KEY,
        webhook_url=LIGHT_SCOUT_WEBHOOK_URL
    )
    
    # Run
    await scout.run(sources)
    
    print("[Test] Light Scout completed!")


if __name__ == "__main__":
    asyncio.run(main())
