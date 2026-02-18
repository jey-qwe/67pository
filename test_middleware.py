"""
Test script for autonomous middleware functionality.

Tests that API interactions are automatically logged to memory.
"""
import time
import httpx

API_BASE = "http://localhost:8000/api/v1"


def test_middleware_logging():
    """Test that middleware logs interactions automatically."""
    print("=" * 60)
    print("Autonomous Middleware Test")
    print("=" * 60)
    print()
    
    client = httpx.Client(timeout=10.0)
    
    # Test 1: Add a memory card
    print("---Test 1: Adding memory card ---")
    add_response = client.post(
        f"{API_BASE}/memory/add",
        json={
            "content": "Testing middleware auto-logging with Trinity",
            "tags": ["test", "middleware"],
            "source": "test_script",
            "importance": 5
        }
    )
    print(f"Status: {add_response.status_code}")
    print(f"Response: {add_response.json()}")
    print()
    
    # Test 2: Search for memories
    print("--- Test 2: Searching memories ---")
    search_response = client.post(
        f"{API_BASE}/memory/search",
        json={
            "query": "What did we test with Trinity?",
            "limit": 5
        }
    )
    print(f"Status: {search_response.status_code}")
    results = search_response.json()
    print(f"Found {results['total']} results")
    if results['results']:
        print(f"Top result: {results['results'][0]['content'][:60]}...")
    print()
    
    # Wait for background tasks to complete
    print("Waiting for background logging to complete...")
    time.sleep(2)
    
    # Test 3: Check if middleware logged the interactions
    print("--- Test 3: Checking middleware logs ---")
    all_response = client.get(f"{API_BASE}/memory/all")
    all_cards = all_response.json()
    
    # Filter for middleware-logged entries
    middleware_logs = [
        card for card in all_cards 
        if card['source'] == 'conversation_auto_log' and 'api_interaction' in card.get('tags', [])
    ]
    
    print(f"Total cards in system: {len(all_cards)}")
    print(f"Middleware-logged interactions: {len(middleware_logs)}")
    print()
    
    if middleware_logs:
        print("Middleware logged interactions:")
        for i, log in enumerate(middleware_logs, 1):
            print(f"{i}. [{log['importance']}] {log['content'][:80]}...")
            print(f"   Tags: {log['tags']}")
    else:
        print("[WARNING] No middleware logs found. Check if middleware is working.")
    
    print()
    print("=" * 60)
    print("[COMPLETE] Middleware test finished")
    print("=" * 60)
    
    client.close()


if __name__ == "__main__":
    try:
        test_middleware_logging()
    except httpx.ConnectError:
        print("[ERROR] Could not connect to server.")
        print("Make sure the server is running: python run.py")
    except Exception as e:
        print(f"[ERROR] Test failed: {e}")
        import traceback
        traceback.print_exc()
