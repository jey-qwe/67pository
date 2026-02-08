
import logging
import os
from pathlib import Path
from typing import Dict, Any
from langchain_ollama import ChatOllama
from langchain_core.prompts import ChatPromptTemplate
from langchain_core.output_parsers import JsonOutputParser

# RAG Dependencies
from langchain_community.embeddings import HuggingFaceEmbeddings
from langchain_community.vectorstores import FAISS

# Utility Dependencies
try:
    from src.utils import sanitize_for_grpc
except ImportError:
    # Fallback if run as script or relative import issue
    try:
        from ..utils import sanitize_for_grpc
    except ImportError:
         def sanitize_for_grpc(text): return text.encode('utf-8', 'ignore').decode('utf-8')

logger = logging.getLogger(__name__)

class BrainAgent:
    """
    The Intelligence Layer.
    Uses ChatOllama to analyze jobs and critique decisions.
    Integrated with Personal RAG Memory.
    """
    def __init__(self, model_name: str = "gemma3:4b"):
        self.llm = ChatOllama(model=model_name, temperature=0.7)
        self.vectorstore = None
        self._load_memory()
        logger.info(f"🧠 Brain initialized with {model_name} + RAG")

    def _load_memory(self):
        """Loads the FAISS database from the archive directory."""
        try:
            # Path to FAISS DB: c:/Users/guyla/Desktop/archive/faiss_db
            # Calculated relative to this script: 
            # src/agents/brain.py -> src/agents -> src -> agartha gateopener -> src -> archive -> faiss_db
            # Actually, let's look for it in the known location.
            
            # Assuming current CWD is .../agartha gateopener
            # faiss is at ../../../faiss_db
            
            # Robust logic: Try absolute first, then relative
            possible_paths = [
                Path("C:/Users/guyla/Desktop/archive/faiss_db"),
                Path("../../../faiss_db"),
                Path("../../faiss_db"),
                Path("faiss_db")
            ]
            
            db_path = None
            for p in possible_paths:
                if p.exists():
                    db_path = str(p)
                    break
            
            if not db_path:
                logger.warning("⚠️ FAISS DB not found. Running without memory.")
                return

            embeddings = HuggingFaceEmbeddings(
                model_name="sentence-transformers/all-MiniLM-L6-v2",
                model_kwargs={'device': 'cpu'},
                encode_kwargs={'normalize_embeddings': True}
            )
            
            self.vectorstore = FAISS.load_local(
                db_path, 
                embeddings, 
                allow_dangerous_deserialization=True
            )
            logger.info(f"🧠 Loaded Personal Memory from {db_path}")
            
        except Exception as e:
            logger.error(f"❌ Failed to load memory: {e}")

    def _retrieve_context(self, query: str) -> str:
        """Retrieves relevant personal skills/experience."""
        if not self.vectorstore:
            return ""
        
        try:
            docs = self.vectorstore.similarity_search(query, k=2)
            if not docs:
                return ""
            
            context_str = "\n".join([f"- {sanitize_for_grpc(d.page_content)}" for d in docs])
            return context_str
        except Exception as e:
            logger.error(f"❌ Retrieval error: {e}")
            return ""

    def analyze_job(self, job_description: str) -> Dict[str, Any]:
        """
        Analyzes a job description to determine if it's a good fit.
        Uses RAG to compare with user skills.
        """
        # 0. Sanitize Input
        job_description = sanitize_for_grpc(job_description)

        # 1. Retrieve Context
        user_context = self._retrieve_context(job_description[:500]) # Use first 500 chars as query
        
        context_block = ""
        if user_context:
            context_block = f"\nUSER SKILLS & EXPERIENCE:\n{user_context}\n"
            logger.info("🧠 Using RAG Context for analysis")
        
        system_prompt = f"""You are an expert recruitment analyst for a Junior AI Automation Engineer.
Your task is to filter freelance jobs based on the User's Skills.{context_block}

Criteria (0-10):
1. Skill Match: Does the job match the USER SKILLS above? (Bonus if exact match).
2. Python/Automation: Involves scraping, bots, scripts, or API integration.
3. Clarity: Clear requirements.
4. Budget: Avoid very low budget checks (<$20).

Output strictly JSON:
{{{{
  "score": (int 0-10, boost if matches User Skills),
  "reasoning": (short text, mention if it matches specific user skills),
  "bid_draft": (professional detailed proposal, max 3 sentences, no filler. Mention specific matching experience from User Skills if applicable).
}}}}

Be critical. If it's just "I need a fix" or "data entry", score low.
"""
        prompt = ChatPromptTemplate.from_messages([
            ("system", system_prompt),
            ("human", "JOB DESCRIPTION:\n{job}")
        ])
        
        chain = prompt | self.llm | JsonOutputParser()
        
        try:
            logger.info("🧠 Brain analyzing job...")
            result = chain.invoke({"job": job_description})
            # Ensure keys exist
            if 'score' not in result:
                result['score'] = 0
            if 'reasoning' not in result:
                result['reasoning'] = "Error in analysis"
            return result
        except Exception as e:
            logger.error(f"❌ Analysis failed: {e}")
            return {"score": 0, "reasoning": f"Failed: {e}", "bid_draft": ""}

    def critique_decision(self, analysis: Dict[str, Any]) -> Dict[str, Any]:
        """
        Critiques the initial analysis to ensure quality control.
        """
        system_prompt = """You are a Senior Python Architect.
Review this job analysis performed by a Junior Scout.

Analysis:
Score: {score}
Reasoning: {reasoning}
Bid Draft: {bid_draft}

Is this a valid assessment? 
If the score is high (>6), verify if the reasoning makes sense for an Automation Engineer.
If the bid looks robotic, flag it.

Output strictly JSON:
{{{{
  "valid": (boolean),
  "feedback": (short critique),
  "refined_score": (int 0-10, adjusted score)
}}}}
"""
        prompt = ChatPromptTemplate.from_messages([
            ("system", system_prompt),
            ("human", "Review this.")
        ])
        
        chain = prompt | self.llm | JsonOutputParser()
        
        try:
            logger.info("🧐 Critic reviewing analysis...")
            result = chain.invoke(analysis)
            return result
        except Exception as e:
            logger.error(f"❌ Critique failed: {e}")
            return {"valid": True, "feedback": "Critique failed, passing through.", "refined_score": analysis.get('score', 0)}
