"""
Archivarius - The Active Memory Agent
Self-reflecting memory system with Deep Think capabilities
Part of Archivarius 2.0 Active Memory System
"""

import logging
import os
from pathlib import Path
from typing import Dict, Any, Optional
from datetime import datetime

# LangChain LLM
from langchain_ollama import ChatOllama
from langchain_core.prompts import ChatPromptTemplate
from langchain_core.output_parsers import JsonOutputParser

# RAG Dependencies
from langchain_community.embeddings import HuggingFaceEmbeddings
from langchain_community.vectorstores import FAISS
from langchain_core.documents import Document

# Memory Guard
import sys
sys.path.insert(0, str(Path(__file__).parent.parent))
from core.memory_guard import MemoryGuard

# Utilities
try:
    from utils import sanitize_for_grpc
except ImportError:
    def sanitize_for_grpc(text):
        return text.encode('utf-8', 'ignore').decode('utf-8')


logger = logging.getLogger(__name__)


class Archivarius:
    """
    The Active Memory Agent.
    Filters garbage, reflects deeply, and only saves valuable knowledge.
    """
    
    def __init__(self, 
                 model_name: str = "gemma3:4b",
                 faiss_path: Optional[str] = None,
                 embedding_model: str = "sentence-transformers/all-MiniLM-L6-v2"):
        """
        Initialize Archivarius with LLM and Memory Guard.
        
        Args:
            model_name: Ollama model for Deep Think (default: gemma:2b)
            faiss_path: Path to FAISS database (auto-detected if None)
            embedding_model: HuggingFace embedding model
        """
        self.llm = ChatOllama(model=model_name, temperature=0.3)
        self.guard = MemoryGuard()
        self.embedding_model = embedding_model
        
        # Initialize embeddings
        self.embeddings = HuggingFaceEmbeddings(
            model_name=self.embedding_model,
            model_kwargs={'device': 'cpu'},
            encode_kwargs={'normalize_embeddings': True}
        )
        
        # Find or create FAISS database
        self.faiss_path = self._locate_faiss_db(faiss_path)
        self.vectorstore = self._load_or_create_vectorstore()
        
        logger.info(f"🧠 Archivarius initialized with {model_name}")
        logger.info(f"📂 FAISS DB: {self.faiss_path}")
    
    def _locate_faiss_db(self, faiss_path: Optional[str]) -> str:
        """
        Locate FAISS database, trying multiple possible paths.
        """
        if faiss_path and Path(faiss_path).exists():
            return faiss_path
        
        # Try common locations
        possible_paths = [
            Path("C:/Users/guyla/Desktop/archive/faiss_db"),
            Path(__file__).parent.parent.parent / "faiss_db",
            Path("faiss_db"),
            Path("../faiss_db"),
            Path("../../faiss_db"),
        ]
        
        for p in possible_paths:
            if p.exists():
                return str(p.resolve())
        
        # Default: create in archive/faiss_db
        default_path = Path("C:/Users/guyla/Desktop/archive/faiss_db")
        return str(default_path)
    
    def _load_or_create_vectorstore(self) -> FAISS:
        """
        Load existing FAISS vectorstore or create new one.
        """
        faiss_path = Path(self.faiss_path)
        
        if faiss_path.exists() and (faiss_path / "index.faiss").exists():
            # Load existing
            try:
                vectorstore = FAISS.load_local(
                    str(faiss_path),
                    self.embeddings,
                    allow_dangerous_deserialization=True
                )
                logger.info(f"✅ Loaded existing FAISS DB from {faiss_path}")
                return vectorstore
            except Exception as e:
                logger.warning(f"⚠️ Failed to load FAISS DB: {e}. Creating new one.")
        
        # Create new vectorstore
        faiss_path.mkdir(parents=True, exist_ok=True)
        
        # Initialize with dummy document
        dummy_doc = Document(
            page_content="Archivarius Active Memory System initialized.",
            metadata={
                "source": "system",
                "timestamp": datetime.now().isoformat(),
                "score": 10.0,
                "priority": "system"
            }
        )
        
        vectorstore = FAISS.from_documents([dummy_doc], self.embeddings)
        vectorstore.save_local(str(faiss_path))
        logger.info(f"✅ Created new FAISS DB at {faiss_path}")
        
        return vectorstore
    
    def _deep_think(self, text: str) -> str:
        """
        Deep Think Engine - LLM-powered self-reflection.
        Simplified version that returns RELEVANT or NOISE.
        
        Args:
            text: Information to analyze
            
        Returns:
            str: "RELEVANT" or "NOISE"
        """
        system_prompt = """You are an internal filter for an AI Engineer.

USER GOALS:
1. Buy an RTX 4090 GPU
2. Win Google Summer of Code (GSoC) 2026
3. Optimize RAM usage and system performance

Does this information help achieve these goals?

If YES (relevant, actionable, technical): Return exactly "RELEVANT"
If NO (generic noise, unrelated topics, vague advice): Return exactly "NOISE"

TEXT TO ANALYZE:
{text}"""

        prompt = ChatPromptTemplate.from_messages([
            ("system", system_prompt),
            ("human", "Analyze this.")
        ])
        
        # Use StrOutputParser instead of JsonOutputParser for simple string output
        from langchain_core.output_parsers import StrOutputParser
        chain = prompt | self.llm | StrOutputParser()
        
        try:
            logger.info("🧠 Deep Think: Analyzing relevance...")
            result = chain.invoke({"text": text}).strip().upper()
            
            # Ensure response is either RELEVANT or NOISE
            if "RELEVANT" in result:
                return "RELEVANT"
            else:
                return "NOISE"
            
        except Exception as e:
            logger.error(f"❌ Deep Think failed: {e}")
            return "NOISE"  # Default to NOISE on error
    
    def _save_to_faiss(self, text: str, metadata: Dict[str, Any], score: float):
        """
        Save approved content to FAISS vectorstore.
        
        Args:
            text: Content to save
            metadata: Metadata dict
            score: Evidence score
        """
        # Sanitize text
        clean_text = sanitize_for_grpc(text)
        
        # Prepare metadata
        full_metadata = {
            **metadata,
            "score": score,
            "timestamp": datetime.now().isoformat(),
            "source": "archivarius"
        }
        
        # Create document
        doc = Document(
            page_content=clean_text,
            metadata=full_metadata
        )
        
        # Add to vectorstore
        self.vectorstore.add_documents([doc])
        
        # Save to disk
        self.vectorstore.save_local(self.faiss_path)
        
        logger.info(f"💾 Saved to FAISS (score: {score:.1f}, priority: {metadata.get('priority', 'N/A')})")
    
    def learn(self, text: str, metadata: Optional[Dict[str, Any]] = None) -> bool:
        """
        Main learning pipeline: Guard → Deep Think → Score → Save.
        
        Strict filtering funnel:
        1. Blacklist check (reject garbage)
        2. Deep Think (reject NOISE)
        3. Evidence score (reject if score < 7.0)
        4. Save to FAISS with #Priority_Alpha tag
        
        Args:
            text: Information to learn
            metadata: Optional metadata dict
            
        Returns:
            bool: True if saved, False if rejected
        """
        if metadata is None:
            metadata = {}
        
        logger.info("=" * 70)
        logger.info("📚 ARCHIVARIUS: New learning request")
        logger.info("=" * 70)
        
        # STEP 1: Guard Check (Blacklist)
        logger.info("🛡️  [1/4] Memory Guard: Blacklist check...")
        
        if self.guard.is_garbage(text):
            logger.warning("❌ REJECTED: Blocked by Blacklist")
            logger.info(f"   Text preview: {text[:100]}...")
            return False
        
        logger.info("✅ Passed blacklist")
        
        # STEP 2: Deep Think
        logger.info("🧠 [2/4] Deep Think: Self-reflection...")
        think_result = self._deep_think(text)
        
        if think_result == "NOISE":
            logger.warning("❌ REJECTED: Blocked by Deep Think")
            logger.info("   Reasoning: Information not relevant to roadmap goals")
            return False
        
        logger.info("✅ RELEVANT to roadmap!")
        
        # STEP 3: Evidence Score
        logger.info("📊 [3/4] Evidence scoring...")
        score = self.guard.calculate_score(text, metadata)
        logger.info(f"   Score: {score:.1f}/10")
        
        if score < 7.0:
            logger.warning(f"❌ REJECTED: Low Score (threshold: 7.0)")
            return False
        
        logger.info(f"✅ High quality score!")
        
        # STEP 4: Save to FAISS with Priority Tag
        logger.info("💾 [4/4] Saving to FAISS...")
        
        # Add #Priority_Alpha tag to all saved content
        metadata["tags"] = metadata.get("tags", []) + ["#Priority_Alpha"]
        metadata["priority"] = "alpha"
        
        self._save_to_faiss(text, metadata, score)
        
        logger.info("=" * 70)
        logger.info("✅ LEARNING COMPLETE - Information archived with #Priority_Alpha")
        logger.info("=" * 70)
        
        return True
    
    def recall(self, query: str, k: int = 3) -> str:
        """
        Recall information from memory.
        
        Args:
            query: Search query
            k: Number of results
            
        Returns:
            str: Formatted results
        """
        try:
            results = self.vectorstore.similarity_search(query, k=k)
            
            if not results:
                return "No relevant memories found."
            
            formatted = []
            for i, doc in enumerate(results, 1):
                clean_content = sanitize_for_grpc(doc.page_content)
                score = doc.metadata.get("score", "N/A")
                priority = doc.metadata.get("priority", "N/A")
                
                formatted.append(
                    f"[Memory {i}] (Score: {score}, Priority: {priority})\n{clean_content}"
                )
            
            return "\n\n".join(formatted)
            
        except Exception as e:
            logger.error(f"❌ Recall failed: {e}")
            return f"Error recalling memories: {str(e)}"


