"""
Test script for MemoryService updates.

Tests:
1. add_memory with comprehensive ContextCard
2. verify_execution (Success Seal)
3. search with filtering (verified_only, min_importance)
"""
import uuid
from datetime import datetime
from src.memory.service import MemoryService
from src.memory.schemas import ContextCard

def test_memory_service_updates():
    print("=" * 60)
    print("MemoryService Updates Test")
    print("=" * 60)
    print()

    service = MemoryService()
    
    # 1. Test add_memory with comprehensive card
    print("--- 1. Testing add_memory ---")
    
    card_id = uuid.uuid4()
    card = ContextCard(
        id=card_id,
        content="Testing MemoryService updates with comprehensive fields",
        tags=["test", "memory_service", "update"],
        source="test_script",
        importance=8,
        logic_logs={
            "phase": "testing",
            "test_run": 1
        },
        system_state={
            "env": "test"
        },
        decision_context="Verifying new functionality"
    )
    
    added_card = service.add_memory(card)
    
    if added_card:
        print(f"[SUCCESS] Added memory card: {added_card.id}")
    else:
        print("[FAIL] Failed to add memory card")
        return

    # 2. Test verify_execution
    print("\n--- 2. Testing verify_execution ---")
    
    # Verify success
    success = service.verify_execution(
        card_id=str(card_id),
        success=True,
        output="Test execution successful"
    )
    
    if success:
        print(f"[SUCCESS] Verified execution for card {card_id}")
    else:
        print(f"[FAIL] Failed to verify execution for card {card_id}")
        
    # Check if verification was stored
    retrieved_card = service.get_card_by_id(str(card_id))
    if retrieved_card and retrieved_card.logic_logs.get("execution_verified") == "Печать Успеха":
         print("[SUCCESS] 'Печать Успеха' found in logic_logs")
    else:
         print(f"[FAIL] Verification seal not found. Logic logs: {retrieved_card.logic_logs if retrieved_card else 'None'}")

    # 3. Test search with filtering
    print("\n--- 3. Testing search filtering ---")
    
    # Search verified only
    print("Searching for verified cards...")
    verified_results = service.search(
        query="Testing MemoryService",
        verified_only=True
    )
    
    found_verified = any(str(c.id) == str(card_id) for c in verified_results)
    if found_verified:
        print(f"[SUCCESS] Found verified card in verified_only search. Total results: {len(verified_results)}")
    else:
        print("[FAIL] Verified card not found in verified_only search")

    # Search high importance
    print("Searching for high importance (>= 8)...")
    important_results = service.search(
        query="Testing MemoryService",
        min_importance=8
    )
    
    found_important = any(str(c.id) == str(card_id) for c in important_results)
    if found_important:
        print(f"[SUCCESS] Found card in high importance search. Total results: {len(important_results)}")
        for i, c in enumerate(important_results[:3]):
             print(f"  {i+1}. {c.content[:30]}... (Imp: {c.importance})")
    else:
        print("[FAIL] Card not found in high importance search")

    # Search low importance (should exclude our card if we set high min)
    print("Searching for very high importance (>= 9)...")
    very_important_results = service.search(
        query="Testing MemoryService",
        min_importance=9
    )
    found_very_important = any(str(c.id) == str(card_id) for c in very_important_results)
    if not found_very_important:
        print(f"[SUCCESS] Card correctly excluded from importance >= 9 search.")
    else:
        print(f"[FAIL] Card found in importance >= 9 search (Should act as filter). Card Imp: {card.importance}")

    print("\n" + "=" * 60)
    print("Test Complete")
    print("=" * 60)

if __name__ == "__main__":
    try:
        test_memory_service_updates()
    except Exception as e:
        print(f"[ERROR] Test failed: {e}")
        import traceback
        traceback.print_exc()
