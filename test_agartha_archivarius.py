"""
Test script for Agartha LangGraph with Archivarius integration.
Tests the enhanced workflow with Memory Guard filtering.
"""

import sys
import logging
from pathlib import Path

# Fix Windows encoding
if sys.platform == "win32":
    sys.stdout.reconfigure(encoding='utf-8')
    sys.stderr.reconfigure(encoding='utf-8')

# Setup logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)

# Add src to path
sys.path.insert(0, str(Path(__file__).parent / "src" / "agartha gateopener" / "src"))

from core.graph import app

def test_agartha_with_archivarius():
    """
    Test the Agartha workflow with sample job data.
    """
    
    print("=" * 80)
    print("🚀 AGARTHA LANGGRAPH + ARCHIVARIUS TEST")
    print("=" * 80)
    
    # Simulate fetched jobs (normally from Scout)
    # We'll inject these directly to test the Memory Guard+ filtering
    test_state = {
        "feed_url": "test://simulation",
        "platform": "test",
        "seen_ids": [],
        "fetched_jobs": [
            # Job 1: SPAM (should be blocked by Memory Guard)
            {
                "id": "spam-1",
                "title": "Make passive income with this chatgpt wrapper!",
                "link": "https://example.com/spam1",
                "description": "Easy money with no-code builder. Course selling opportunity!",
                "platform": "test"
            },
            
            # Job 2: Low quality (should be blocked by evidence score)
            {
                "id": "lowq-1",
                "title": "Need someone to help with basic task",
                "link": "https://example.com/lowq1",
                "description": "Just a simple task, nothing special",
                "platform": "test"
            },
            
            # Job 3: HIGH QUALITY (should pass all filters)
            {
                "id": "quality-1",
                "title": "Python AI Engineer - RAG Systems & Agentic Workflows",
                "link": "https://github.com/example/ai-job",
                "description": """
                Looking for an experienced Python developer for AI/ML project.
                
                Requirements:
                - Strong Python skills
                - Experience with RAG (Retrieval-Augmented Generation)
                - Knowledge of LangChain, CrewAI, or similar frameworks
                - CUDA optimization experience
                - RTX 4090 or similar GPU experience preferred
                
                Project involves building autonomous agents and optimizing LLM pipelines.
                GSoC contributors welcome. GitHub portfolio required.
                
                ```python
                # Sample code your experience should cover:
                from langchain import VectorStore
                embeddings = create_embeddings()
                ```
                
                Budget: $3000-5000/month
                Remote OK
                """,
                "platform": "test"
            },
            
            # Job 4: Medium quality (might pass or fail depending on Brain analysis)
            {
                "id": "medium-1",
                "title": "Python developer needed for automation",
                "link": "https://example.com/medium1",
                "description": "Looking for Python developer to automate some tasks. Selenium experience needed.",
                "platform": "test"
            }
        ]
    }
    
    print("\n📥 SIMULATED INPUT:")
    print(f"   Total jobs: {len(test_state['fetched_jobs'])}")
    for i, job in enumerate(test_state['fetched_jobs'], 1):
        print(f"   {i}. {job['title'][:60]}...")
    
    print("\n" + "=" * 80)
    print("⚡ RUNNING AGARTHA WORKFLOW...")
    print("=" * 80)
    
    try:
        # Run the workflow
        result = app.invoke(test_state)
        
        print("\n" + "=" * 80)
        print("📊 WORKFLOW RESULTS")
        print("=" * 80)
        
        print(f"\n🕸️  Fetched: {len(result.get('fetched_jobs', []))}")
        print(f"🔍 Sifter Passed: {len(result.get('relevant_jobs', []))}")
        print(f"🛡️  Memory Guard Passed: {len(result.get('filtered_jobs', []))}")
        print(f"🧠 Brain Analyzed: {len(result.get('analyzed_jobs', []))}")
        print(f"🧐 Critic Approved: {len(result.get('approved_jobs', []))}")
        
        if result.get('approved_jobs'):
            print("\n✅ APPROVED JOBS:")
            for job in result['approved_jobs']:
                print(f"\n   📌 {job['title']}")
                print(f"      Score: {job.get('score', 'N/A')}/10")
                print(f"      Evidence: {job.get('evidence_score', 'N/A')}/10")
                print(f"      Link: {job['link']}")
                print(f"      Reasoning: {job.get('reasoning', 'N/A')[:100]}...")
        
        print("\n" + "=" * 80)
        print("✅ TEST COMPLETE")
        print("=" * 80)
        
    except Exception as e:
        print(f"\n❌ ERROR: {e}")
        import traceback
        traceback.print_exc()

if __name__ == "__main__":
    test_agartha_with_archivarius()
