"""
Quick script to list available Gemini models and test embedding.
"""
import google.generativeai as genai
import os
from dotenv import load_dotenv

load_dotenv()

# Configure Gemini
genai.configure(api_key=os.getenv("GEMINI_API_KEY"))

print("=== Listing Available Gemini Models ===\n")

# List all available models
for model in genai.list_models():
    print(f"Model: {model.name}")
    print(f"  Supported methods: {model.supported_generation_methods}")
    print()

# Try to embed with different model names
print("\n=== Testing Embedding Methods ===\n")

test_text = "This is a test"

# Try text-embedding-004
try:
    print("Trying: text-embedding-004")
    result = genai.embed_content(
        model="text-embedding-004",
        content=test_text
    )
    print(f"SUCCESS! Dimension: {len(result['embedding'])}")
    print(f"First 5: {result['embedding'][:5]}\n")
except Exception as e:
    print(f"FAILED: {e}\n")

# Try embedding-001  
try:
    print("Trying: embedding-001")
    result = genai.embed_content(
        model="embedding-001",
        content=test_text
    )
    print(f"SUCCESS! Dimension: {len(result['embedding'])}")
    print(f"First 5: {result['embedding'][:5]}\n")
except Exception as e:
    print(f"FAILED: {e}\n")

# Try models/embedding-001
try:
    print("Trying: models/embedding-001")
    result = genai.embed_content(
        model="models/embedding-001",
        content=test_text
    )
    print(f"SUCCESS! Dimension: {len(result['embedding'])}")
    print(f"First 5: {result['embedding'][:5]}\n")
except Exception as e:
    print(f"FAILED: {e}\n")
