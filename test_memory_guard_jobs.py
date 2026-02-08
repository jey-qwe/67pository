"""
Simple test to demonstrate Archivarius Memory Guard filtering.
Tests filtering logic without requiring full LangGraph setup.
"""

import sys
import logging
from pathlib import Path

#Fix Windows encoding
if sys.platform == "win32":
    sys.stdout.reconfigure(encoding='utf-8')
    sys.stderr.reconfigure(encoding='utf-8')

# Add project to path
sys.path.insert(0, str(Path(__file__).parent / "src"))

from core.memory_guard import MemoryGuard

try:
    from agents.archivarius import Archivarius
    ARCH_AVAILABLE = True
except:
    ARCH_AVAILABLE = False
    print("⚠️  Archivarius not available, testing Memory Guard only")

logging.basicConfig(level=logging.INFO, format='%(message)s')

def test_memory_guard_on_jobs():
    """Test Memory Guard filtering on simulated job posts"""
    
    print("=" * 80)
    print("🛡️  MEMORY GUARD TEST - Job Filtering Simulation")
    print("=" * 80)
    
    guard = MemoryGuard()
    
    # Simulated jobs
    test_jobs = [
        {
            "title": "Make passive income with chatgpt wrapper!",
            "description": "Easy money with no-code builder. Course selling opportunity!",
            "expected": "SPAM"
        },
        {
            "title": "Need someone for basic task",
            "description": "Just a simple task, nothing special",
            "expected": "LOW_QUALITY"
        },
        {
            "title": "Python AI Engineer - RAG & CUDA",
            "description": """
Looking for Python developer with RAG experience.
Work on github.com/example/ai-project

Requirements:
- Python, LangChain
- CUDA optimization
- RTX 4090 experience 
- GSoC contributors welcome

```python
from langchain import VectorStore
```

Karpathy recommended this approach.
            """,
            "expected": "HIGH_QUALITY"
        },
        {
            "title": "Automation engineer needed",
            "description": "Python Selenium automation work",
            "expected": "MEDIUM_QUALITY"
        }
    ]
    
    print("\n📋 TESTING {len(test_jobs)} SIMULATED JOBS\n")
    
    passed_jobs = []
    
    for i, job in enumerate(test_jobs, 1):
        job_text = f"{job['title']}\n{job['description']}"
        
        print(f"\n{'-' * 80}")
        print(f"JOB #{i}: {job['title'][:60]}...")
        print(f"Expected: {job['expected']}")
        print(f"{'-' * 80}")
        
        # Test 1: Garbage check
        is_spam = guard.is_garbage(job_text)
        print(f"🛡️  Blacklist Check: {'❌ SPAM' if is_spam else '✅ CLEAN'}")
        
        if is_spam:
            print(f"Result: ❌ REJECTED (Spam)")
            continue
        
        # Test 2: Evidence score
        score = guard.calculate_score(job_text)
        print(f"📊 Evidence Score: {score:.1f}/10")
        
        if score < 4.0:
            print(f"Result: ❌ REJECTED (Low Quality, threshold: 4.0)")
            continue
        
        print(f"Result: ✅ PASSED Memory Guard")
        passed_jobs.append({**job, 'evidence_score': score})
    
    print(f"\n{'=' * 80}")
    print(f"📊 SUMMARY")
    print(f"{'=' * 80}")
    print(f"Total Jobs: {len(test_jobs)}")
    print(f"Passed Guard: {len(passed_jobs)}")
    print(f"Blocked: {len(test_jobs) - len(passed_jobs)}")
    
    if passed_jobs:
        print(f"\n✅ JOBS THAT WOULD PROCEED TO BRAIN ANALYSIS:")
        for job in passed_jobs:
            print(f"   - {job['title'][:50]}... (Score: {job['evidence_score']:.1f})")
    
    print(f"\n{'=' * 80}")
    
    # Bonus: Test with Archivarius if available
    if ARCH_AVAILABLE:
        print("\n🧠 BONUS: Testing with full Archivarius Deep Think")
        print("=" * 80)
        
        arch = Archivarius()
        
        for job in passed_jobs:
            job_text = f"{job['title']}\n{job['description']}"
            print(f"\n📌 {job['title'][:50]}...")
            
            # Deep Think
            result = arch._deep_think(job_text)
            print(f"   Deep Think: {result}")
            
            if result == "RELEVANT":
                print(f"   ✅ Would be saved to FAISS")
            else:
                print(f"   ⏭️  Would be skipped (NOISE)")
    
    print("\n" + "=" * 80)
    print("✅ TEST COMPLETE")
    print("=" * 80)

if __name__ == "__main__":
    test_memory_guard_on_jobs()
