"""
Trinity Context Core - Memory Seeding Script

Seeds the memory database with initial context cards from JSON grimoire file.
"""
import httpx
import sys
import time
import json
from pathlib import Path
from typing import Dict, List


# API Configuration
API_BASE_URL = "http://localhost:8000/api/v1"
TIMEOUT = 30.0

# Path to grimoire file
GRIMOIRE_PATH = Path(__file__).parent.parent / "data" / "initial_memories.json"


def load_grimoire() -> List[Dict]:
    """
    Load initial memories from JSON grimoire file.
    
    Returns:
        List of memory card dictionaries
    """
    try:
        with open(GRIMOIRE_PATH, 'r', encoding='utf-8') as f:
            memories = json.load(f)
        
        if not isinstance(memories, list):
            print(f"[ERROR] Grimoire must contain a JSON array, got {type(memories)}")
            return []
        
        print(f"[SUCCESS] Loaded {len(memories)} cards from grimoire")
        return memories
        
    except FileNotFoundError:
        print(f"[ERROR] Grimoire file not found: {GRIMOIRE_PATH}")
        print("  Please create src/data/initial_memories.json")
        return []
    except json.JSONDecodeError as e:
        print(f"[ERROR] Invalid JSON in grimoire: {e}")
        print(f"  File: {GRIMOIRE_PATH}")
        return []
    except Exception as e:
        print(f"[ERROR] Could not load grimoire: {e}")
        return []


def add_memory_card(card: Dict) -> bool:
    """
    Add a single memory card to the system.
    
    Args:
        card: Dictionary containing card data
        
    Returns:
        True if successful, False otherwise
    """
    try:
        with httpx.Client(timeout=TIMEOUT) as client:
            response = client.post(
                f"{API_BASE_URL}/memory/add",
                json=card
            )
            
            if response.status_code == 201:
                return True
            else:
                print(f"[FAILED] Error {response.status_code}: {response.text}")
                return False
                
    except httpx.ConnectError:
        print(f"[ERROR] Cannot connect to API at {API_BASE_URL}")
        print("  Make sure the server is running: python run.py")
        return False
    except Exception as e:
        print(f"[ERROR] {e}")
        return False


def search_memory(query: str, limit: int = 5) -> List[Dict]:
    """
    Search memory for relevant context cards.
    
    Args:
        query: Search query
        limit: Maximum number of results
        
    Returns:
        List of matching cards
    """
    try:
        with httpx.Client(timeout=TIMEOUT) as client:
            response = client.post(
                f"{API_BASE_URL}/memory/search",
                json={"query": query, "limit": limit}
            )
            
            if response.status_code == 200:
                return response.json().get("results", [])
            else:
                print(f"[FAILED] Search error: {response.status_code}")
                return []
                
    except Exception as e:
        print(f"[ERROR] Search failed: {e}")
        return []


def verify_seeding():
    """
    Verify that seeding was successful by performing a search.
    """
    print("\n" + "=" * 60)
    print("VERIFICATION: Testing Memory Search")
    print("=" * 60)
    
    query = "Куда мы идем?"
    print(f"\nQuery: '{query}'\n")
    
    results = search_memory(query, limit=3)
    
    if results:
        print(f"[SUCCESS] Found {len(results)} relevant cards:\n")
        for i, card in enumerate(results, 1):
            content_preview = card['content'][:80] + "..." if len(card['content']) > 80 else card['content']
            print(f"{i}. {content_preview}")
            print(f"   Tags: {card['tags']}")
            print(f"   Importance: {card['importance']}/10")
            print()
    else:
        print("[WARNING] No results found.")
        print("  Note: Search may be limited in in-memory mode without Docker")


def main():
    """
    Main seeding function.
    """
    print("=" * 60)
    print("Trinity Context Core - Memory Seeding from Grimoire")
    print("=" * 60)
    print()
    
    # Load memories from grimoire
    memories = load_grimoire()
    
    if not memories:
        print("\n[ERROR] No memories to load. Exiting.")
        return 1
    
    print(f"\nLoading {len(memories)} context cards from grimoire...\n")
    
    # Add all context cards
    success_count = 0
    failed_cards = []
    
    for i, card in enumerate(memories, 1):
        # Show preview
        content_preview = card.get('content', '')[:60] + "..." if len(card.get('content', '')) > 60 else card.get('content', '')
        print(f"[{i}/{len(memories)}] {content_preview}")
        
        # Add to memory
        if add_memory_card(card):
            print(f"        [SUCCESS] Added")
            success_count += 1
        else:
            print(f"        [FAILED] Could not add")
            failed_cards.append(i)
        
        time.sleep(0.5)  # Small delay to avoid rate limiting
        print()
    
    # Summary
    print("=" * 60)
    print(f"COMPLETE: Loaded {success_count}/{len(memories)} cards")
    if failed_cards:
        print(f"Failed cards: {failed_cards}")
    print("=" * 60)
    
    # Verify with search (if at least some cards were added)
    if success_count > 0:
        verify_seeding()
    
    print("\n" + "=" * 60)
    print("Seeding Complete!")
    print("=" * 60)
    
    return 0 if success_count == len(memories) else 1


if __name__ == "__main__":
    sys.exit(main())
