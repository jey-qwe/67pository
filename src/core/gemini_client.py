"""
Google Gemini API client for generating embeddings.
"""
import os
import time
from typing import List, Optional
from dotenv import load_dotenv
import google.generativeai as genai

# Load environment variables
load_dotenv()

# Configure Gemini API
GEMINI_API_KEY = os.getenv("GEMINI_API_KEY")
if GEMINI_API_KEY:
    genai.configure(api_key=GEMINI_API_KEY)


def get_embedding(
    text: str,
    model: str = "models/gemini-embedding-001",
    max_retries: int = 3,
    retry_delay: int = 2
) -> Optional[List[float]]:
    """
    Generate text embedding using Google Gemini API.
    
    Args:
        text: Input text to generate embedding for
        model: Gemini embedding model to use (default: text-embedding-004)
        max_retries: Maximum number of retry attempts on failure
        retry_delay: Delay in seconds between retries
        
    Returns:
        List of float values representing the text embedding, or None on failure
        
    Raises:
        ValueError: If GEMINI_API_KEY is not configured
    """
    if not GEMINI_API_KEY:
        raise ValueError(
            "GEMINI_API_KEY not found in environment variables. "
            "Please set it in your .env file."
        )
    
    if not text or not text.strip():
        raise ValueError("Text cannot be empty")
    
    for attempt in range(max_retries):
        try:
            # Generate embedding using Gemini API
            result = genai.embed_content(
                model=model,
                content=text,
                task_type="retrieval_document"
            )
            
            # Extract embedding from result
            embedding = result.get("embedding")
            
            if embedding is None:
                raise ValueError("No embedding returned from API")
            
            return embedding
            
        except Exception as e:
            error_message = str(e).lower()
            
            # Check for rate limit errors
            if "rate limit" in error_message or "quota" in error_message:
                if attempt < max_retries - 1:
                    wait_time = retry_delay * (2 ** attempt)  # Exponential backoff
                    print(f"Rate limit hit. Retrying in {wait_time} seconds... (Attempt {attempt + 1}/{max_retries})")
                    time.sleep(wait_time)
                    continue
                else:
                    print(f"Rate limit exceeded after {max_retries} attempts")
                    return None
            
            # Check for API key errors
            elif "api key" in error_message or "authentication" in error_message:
                print(f"Authentication error: {e}")
                return None
            
            # Other errors
            else:
                if attempt < max_retries - 1:
                    print(f"Error generating embedding: {e}. Retrying... (Attempt {attempt + 1}/{max_retries})")
                    time.sleep(retry_delay)
                    continue
                else:
                    print(f"Failed to generate embedding after {max_retries} attempts: {e}")
                    return None
    
    return None


def get_query_embedding(
    query: str,
    model: str = "models/gemini-embedding-001"
) -> Optional[List[float]]:
    """
    Generate query embedding for semantic search.
    
    Args:
        query: Search query text
        model: Gemini embedding model to use
        
    Returns:
        List of float values representing the query embedding, or None on failure
    """
    if not GEMINI_API_KEY:
        raise ValueError(
            "GEMINI_API_KEY not found in environment variables. "
            "Please set it in your .env file."
        )
    
    if not query or not query.strip():
        raise ValueError("Query cannot be empty")
    
    try:
        result = genai.embed_content(
            model=model,
            content=query,
            task_type="retrieval_query"
        )
        
        embedding = result.get("embedding")
        
        if embedding is None:
            raise ValueError("No embedding returned from API")
        
        return embedding
        
    except Exception as e:
        print(f"Error generating query embedding: {e}")
        return None
