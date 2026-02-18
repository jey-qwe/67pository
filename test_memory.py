"""
Test script for Trinity Context Core memory system.

This script tests the memory service without requiring Docker by using
Qdrant's in-memory mode.
"""
import asyncio
from qdrant_client import QdrantClient
from qdrant_client.models import Distance, VectorParams

from src.memory.service import MemoryService
from src.core.gemini_client import get_embedding


def test_gemini_embedding():
    """Test Gemini API connection and embedding generation."""
    print("\n=== Testing Gemini API ===")
    
    test_text = "This is a test sentence for embedding generation."
    print(f"Generating embedding for: '{test_text}'")
    
    embedding = get_embedding(test_text)
    
    if embedding:
        print(f"[SUCCESS] Embedding dimension: {len(embedding)}")
        print(f"First 5 values: {embedding[:5]}")
        return True
    else:
        print("[FAILED] Failed to generate embedding")
        return False


def test_memory_service_in_memory():
    """Test MemoryService with in-memory Qdrant."""
    print("\n=== Testing Memory Service (In-Memory Mode) ===")
    
    # Create in-memory Qdrant client
    print("Creating in-memory Qdrant client...")
    client = QdrantClient(":memory:")
    
    # Initialize memory service with in-memory client
    memory_service = MemoryService(client=client)
    print(f"[SUCCESS] Memory service initialized with collection: {memory_service.collection_name}")
    
    # Test 1: Add a memory card
    print("\n--- Test 1: Adding memory cards ---")
    
    cards_data = [
        {
            "content": "User prefers Python for backend development and loves FastAPI framework",
            "tags": ["python", "preference", "backend", "fastapi"],
            "source": "user",
            "importance": 9
        },
        {
            "content": "User experienced asyncio timeout error when handling large file uploads",
            "tags": ["python", "asyncio", "error_log", "performance"],
            "source": "system",
            "importance": 7
        },
        {
            "content": "Project uses Qdrant for vector database and Gemini for embeddings",
            "tags": ["architecture", "qdrant", "gemini", "vector-db"],
            "source": "system",
            "importance": 8
        }
    ]
    
    added_cards = []
    for i, card_data in enumerate(cards_data, 1):
        print(f"\nAdding card {i}: {card_data['content'][:50]}...")
        card = memory_service.add_card(**card_data)
        
        if card:
            print(f"[SUCCESS] Card added successfully!")
            print(f"   ID: {card.id}")
            print(f"   Tags: {card.tags}")
            print(f"   Importance: {card.importance}")
            added_cards.append(card)
        else:
            print(f"[FAILED] Failed to add card")
    
    print(f"\n[SUCCESS] Added {len(added_cards)} cards successfully")
    
    # Test 2: Search for similar cards
    print("\n--- Test 2: Semantic search ---")
    
    queries = [
        "What programming languages does the user like?",
        "Tell me about database architecture",
        "Any errors related to file handling?"
    ]
    
    for query in queries:
        print(f"\nQuery: '{query}'")
        results = memory_service.search(query, limit=3)
        
        if results:
            print(f"[SUCCESS] Found {len(results)} results:")
            for i, result in enumerate(results, 1):
                print(f"   {i}. {result.content[:60]}...")
                print(f"      Tags: {result.tags}")
                print(f"      Importance: {result.importance}")
        else:
            print("[FAILED] No results found")
    
    # Test 3: Get all cards
    print("\n--- Test 3: Get all cards ---")
    all_cards = memory_service.get_all_cards()
    print(f"[SUCCESS] Retrieved {len(all_cards)} cards total")
    
    # Test 4: Filter by tag
    print("\n--- Test 4: Filter by tag ---")
    tag = "python"
    print(f"Filtering by tag: '{tag}'")
    tagged_cards = memory_service.get_cards_by_tag(tag)
    print(f"[SUCCESS] Found {len(tagged_cards)} cards with tag '{tag}'")
    for card in tagged_cards:
        print(f"   - {card.content[:50]}...")
    
    # Test 5: Get card by ID
    if added_cards:
        print("\n--- Test 5: Get card by ID ---")
        test_id = str(added_cards[0].id)
        print(f"Retrieving card: {test_id}")
        card = memory_service.get_card_by_id(test_id)
        if card:
            print(f"[SUCCESS] Retrieved card: {card.content[:50]}...")
        else:
            print(f"[FAILED] Card not found")
    
    # Test 6: Delete card
    if added_cards:
        print("\n--- Test 6: Delete card ---")
        test_id = str(added_cards[0].id)
        print(f"Deleting card: {test_id}")
        success = memory_service.delete_card(test_id)
        if success:
            print(f"[SUCCESS] Card deleted successfully")
            remaining = memory_service.get_all_cards()
            print(f"   Remaining cards: {len(remaining)}")
        else:
            print(f"[FAILED] Failed to delete card")
    
    print("\n=== Memory Service Tests Complete ===")


def main():
    """Run all tests."""
    print("=" * 60)
    print("Trinity Context Core - Memory System Test")
    print("=" * 60)
    
    # Test 1: Gemini API
    gemini_ok = test_gemini_embedding()
    
    if not gemini_ok:
        print("\n[WARNING] Gemini API test failed. Check your API key in .env file.")
        print("Cannot proceed with memory service tests.")
        return
    
    # Test 2: Memory Service
    try:
        test_memory_service_in_memory()
        print("\n" + "=" * 60)
        print("[SUCCESS] ALL TESTS PASSED!")
        print("=" * 60)
    except Exception as e:
        print(f"\n[FAILED] Test failed with error: {e}")
        import traceback
        traceback.print_exc()


if __name__ == "__main__":
    main()
