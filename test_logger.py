"""
Test script for ContextLogger.

Tests the automatic logging functionality with keyword-based importance boosting.
"""
from src.core.logger import ContextLogger
from src.memory.service import MemoryService
from qdrant_client import QdrantClient


def test_context_logger():
    """Test the ContextLogger functionality."""
    print("=" * 60)
    print("ContextLogger Test")
    print("=" * 60)
    print()
    
    # Create in-memory Qdrant for testing
    print("Setting up in-memory database...")
    client = QdrantClient(":memory:")
    memory_service = MemoryService(client=client)
    
    # Initialize logger
    logger = ContextLogger(memory_service=memory_service)
    print("[SUCCESS] ContextLogger initialized")
    print()
    
    # Test 1: Normal logging (no keyword boost)
    print("--- Test 1: Normal logging ---")
    result = logger.commit_to_memory(
        content="User is learning Python and FastAPI basics",
        tags=["learning", "python"],
        importance=5
    )
    print(f"Result: {'SUCCESS' if result else 'FAILED'}")
    print()
    
    # Test 2: Keyword boost - "Фукуока"
    print("--- Test 2: Keyword boost (Фукуока) ---")
    result = logger.commit_to_memory(
        content="User wants to move to Фукуока after graduating",
        tags=["goal", "location"],
        importance=5
    )
    print(f"Result: {'SUCCESS' if result else 'FAILED'}")
    print()
    
    # Test 3: Keyword boost - "Trinity"
    print("--- Test 3: Keyword boost (Trinity) ---")
    result = logger.commit_to_memory(
        content="Trinity architecture uses Haq AI, Liar's Requiem, and Mahoraga",
        tags=["architecture", "agents"],
        importance=6
    )
    print(f"Result: {'SUCCESS' if result else 'FAILED'}")
    print()
    
    # Test 4: Bug logging (includes "Баг" keyword)
    print("--- Test 4: Bug logging ---")
    result = logger.log_bug(
        "Qdrant search method deprecated, need to use query_points",
        tags=["qdrant", "api"]
    )
    print(f"Result: {'SUCCESS' if result else 'FAILED'}")
    print()
    
    # Test 5: Solution logging (includes "Решение" keyword)
    print("--- Test 5: Solution logging ---")
    result = logger.log_solution(
        "Fixed by replacing client.search() with client.query_points()",
        tags=["qdrant", "fix"]
    )
    print(f"Result: {'SUCCESS' if result else 'FAILED'}")
    print()
    
    # Test 6: Insight logging
    print("--- Test 6: Insight logging ---")
    result = logger.log_insight(
        "Direct MemoryService integration is faster than HTTP calls",
        tags=["performance", "architecture"]
    )
    print(f"Result: {'SUCCESS' if result else 'FAILED'}")
    print()
    
    # Test 7: Get statistics
    print("--- Test 7: Logger statistics ---")
    stats = logger.get_stats()
    print(f"Total memories: {stats['total_memories']}")
    print(f"Auto-logged: {stats['auto_logged']}")
    print(f"High importance: {stats['high_importance']}")
    print()
    
    # Test 8: Verify importance boosting
    print("--- Test 8: Verify memory contents ---")
    all_cards = memory_service.get_all_cards()
    print(f"Found {len(all_cards)} cards:")
    for card in all_cards:
        preview = card.content[:50] + "..." if len(card.content) > 50 else card.content
        boost_marker = "[HIGH]" if card.importance >= 9 else ""
        print(f"  {boost_marker} [{card.importance}] {preview}")
        print(f"     Source: {card.source}, Tags: {card.tags}")
    print()
    
    print("=" * 60)
    print("[SUCCESS] All ContextLogger tests completed!")
    print("=" * 60)


if __name__ == "__main__":
    test_context_logger()
