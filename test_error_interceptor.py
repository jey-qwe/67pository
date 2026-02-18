"""
Test script for error interceptor decorator.

Tests automatic error logging with system state capture.
"""
from src.core.logger import catch_logic_error, ContextLogger
from src.memory.service import MemoryService
from qdrant_client import QdrantClient


# Test functions with different error scenarios

@catch_logic_error(agent_name="Mahoraga", phase_ref="test_phase_001")
def function_with_division_error(a, b):
    """Test function that will cause ZeroDivisionError."""
    print(f"Attempting to divide {a} / {b}")
    return a / b


@catch_logic_error(agent_name="Muezzin", phase_ref="async_test_002")
def function_with_race_condition(data):
    """Test function simulating a race condition."""
    # Simulate race condition error
    raise RuntimeError("Race condition detected: concurrent access to shared resource")


@catch_logic_error(agent_name="Mahoraga")
def function_with_context_compression():
    """Test function simulating context compression issue."""
    raise ValueError("Context compression failed: memory limit exceeded")


def test_error_interceptor():
    """Test the error interceptor functionality."""
    print("=" * 60)
    print("Error Interceptor Test")
    print("=" * 60)
    print()
    
    # Set up in-memory database
    print("Setting up in-memory database...")
    client = QdrantClient(":memory:")
    memory_service = MemoryService(client=client)
    print("[SUCCESS] Database initialized")
    print()
    
    # Test 1: Division by zero error
    print("--- Test 1: Division by zero error ---")
    try:
        function_with_division_error(10, 0)
    except ZeroDivisionError:
        print("[EXPECTED] ZeroDivisionError caught and logged")
    print()
    
    # Test 2: Race condition error (should trigger mentor_sync_issue tag)
    print("--- Test 2: Race condition error ---")
    try:
        function_with_race_condition({"key": "value"})
    except RuntimeError:
        print("[EXPECTED] RuntimeError caught and logged")
        print("[INFO] Should be tagged with 'mentor_sync_issue'")
    print()
    
    # Test 3: Context compression error (should trigger mentor_sync_issue tag)
    print("--- Test 3: Context compression error ---")
    try:
        function_with_context_compression()
    except ValueError:
        print("[EXPECTED] ValueError caught and logged")
        print("[INFO] Should be tagged with 'mentor_sync_issue'")
    print()
    
    # Test 4: Check logged errors
    print("--- Test 4: Verify error cards in memory ---")
    all_cards = memory_service.get_all_cards()
    error_cards = [c for c in all_cards if "error" in c.tags]
    
    print(f"Total cards in database: {len(all_cards)}")
    print(f"Error cards logged: {len(error_cards)}")
    print()
    
    if error_cards:
        print("Logged error cards:")
        for i, card in enumerate(error_cards, 1):
            print(f"\n{i}. Importance: {card.importance}")
            print(f"   Agent: {[t for t in card.tags if t in ['mahoraga', 'muezzin']]}")
            print(f"   Tags: {card.tags}")
            # Show first 200 chars of content
            preview = card.content[:200] + "..." if len(card.content) > 200 else card.content
            print(f"   Content preview:\n   {preview}")
            
            # Check for mentor sync tag
            if "mentor_sync_issue" in card.tags:
                print("   [DETECTED] Mentor sync issue tag present")
    else:
        print("[WARNING] No error cards found")
    
    print()
    print("=" * 60)
    print("[COMPLETE] Error interceptor test finished")
    print("=" * 60)


if __name__ == "__main__":
    try:
        test_error_interceptor()
    except Exception as e:
        print(f"[ERROR] Test failed: {e}")
        import traceback
        traceback.print_exc()
