"""
USER DATA PROFILE - VECTORIZED REPRESENTATION
Mathematical framework for prioritization, indexing, and retrieval
Based on Core Identity Vectors for AI-driven decision making
"""

import numpy as np
from typing import Dict, Tuple
from dataclasses import dataclass

# ============================================================================
# 1. CORE IDENTITY VECTORS
# ============================================================================

@dataclass
class TechnicalDomain:
    """Technical Domain Vector Space"""
    status: str = "AI Engineer (Junior-Mid)"
    primary_language: str = "Python"
    focus_areas: np.ndarray = None
    mathematical_foundation: np.ndarray = None
    
    def __post_init__(self):
        # Focus areas encoded as binary vector [CrewAI, LangChain, Ollama, RAG, Gemma]
        self.focus_areas = np.array([1, 1, 1, 1, 1], dtype=np.float32)
        
        # Math foundation [Linear Algebra, Vectors, Cosine Similarity, SVD, Optimization]
        self.mathematical_foundation = np.array([1, 1, 1, 1, 0.7], dtype=np.float32)
        
    def get_technical_vector(self) -> np.ndarray:
        """Returns combined technical capability vector"""
        return np.concatenate([self.focus_areas, self.mathematical_foundation])


@dataclass
class CreativeDomain:
    """Creative Domain Vector Space"""
    status: str = "Video Editor & Director"
    tools: np.ndarray = None
    aesthetic_vectors: np.ndarray = None
    
    def __post_init__(self):
        # Tools proficiency [After Effects, AI-VFX, Premiere, DaVinci, Blender]
        self.tools = np.array([0.9, 0.8, 0.6, 0.4, 0.3], dtype=np.float32)
        
        # Aesthetic preferences [VHS-horror, Dark Fantasy, ARG-horror, Renaissance, Cyberpunk]
        self.aesthetic_vectors = np.array([1.0, 1.0, 1.0, 0.8, 0.6], dtype=np.float32)
    
    def get_creative_vector(self) -> np.ndarray:
        """Returns combined creative capability vector"""
        return np.concatenate([self.tools, self.aesthetic_vectors])


@dataclass
class StrategicDomain:
    """Strategic & Financial Vector Space"""
    status: str = "UnderDog (Semey, Kazakhstan)"
    current_capital: float = 0.0  # KZT
    target_capital: float = 2_000_000  # KZT
    target_locations: np.ndarray = None
    active_projects: np.ndarray = None
    
    def __post_init__(self):
        # Location preferences [Japan, USA, EU, Singapore, Remote]
        self.target_locations = np.array([1.0, 1.0, 0.6, 0.5, 0.8], dtype=np.float32)
        
        # Project priority [Job Sniper, The Archivist, Portfolio, Learning, Networking]
        self.active_projects = np.array([1.0, 0.9, 0.7, 0.8, 0.6], dtype=np.float32)
    
    def get_strategic_vector(self) -> np.ndarray:
        """Returns combined strategic vector"""
        capital_progress = min(self.current_capital / self.target_capital, 1.0)
        return np.concatenate([
            self.target_locations, 
            self.active_projects,
            np.array([capital_progress])
        ])


# ============================================================================
# 2. RELEVANCE SCORING SYSTEM
# ============================================================================

