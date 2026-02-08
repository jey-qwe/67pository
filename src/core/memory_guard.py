"""
Memory Guard - The Bouncer & The Sieve
Filters garbage and calculates evidence-based quality scores
Part of Archivarius 2.0 Active Memory System
"""

import re
from typing import Tuple, Dict, Any


class MemoryGuard:
    """
    The Bouncer & The Sieve.
    Filters garbage and calculates evidence-based quality scores.
    """
    
    def __init__(self):
        # Blacklist patterns (case-insensitive regex)
        # Specific patterns to BLOCK
        self.blacklist_patterns = [
            (r'chatgpt\s+wrapper', "ChatGPT wrapper spam"),
            (r'passive\s+income', "Passive income noise"),
            (r'course\s+selling', "Course selling spam"),
            (r'no-code\s+builder', "No-code builder spam"),
            (r'crypto\s+pump', "Crypto pump spam"),
        ]
        
        # Authority names (for evidence scoring)
        self.authority_names = ['karpathy', 'lecun', 'altman', 'hassabis']
        
        # Relevance keywords (aligned with user roadmap)
        self.relevance_keywords = [
            'rtx 4090', 'gsoc', 'optimization', 'cuda', 'agentic'
        ]
        
        # Trusted domains
        self.trusted_domains = ['github.com', 'arxiv.org', 'huggingface.co']
    
    def is_garbage(self, text: str) -> bool:
        """
        Check if text matches garbage/spam patterns.
        
        Args:
            text: Input text to check
            
        Returns:
            bool: True if garbage, False if clean
        """
        text_lower = text.lower()
        
        for pattern, _ in self.blacklist_patterns:
            if re.search(pattern, text_lower):
                return True
        
        return False
    
    def calculate_score(self, text: str, metadata: Dict[str, Any] = None) -> float:
        """
        Calculate evidence-based quality score.
        
        Scoring criteria:
        - Base: 5.0 points
        - +2.0: Domain is github.com, arxiv.org, or huggingface.co
        - +1.5: Text contains code blocks (```) or terminal logs
        - +2.0: Text mentions Authority Names (Karpathy, LeCun, Altman, Hassabis)
        - +2.0: Relevance to Roadmap Keywords (RTX 4090, GSoC, Optimization, CUDA, Agentic)
        
        Args:
            text: Input text to score
            metadata: Optional metadata dict
            
        Returns:
            float: Score from 0-10, capped at 10.0
        """
        score = 5.0  # Base score
        text_lower = text.lower()
        
        # +2.0 for trusted domain links
        for domain in self.trusted_domains:
            if domain in text_lower:
                score += 2.0
                break  # Only count once
        
        # +1.5 for code blocks or terminal logs
        if '```' in text or re.search(r'\$\s+[a-z]+|>\s+[A-Z]:|C:\\\\', text):
            score += 1.5
        
        # +2.0 for authority names
        for name in self.authority_names:
            if name in text_lower:
                score += 2.0
                break  # Only count once
        
        # +2.0 for relevance keywords
        for keyword in self.relevance_keywords:
            if keyword in text_lower:
                score += 2.0
                break  # Only count once
        
        # Cap at 10.0
        return min(score, 10.0)
    
    def evaluate(self, text: str, metadata: Dict[str, Any] = None) -> Dict[str, Any]:
        """
        Complete evaluation: garbage check + scoring.
        
        Args:
            text: Input text
            metadata: Optional metadata
            
        Returns:
            dict: {
                "passed": bool,
                "score": float,
                "reason": str
            }
        """
        # Check garbage first
        if self.is_garbage(text):
            return {
                "passed": False,
                "score": 0.0,
                "reason": "Blocked by blacklist"
            }
        
        # Calculate evidence score
        score = self.calculate_score(text, metadata)
        
        return {
            "passed": True,
            "score": score,
            "reason": f"Evidence score: {score:.1f}/10"
        }


# ============================================================================
# STANDALONE USAGE / TESTING
# ============================================================================

if __name__ == "__main__":
    # Fix Windows console encoding
    import sys
    if sys.platform == "win32":
        sys.stdout.reconfigure(encoding='utf-8')
        sys.stderr.reconfigure(encoding='utf-8')
    
    print("=" * 70)
    print("🛡️  MEMORY GUARD - Test Suite")
    print("=" * 70)
    
    guard = MemoryGuard()
    
    # Test 1: Blacklist
    print("\n[TEST 1] Garbage Detection (Blacklist)")
    print("-" * 70)
    
    spam_samples = [
        "This chatgpt wrapper will make you rich!",
        "Learn passive income with my system",
        "Use this no-code builder for apps",
        "Get into this crypto pump before it moons"
    ]
    
    for sample in spam_samples:
        is_spam = guard.is_garbage(sample)
        status = "❌ BLOCKED" if is_spam else "✅ PASSED"
        print(f"{status}: {sample[:60]}")
    
    # Test 2: Evidence Scoring
    print("\n[TEST 2] Evidence-Based Scoring (Base: 5.0)")
    print("-" * 70)
    
    quality_samples = [
        "Check out github.com/karpathy/nanoGPT ```python def train()```",
        "Arxiv paper on optimization by LeCun",
        "RTX 4090 CUDA guide from huggingface.co",
        "Agentic workflows for GSoC contributors",
        "Random text about cooking recipes"
    ]
    
    for sample in quality_samples:
        score = guard.calculate_score(sample)
        rating = "🔥" if score > 7 else "⚡" if score > 5 else "📄"
        print(f"{rating} Score: {score:.1f}/10 - {sample[:50]}")
    
    # Test 3: Complete Evaluation
    print("\n[TEST 3] Complete Evaluation")
    print("-" * 70)
    
    test_cases = [
        "passive income no-code builder",
        "Basic tutorial on Python",
        "Altman's CUDA optimization guide github.com/openai ```bash nvidia-smi```"
    ]
    
    for text in test_cases:
        result = guard.evaluate(text)
        status = "✅ ACCEPT" if result["passed"] and result["score"] > 7 else "❌ REJECT"
        print(f"{status}: {text[:50]}")
        print(f"         {result['reason']}")
    
    print("\n" + "=" * 70)
    print("✅ Memory Guard tests complete")
    print("=" * 70)
