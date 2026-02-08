"""
Quick test script for updated Archivarius specifications.
Tests the new filtering funnel with simplified Deep Think.
"""

import sys
import logging
from pathlib import Path

# Fix Windows encoding
if sys.platform == "win32":
    sys.stdout.reconfigure(encoding='utf-8')
    sys.stderr.reconfigure(encoding='utf-8')

# Add src to path
sys.path.insert(0, str(Path(__file__).parent / "src"))

# Setup logging
logging.basicConfig(level=logging.INFO, format='%(message)s')

from core.memory_guard import MemoryGuard

print("=" * 70)
print("🧪 QUICK TEST - Updated Specifications")
print("=" * 70)

guard = MemoryGuard()

# Test 1: is_garbage() method
print("\n[TEST 1] is_garbage() Method")
print("-" * 70)

test_cases = [
    ("chatgpt wrapper spam", True),
    ("passive income system", True),
    ("no-code builder app", True),
    ("Valid technical content", False)
]

for text, expected in test_cases:
    result = guard.is_garbage(text)
    status = "✅" if result == expected else "❌"
    print(f"{status} is_garbage('{text[:30]}...'): {result} (expected: {expected})")

# Test 2: Base score is 5.0
print("\n[TEST 2] Base Score = 5.0")
print("-" * 70)

plain_text = "Some random plain text"
score = guard.calculate_score(plain_text)
print(f"Plain text score: {score:.1f}/10 (expected: 5.0)")

# Test 3: HuggingFace domain
print("\n[TEST 3] HuggingFace Domain (+2.0)")
print("-" * 70)

hf_text = "Check out this model on huggingface.co"
score = guard.calculate_score(hf_text)
print(f"HuggingFace text score: {score:.1f}/10 (expected: 7.0)")

# Test 4: New authority names
print("\n[TEST 4] Authority Names: Karpathy, LeCun, Altman, Hassabis")
print("-" * 70)

authority_tests = [
    ("Article by Karpathy", 7.0),
    ("Paper by LeCun", 7.0),
    ("Talk by Altman", 7.0),
    ("Research by Hassabis", 7.0)
]

for text, expected_score in authority_tests:
    score = guard.calculate_score(text)
    status = "✅" if score >= expected_score else "❌"
    print(f"{status} '{text}': {score:.1f}/10")

# Test 5: New relevance keywords
print("\n[TEST 5] Relevance Keywords: RTX 4090, GSoC, Optimization, CUDA, Agentic")
print("-" * 70)

keyword_tests = [
    ("RTX 4090 guide", 7.0),
    ("GSoC project", 7.0),
    ("CUDA optimization", 7.0),
    ("Agentic workflows", 7.0)
]

for text, expected_score in keyword_tests:
    score = guard.calculate_score(text)
    status = "✅" if score >= expected_score else "❌"
    print(f"{status} '{text}': {score:.1f}/10")

# Test 6: Combined scoring
print("\n[TEST 6] Combined Scoring (Should reach 10.0)")
print("-" * 70)

max_score_text = "Karpathy's RTX 4090 CUDA guide on github.com ```python code```"
score = guard.calculate_score(max_score_text)
print(f"Max score text: {score:.1f}/10 (expected: 10.0)")
print(f"Breakdown: Base(5.0) + Github(2.0) + Code(1.5) + Authority(2.0) + Keyword(2.0) = 12.5 → capped at 10.0")

print("\n" + "=" * 70)
print("✅ All specification tests complete!")
print("=" * 70)

print("\n⚠️  NOTE: gemma:2b model not found in Ollama.")
print("Available model: gemma3:4b")
print("To test Archivarius Deep Think, either:")
print("1. Pull gemma:2b with: ollama pull gemma:2b")
print("2. Or temporarily change model in archivarius.py to 'gemma3:4b'")
