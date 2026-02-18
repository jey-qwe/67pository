"""
Comprehensive test for updated schema with error tracking fields.

Tests the new logic_logs, system_state, and decision_context fields.
"""
from src.core.logger import ContextLogger
from src.memory.service import MemoryService
from qdrant_client import QdrantClient


def test_enhanced_schema():
    """Test the enhanced schema with new fields."""
    print("=" * 60)
    print("Enhanced Schema Test")
    print("=" * 60)
    print()
    
    # Use the real Qdrant instance (not in-memory) to see actual error logs
    print("Connecting to Qdrant...")
    memory_service = MemoryService()
    print("[SUCCESS] Connected to database")
    print()
    
    # Test 1: Add card with all new fields
    print("--- Test 1: Adding card with full metadata ---")
    card1 = memory_service.add_card(
        content="Fixed Qdrant search API by switching from client.search() to client.query_points()",
        tags=["fix", "qdrant", "api", "search"],
        source="manual",
        importance=9,
        logic_logs={
            "error_trace": "'QdrantClient' object has no attribute 'search'",
            "failed_attempts": [
                "Tried updating qdrant-client version",
                "Checked official docs for search method"
            ]
        },
        system_state={
            "os": "Windows 11",
            "environment": "Docker (Qdrant v1.x)",
            "hardware": "Thunderobot 16GB RAM"
        },
        decision_context="The Qdrant API changed. query_points() is the new method, and results are in .points attribute not direct iteration"
    )
    
    if card1:
        print(f"[SUCCESS] Card created: {card1.id}")
        print(f"  Importance: {card1.importance}")
        print(f"  Has logic_logs: {card1.logic_logs is not None}")
        print(f"  Has system_state: {card1.system_state is not None}")
        print(f"  Has decision_context: {card1.decision_context is not None}")
    print()
    
    # Test 2: Check error cards from interceptor
    print("--- Test 2: Checking error interceptor cards ---")
    all_cards = memory_service.get_all_cards()
    error_cards = [c for c in all_cards if "error" in c.tags and "intercepted" in c.tags]
    
    print(f"Total cards: {len(all_cards)}")
    print(f"Error interceptor cards: {len(error_cards)}")
    
    if error_cards:
        print("\nError cards with full context:")
        for i, card in enumerate(error_cards[:3], 1):  # Show first 3
            print(f"\n{i}. Card ID: {card.id}")
            print(f"   Importance: {card.importance}")
            print(f"   Tags: {card.tags}")
            print(f"   Source: {card.source}")
            # Show snippet of content
            lines = card.content.split('\n')
            print(f"   Content (first 3 lines):")
            for line in lines[:3]:
                print(f"     {line}")
    print()
    
    # Test 3: Search for cards with logic_logs
    print("--- Test 3: Cards with logic_logs ---")
    cards_with_logs = [c for c in all_cards if hasattr(c, 'logic_logs') and c.logic_logs]
    print(f"Cards with logic_logs: {len(cards_with_logs)}")
    
    # Test 4: Cards with decision_context
    print("\n--- Test 4: Cards with decision_context ---")
    cards_with_context = [c for c in all_cards if hasattr(c, 'decision_context') and c.decision_context]
    print(f"Cards with decision_context: {len(cards_with_context)}")
    
    if cards_with_context:
        for card in cards_with_context[:2]:
            print(f"\n  Decision: {card.decision_context[:100]}...")
    
    print()
    print("=" * 60)
    print("[COMPLETE] Enhanced schema test finished")
    print("=" * 60)


if __name__ == "__main__":
    try:
        test_enhanced_schema()
    except Exception as e:
        print(f"[ERROR] Test failed: {e}")
        import traceback
        traceback.print_exc()