class RelevanceCalculator:
    """
    Calculates Relevance Vector (R) for new information
    R = (ω₁ · Ic) + (ω₂ · It) + (ω₃ · Ia)
    """
    
    def __init__(self, 
                 weight_capital: float = 0.4,
                 weight_technical: float = 0.35,
                 weight_aesthetic: float = 0.25):
        """
        Initialize with default weights
        ω₁: Capital impact weight
        ω₂: Technical upgrade weight
        ω₃: Aesthetic synergy weight
        """
        self.ω1 = weight_capital
        self.ω2 = weight_technical
        self.ω3 = weight_aesthetic
        
        # Normalize weights to sum to 1.0
        total = self.ω1 + self.ω2 + self.ω3
        self.ω1 /= total
        self.ω2 /= total
        self.ω3 /= total
    
    def calculate_relevance(self, 
                          capital_impact: float,
                          technical_impact: float,
                          aesthetic_impact: float) -> float:
        """
        Calculate relevance score for new information
        
        Args:
            capital_impact (Ic): 0.0-1.0, impact on earning potential
            technical_impact (It): 0.0-1.0, improvement to code/AI logic
            aesthetic_impact (Ia): 0.0-1.0, match with visual style
            
        Returns:
            R: Relevance score (0.0-1.0)
        """
        R = (self.ω1 * capital_impact) + \
            (self.ω2 * technical_impact) + \
            (self.ω3 * aesthetic_impact)
        
        return R
    
    def adjust_weights(self, urgency_mode: str = "balanced"):
        """
        Adjust weights based on current urgency
        
        Modes:
        - "capital_urgent": Prioritize money-making (0.6, 0.25, 0.15)
        - "learning": Prioritize technical growth (0.2, 0.6, 0.2)
        - "creative": Prioritize aesthetic projects (0.2, 0.3, 0.5)
        - "balanced": Default balanced mode (0.4, 0.35, 0.25)
        """
        weight_profiles = {
            "capital_urgent": (0.6, 0.25, 0.15),
            "learning": (0.2, 0.6, 0.2),
            "creative": (0.2, 0.3, 0.5),
            "balanced": (0.4, 0.35, 0.25)
        }
        
        if urgency_mode in weight_profiles:
            self.ω1, self.ω2, self.ω3 = weight_profiles[urgency_mode]
        
        return self


# ============================================================================
# 3. USER PROFILE MATRIX
# ============================================================================

class UserProfile:
    """Complete user profile with all vectors and matrices"""
    
    def __init__(self):
        self.technical = TechnicalDomain()
        self.creative = CreativeDomain()
        self.strategic = StrategicDomain()
        self.relevance_calc = RelevanceCalculator()
        
        # User context
        self.age = 15
        self.location = "Semey, Kazakhstan"
        self.hardware_status = "limited"
        self.ambition_level = "unlimited"
        self.target_goal = "Ocean (Global Freedom)"
    
    def get_complete_vector(self) -> np.ndarray:
        """Returns complete user profile as single vector"""
        return np.concatenate([
            self.technical.get_technical_vector(),
            self.creative.get_creative_vector(),
            self.strategic.get_strategic_vector()
        ])
    
    def get_profile_matrix(self) -> np.ndarray:
        """Returns profile as matrix [3 domains x features]"""
        tech_vec = self.technical.get_technical_vector()
        creative_vec = self.creative.get_creative_vector()
        strategic_vec = self.strategic.get_strategic_vector()
        
        # Pad vectors to same length
        max_len = max(len(tech_vec), len(creative_vec), len(strategic_vec))
        
        tech_padded = np.pad(tech_vec, (0, max_len - len(tech_vec)))
        creative_padded = np.pad(creative_vec, (0, max_len - len(creative_vec)))
        strategic_padded = np.pad(strategic_vec, (0, max_len - len(strategic_vec)))
        
        return np.vstack([tech_padded, creative_padded, strategic_padded])
    
    def cosine_similarity(self, vec1: np.ndarray, vec2: np.ndarray) -> float:
        """Calculate cosine similarity between two vectors"""
        dot_product = np.dot(vec1, vec2)
        norm_product = np.linalg.norm(vec1) * np.linalg.norm(vec2)
        
        if norm_product == 0:
            return 0.0
        
        return dot_product / norm_product
    
    def evaluate_opportunity(self, 
                           description: str,
                           capital_impact: float,
                           technical_impact: float,
                           aesthetic_impact: float) -> Dict:
        """
        Evaluate a new opportunity (job, project, learning resource)
        
        Returns:
            Dict with relevance score, recommendation, and reasoning
        """
        relevance = self.relevance_calc.calculate_relevance(
            capital_impact, technical_impact, aesthetic_impact
        )
        
        # Categorize relevance
        if relevance >= 0.75:
            recommendation = "HIGH PRIORITY - PURSUE IMMEDIATELY"
            action = "🔥 UNDERDOG MOVE"
        elif relevance >= 0.50:
            recommendation = "MEDIUM PRIORITY - Worth Pursuing"
            action = "⚡ CONSIDER"
        elif relevance >= 0.30:
            recommendation = "LOW PRIORITY - Evaluate carefully"
            action = "🤔 REVIEW"
        else:
            recommendation = "SKIP - Low alignment with goals"
            action = "❌ PASS"
        
        return {
            "description": description,
            "relevance_score": round(relevance, 3),
            "recommendation": recommendation,
            "action": action,
            "breakdown": {
                "capital_impact": capital_impact,
                "technical_impact": technical_impact,
                "aesthetic_impact": aesthetic_impact
            },
            "weights": {
                "ω1 (capital)": self.relevance_calc.ω1,
                "ω2 (technical)": self.relevance_calc.ω2,
                "ω3 (aesthetic)": self.relevance_calc.ω3
            }
        }


