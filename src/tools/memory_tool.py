"""
Personal Memory Tool - The Archivist
Retrieval tool for accessing vectorized user profile data
Compatible with CrewAI (Native BaseTool)
"""

import sys
import io
from pathlib import Path
from typing import Type
from pydantic import BaseModel, Field

# Fix Windows encoding (Handled via PYTHONIOENCODING now)
# sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8')

from langchain_community.vectorstores import FAISS
from langchain_community.embeddings import HuggingFaceEmbeddings
from crewai.tools import BaseTool

# Import UTF-8 sanitization utilities
import sys
sys.path.insert(0, str(Path(__file__).parent.parent))
from utils import sanitize_for_grpc

# ============================================================================
# PATH CONFIGURATION
# ============================================================================

# Get script directory (src/tools/)
SCRIPT_DIR = Path(__file__).parent

# FAISS database: ../../faiss_db (from src/tools/ to archive/faiss_db)
FAISS_DIR = SCRIPT_DIR.parent.parent / "faiss_db"

# Embedding model (must match the one used in ingest_memory.py)
EMBEDDING_MODEL = "sentence-transformers/all-MiniLM-L6-v2"

# ============================================================================
# LOGIC IMPLEMENTATION (Internal)
# ============================================================================

class _PersonalMemoryLogic:
    """
    Internal logic for searching user's personal knowledge base
    """
    
    def __init__(self, faiss_path: str = None, model_name: str = None):
        self.faiss_path = faiss_path or str(FAISS_DIR)
        self.model_name = model_name or EMBEDDING_MODEL
        self.embeddings = None
        self.vectorstore = None
        
    def _load_embeddings(self):
        if self.embeddings is None:
            self.embeddings = HuggingFaceEmbeddings(
                model_name=self.model_name,
                model_kwargs={'device': 'cpu'},
                encode_kwargs={'normalize_embeddings': True}
            )
        return self.embeddings
    
    def _load_vectorstore(self):
        if self.vectorstore is None:
            embeddings = self._load_embeddings()
            self.vectorstore = FAISS.load_local(
                self.faiss_path,
                embeddings,
                allow_dangerous_deserialization=True
            )
        return self.vectorstore
    
    def search(self, query: str, k: int = 3) -> str:
        try:
            db = self._load_vectorstore()
            results = db.similarity_search(query, k=k)
            
            if not results:
                return "No relevant information found in personal knowledge base."
            
            formatted_results = []
            for i, doc in enumerate(results, 1):
                clean_content = sanitize_for_grpc(doc.page_content)
                formatted_results.append(f"[Result {i}]\n{clean_content}")
            
            return "\n\n".join(formatted_results)
            
        except Exception as e:
            return f"Error searching memory: {str(e)}"

# Global instance for the logic
_logic_instance = _PersonalMemoryLogic()

# ============================================================================
# INPUT SCHEMA
# ============================================================================

class SearchMemoryInput(BaseModel):
    """Input schema for search_personal_memory."""
    query: str = Field(..., description="The query string to search for in the user's personal memory.")

# ============================================================================
# CREWAI TOOL DEFINITION
# ============================================================================

class PersonalMemoryTool(BaseTool):
    name: str = "search_personal_memory"
    description: str = (
        "Search the user's personal knowledge base for relevant information about "
        "skills, goals, projects, and preferences."
    )
    args_schema: Type[BaseModel] = SearchMemoryInput

    def _run(self, query: str) -> str:
        return _logic_instance.search(query, k=3)

# Export an instance of the tool
search_personal_memory = PersonalMemoryTool()

# ============================================================================
# STANDALONE USAGE
# ============================================================================

def main():
    print("=" * 70)
    print("🧠 Personal Memory Tool - Test (CrewAI Native)")
    print("=" * 70)
    
    tool = PersonalMemoryTool()
    
    queries = [
        "What are my technical skills?",
        "What are my career goals?"
    ]
    
    for q in queries:
        print(f"\n📊 Query: '{q}'")
        print("-" * 70)
        print(tool._run(q))
        print()

if __name__ == "__main__":
    main()
