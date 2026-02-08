
from src.agents.brain import BrainAgent
from src.utils import safe_print

def test_brain_memory():
    safe_print("🧠 Testing Brain RAG Memory...")
    
    # Initialize Brain (should load FAISS)
    brain = BrainAgent()
    
    if not brain.vectorstore:
        safe_print("❌ Memory NOT loaded.")
    else:
        safe_print("✅ Memory loaded successfully.")

    # Test Retrieval
    query = "Python automation skills"
    context = brain._retrieve_context(query)
    
    if context:
        safe_print(f"\n✅ Retrieval Test Found Context:\n{context[:200]}...")
    else:
        safe_print("\n⚠️ No context retrieved (DB might be empty or query mismatch).")

    # Test Analysis with Context
    job = "Looking for a Python developer to build a web scraper for real estate data."
    safe_print(f"\nAnalyzing Job: {job}")
    
    result = brain.analyze_job(job)
    safe_print(f"\nResult:\nScore: {result.get('score')}\nReasoning: {result.get('reasoning')}")
    safe_print(f"Bid Draft: {result.get('bid_draft')}")

if __name__ == "__main__":
    test_brain_memory()