# ============================================================================
# 4. USAGE EXAMPLE
# ============================================================================

if __name__ == "__main__":
    # Fix Windows console encoding for emoji support
    import sys
    import io
    sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8')
    
    # Initialize user profile
    profile = UserProfile()
    
    print("=" * 70)
    print("USER PROFILE - VECTORIZED REPRESENTATION")
    print("=" * 70)
    print(f"Status: {profile.age}-year-old UnderDog from {profile.location}")
    print(f"Goal: {profile.target_goal}")
    print()
    
    # Display complete vector
    complete_vec = profile.get_complete_vector()
    print(f"Complete Profile Vector Shape: {complete_vec.shape}")
    print(f"Profile Matrix Shape: {profile.get_profile_matrix().shape}")
    print()
    
    # Example opportunity evaluation
    print("=" * 70)
    print("EXAMPLE: Evaluating Opportunities")
    print("=" * 70)
    print()
    
    opportunities = [
        {
            "desc": "Junior AI Engineer job - Python/LangChain - $500/month",
            "Ic": 0.7, "It": 0.9, "Ia": 0.2
        },
        {
            "desc": "After Effects VFX project - Dark Fantasy theme - $300",
            "Ic": 0.5, "It": 0.3, "Ia": 1.0
        },
        {
            "desc": "RAG System tutorial - Advanced vectorization techniques",
            "Ic": 0.3, "It": 1.0, "Ia": 0.1
        },
        {
            "desc": "Generic data entry job - No skills required - $200/month",
            "Ic": 0.4, "It": 0.0, "Ia": 0.0
        }
    ]
    
    # Evaluate in capital-urgent mode
    profile.relevance_calc.adjust_weights("balanced")
    
    for opp in opportunities:
        result = profile.evaluate_opportunity(
            opp["desc"], opp["Ic"], opp["It"], opp["Ia"]
        )
        
        print(f"{result['action']} | Score: {result['relevance_score']:.3f}")
        print(f"  {result['description']}")
        print(f"  → {result['recommendation']}")
        print()
    
    print("=" * 70)
    print("VECTOR WEIGHTS (Current Mode: Balanced)")
    print("=" * 70)
    print(f"ω₁ (Capital Impact):    {profile.relevance_calc.ω1:.2f}")
    print(f"ω₂ (Technical Upgrade): {profile.relevance_calc.ω2:.2f}")
    print(f"ω₃ (Aesthetic Synergy): {profile.relevance_calc.ω3:.2f}")
    print()
    print("💡 TIP: Use .adjust_weights() to change urgency mode")
    print("   Modes: 'capital_urgent', 'learning', 'creative', 'balanced'")
