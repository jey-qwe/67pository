"""
Load initial memories from JSON grimoire file.

This script loads the foundational context cards from initial_memories.json
and adds them to the Trinity Context Core memory system.
"""
import json
import sys
from pathlib import Path
import httpx

# API Configuration
API_BASE_URL = "http://localhost:8000/api/v1"
TIMEOUT = 30.0

# Path to grimoire file
GRIMOIRE_PATH = Path(__file__).parent.parent / "data" / "initial_memories.json"


def load_grimoire():
    """Load initial memories from JSON file."""
    try:
        with open(GRIMOIRE_PATH, 'r', encoding='utf-8') as f:
            memories = json.load(f)
        return memories
    except FileNotFoundError:
        print(f"[ERROR] Grimoire file not found: {GRIMOIRE_PATH}")
        return []
    except json.JSONDecodeError as e:
        print(f"[ERROR] Invalid JSON in grimoire: {e}")
        return []


def add_memory(memory: dict) -> bool:
    """Add a single memory card to the system."""
    try:
        with httpx.Client(timeout=TIMEOUT) as client:
            response = client.post(
                f"{API_BASE_URL}/memory/add",
                json=memory
            )
            
            if response.status_code == 201:
                return True
            else:
                print(f"[FAILED] Error: {response.status_code}")
                print(f"  Details: {response.text}")
                return False
                
    except httpx.ConnectError:
        print(f"[ERROR] Cannot connect to API at {API_BASE_URL}")
        print("  Make sure the server is running: python run.py")
        return False
    except Exception as e:
        print(f"[ERROR] {e}")
        return False


def main():
    """Main function to load grimoire into memory."""
    print("=" * 60)
    print("Trinity Context Core - Grimoire Loader")
    print("=" * 60)
    print()
    
    # Load memories from file
    memories = load_grimoire()
    
    if not memories:
        print("[ERROR] No memories found in grimoire")
        return 1
    
    print(f"[INFO] Found {len(memories)} initial memories")
    print()
    
    # Add each memory
    success_count = 0
    for i, memory in enumerate(memories, 1):
        preview = memory['content'][:60] + "..." if len(memory['content']) > 60 else memory['content']
        print(f"{i}. {preview}")
        
        if add_memory(memory):
            print(f"   [SUCCESS] Added to memory")
            success_count += 1
        else:
            print(f"   [FAILED] Could not add")
        print()
    
    # Summary
    print("=" * 60)
    print(f"[COMPLETE] Loaded {success_count}/{len(memories)} memories")
    print("=" * 60)
    
    return 0 if success_count == len(memories) else 1


if __name__ == "__main__":
    sys.exit(main())
