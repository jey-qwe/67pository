
from src.core.graph import app
from src.agents.scout import ScoutAgent
from src.utils import safe_print

# Mock state
safe_print("🚀 Testing Graph...")
try:
    # Use a real URL or mock? 
    # Let's use a real one but with a fast timeout if possible, or just trust ScoutAgent works (it was tested separately)
    # Actually, let's run the graph with a real URL but we need to ensure Brain doesn't error out.
    
    url = "https://www.reddit.com/r/pythonjobs/.rss"
    result = app.invoke({"feed_url": url, "seen_ids": []})
    
    safe_print("\n✅ Graph Execution Complete!")
    safe_print(f"Fetched: {len(result.get('fetched_jobs', []))}")
    safe_print(f"Relevant: {len(result.get('relevant_jobs', []))}")
    safe_print(f"Analyzed: {len(result.get('analyzed_jobs', []))}")
    safe_print(f"Approved: {len(result.get('approved_jobs', []))}")
    
    if result.get('approved_jobs'):
        msg = result['approved_jobs'][0]['bid_draft']
        safe_print(f"\nSample Bid:\n{msg[:200]}...")

except Exception as e:
    safe_print(f"❌ Graph Error: {e}")