# ============================================================================
# STANDALONE USAGE / TESTING
# ============================================================================

if __name__ == "__main__":
    import sys
    
    # Fix Windows console encoding
    if sys.platform == "win32":
        sys.stdout.reconfigure(encoding='utf-8')
        sys.stderr.reconfigure(encoding='utf-8')
    
    # Setup logging
    logging.basicConfig(
        level=logging.INFO,
        format='%(message)s'
    )
    
    print("=" * 70)
    print("🧠 ARCHIVARIUS - Active Memory System Test")
    print("=" * 70)
    
    # Initialize
    arch = Archivarius()
    
    print("\n[TEST 1] Blacklist Rejection")
    print("-" * 70)
    spam = "This chatgpt wrapper will give you passive income!"
    result = arch.learn(spam)
    print(f"Result: {'❌ Rejected' if not result else '✅ Saved'} (Expected: ❌ Rejected)")
    
    print("\n[TEST 2] Low Evidence Score Rejection")
    print("-" * 70)
    low_quality = "Some random thoughts about life and meditation"
    result = arch.learn(low_quality)
    print(f"Result: {'❌ Rejected' if not result else '✅ Saved'} (Expected: ❌ Rejected)")
    
    print("\n[TEST 3] High-Quality Relevant Content")
    print("-" * 70)
    quality = """
    RTX 4090 optimization guide for AI workloads.
    Check out this github.com/nvidia/cuda-samples repository.
    ```python
    import torch
    device = torch.device('cuda' if torch.cuda.is_available() else 'cpu')
    ```
    Tips for GSoC 2026 contributors on GPU computing.
    """
    result = arch.learn(quality, metadata={"source": "test"})
    print(f"Result: {'❌ Rejected' if not result else '✅ Saved'} (Expected: ✅ Saved)")
    
    print("\n[TEST 4] Memory Recall")
    print("-" * 70)
    if result:  # If previous test saved something
        recall_result = arch.recall("RTX 4090 GPU optimization")
        print(f"Recall result:\n{recall_result}")
    
    print("\n" + "=" * 70)
    print("✅ Archivarius tests complete")
    print("=" * 70)
