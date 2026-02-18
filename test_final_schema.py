"""
Comprehensive test for final ContextCard schema.

Tests all new fields including enhanced logic_logs,
system_state, vws_metadata, and decision_context.
"""
from src.memory.service import MemoryService


def test_final_schema():
    """Test the ultimate ContextCard schema."""
    print("=" * 60)
    print("Final Context Schema Test")
    print("=" * 60)
    print()
    
    # Use real Qdrant instance
    print("Connecting to Qdrant...")
    memory_service = MemoryService()
    print("[SUCCESS] Connected")
    print()
    
    # Test 1: Add card with ALL fields
    print("--- Test 1: Card with all comprehensive fields ---")
    card = memory_service.add_card(
        content="Implemented VWS with ls_contextual and tree_focused for intelligent file navigation",
        tags=["vws", "workspace", "filesystem", "qdrant"],
        source="manual",
        importance=9,
        logic_logs={
            "error_trace": "UnicodeEncodeError with emoji icons in tree output",
            "failed_attempts": [
                "Used Unicode box-drawing characters",
                "Tried UTF-8 encoding in print"
            ],
            "code_diff": "- icon = '📁'\n+ icon = '[DIR]'",
            "phase_ref_state": "vws_v1_stable"
        },
        system_state={
            "os_version": "Windows 11",
            "resources": "16GB RAM (60% used)",
            "hardware": "Thunderobot"
        },
        vws_metadata={
            "related_files": [
                "src/core/vws.py",
                "test_vws.py",
                "src/memory/service.py"
            ],
            "dependencies": ["os", "pathlib", "qdrant-client"]
        },
        decision_context="Replaced all Unicode characters with ASCII for Windows console compatibility. VWS provides file access control via WorkspaceManifest to prevent unauthorized file reads."
    )
    
    if card:
        print(f"[SUCCESS] Card created: {card.id}")
        print(f"  Tags: {card.tags}")
        print(f"  Importance: {card.importance}")
        print(f"  Source: {card.source}")
        print()
        
        # Verify all fields
        print("  Field verification:")
        print(f"    Has logic_logs: {card.logic_logs is not None}")
        if card.logic_logs:
            print(f"      - error_trace: {bool(card.logic_logs.get('error_trace'))}")
            print(f"      - failed_attempts: {bool(card.logic_logs.get('failed_attempts'))}")
            print(f"      - code_diff: {bool(card.logic_logs.get('code_diff'))}")
            print(f"      - phase_ref_state: {bool(card.logic_logs.get('phase_ref_state'))}")
        
        print(f"    Has system_state: {card.system_state is not None}")
        if card.system_state:
            print(f"      - os_version: {card.system_state.get('os_version')}")
            print(f"      - resources: {card.system_state.get('resources')}")
            print(f"      - hardware: {card.system_state.get('hardware')}")
        
        print(f"    Has vws_metadata: {card.vws_metadata is not None}")
        if card.vws_metadata:
            files = card.vws_metadata.get('related_files', [])
            deps = card.vws_metadata.get('dependencies', [])
            print(f"      - related_files: {len(files)} files")
            print(f"      - dependencies: {len(deps)} deps")
        
        print(f"    Has decision_context: {bool(card.decision_context)}")
        print()
    
    # Test 2: Backwards compatibility - minimal card
    print("--- Test 2: Minimal card (backwards compatibility) ---")
    minimal_card = memory_service.add_card(
        content="Simple memory card for testing backwards compatibility",
        tags=["test", "minimal"]
    )
    
    if minimal_card:
        print(f"[SUCCESS] Minimal card created: {minimal_card.id}")
        print(f"  Source (default): {minimal_card.source}")
        print(f"  Importance (default): {minimal_card.importance}")
        print(f"  Decision context (default): '{minimal_card.decision_context}'")
        print()
    
    # Test 3: Retrieve and verify all cards
    print("--- Test 3: Retrieving all cards ---")
    all_cards = memory_service.get_all_cards()
    
    comprehensive_cards = [
        c for c in all_cards 
        if c.vws_metadata is not None or (c.logic_logs and 'code_diff' in c.logic_logs)
    ]
    
    print(f"Total cards: {len(all_cards)}")
    print(f"Cards with comprehensive data: {len(comprehensive_cards)}")
    print()
    
    if comprehensive_cards:
        print("Sample comprehensive card:")
        sample = comprehensive_cards[0]
        print(f"  ID: {sample.id}")
        print(f"  Content (first 60 chars): {sample.content[:60]}...")
        print(f"  Tags: {sample.tags[:3]}...")
        
        if sample.logic_logs:
            print(f"  Logic Logs keys: {list(sample.logic_logs.keys())}")
        
        if sample.vws_metadata:
            print(f"  VWS Metadata keys: {list(sample.vws_metadata.keys())}")
    
    print()
    print("=" * 60)
    print("[COMPLETE] Final schema test finished")
    print("=" * 60)


if __name__ == "__main__":
    try:
        test_final_schema()
    except Exception as e:
        print(f"[ERROR] Test failed: {e}")
        import traceback
        traceback.print_exc()
