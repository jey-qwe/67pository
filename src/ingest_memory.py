"""
RAG INGESTION SCRIPT - The Archivist
Converts user_data.md into vectors and stores locally
Uses local HuggingFace embeddings (no API required)
Uses FAISS for vector storage (no C++ build tools needed)
"""

import sys
import io
import os
from pathlib import Path
import shutil
import pickle

# --- ЖЕЛЕЗНЫЙ КУПОЛ (НАЧАЛО) ---

# 1. Затыкаем рот OpenAI (чтобы CrewAI даже не думал туда стучаться)
os.environ["OPENAI_API_KEY"] = "NA"
os.environ["OPENAI_MODEL_NAME"] = "NA"

# 2. Принудительная кодировка (лечит ошибку "invalid UTF-8" из логов)
os.environ["PYTHONIOENCODING"] = "utf-8"
os.environ["LANG"] = "C.UTF-8"

# 3. Перехват вывода (чтобы Windows консоль не крашилась от эмодзи)
if sys.platform == "win32":
    sys.stdout.reconfigure(encoding='utf-8')
    sys.stderr.reconfigure(encoding='utf-8')

# --- ЖЕЛЕЗНЫЙ КУПОЛ (КОНЕЦ) ---

from langchain_community.document_loaders import TextLoader
from langchain_text_splitters import RecursiveCharacterTextSplitter
from langchain_community.embeddings import HuggingFaceEmbeddings
from langchain_community.vectorstores import FAISS

# Import UTF-8 sanitization utilities
from utils import sanitize_for_grpc

# ============================================================================
# PATH CONFIGURATION
# ============================================================================

# Get script directory (src/)
SCRIPT_DIR = Path(__file__).parent

# Data file: ../data/user_data.md
DATA_FILE = SCRIPT_DIR.parent / "data" / "user_data.md"

# FAISS DB: ../faiss_db
FAISS_DIR = SCRIPT_DIR.parent / "faiss_db"

# ============================================================================
# CONFIGURATION
# ============================================================================

CHUNK_SIZE = 500
CHUNK_OVERLAP = 50
EMBEDDING_MODEL = "sentence-transformers/all-MiniLM-L6-v2"

# ============================================================================
# MAIN INGESTION LOGIC
# ============================================================================

def ensure_clean_db():
    """Remove existing FAISS DB to ensure idempotency"""
    if FAISS_DIR.exists():
        print(f"🗑️  Removing existing database at {FAISS_DIR}")
        shutil.rmtree(FAISS_DIR)
        print("✅ Old database removed")
    else:
        print("📂 No existing database found")


def load_user_data():
    """Load user_data.md from data directory"""
    print(f"\n📖 Loading data from: {DATA_FILE}")
    
    if not DATA_FILE.exists():
        raise FileNotFoundError(f"❌ Data file not found: {DATA_FILE}")
    
    loader = TextLoader(str(DATA_FILE), encoding='utf-8')
    documents = loader.load()
    
    print(f"✅ Loaded {len(documents)} document(s)")
    print(f"   Total characters: {sum(len(doc.page_content) for doc in documents)}")
    
    return documents


def split_documents(documents):
    """Split documents into chunks"""
    print(f"\n✂️  Splitting documents...")
    print(f"   Chunk size: {CHUNK_SIZE} characters")
    print(f"   Overlap: {CHUNK_OVERLAP} characters")
    
    text_splitter = RecursiveCharacterTextSplitter(
        chunk_size=CHUNK_SIZE,
        chunk_overlap=CHUNK_OVERLAP,
        length_function=len,
        separators=["\n\n", "\n", ". ", " ", ""]
    )
    
    chunks = text_splitter.split_documents(documents)
    
    print(f"✅ Created {len(chunks)} chunks")
    
    # Sanitize all chunks to prevent UTF-8 encoding errors
    print(f"\n🧹 Sanitizing text for UTF-8 compliance...")
    for chunk in chunks:
        chunk.page_content = sanitize_for_grpc(chunk.page_content)
    print(f"✅ All chunks sanitized")
    
    # Show sample chunk
    if chunks:
        print(f"\n📄 Sample chunk:")
        preview = chunks[0].page_content[:100].replace('\n', ' ')
        print(f"   '{preview}...'")
    
    return chunks


def create_embeddings():
    """Initialize HuggingFace embeddings (local, no API)"""
    print(f"\n🧠 Initializing embeddings model...")
    print(f"   Model: {EMBEDDING_MODEL}")
    print(f"   ⚡ Running locally (no API required)")
    print(f"   ⏳ First run will download the model...")
    
    embeddings = HuggingFaceEmbeddings(
        model_name=EMBEDDING_MODEL,
        model_kwargs={'device': 'cpu'},  # Use 'cuda' if you have GPU
        encode_kwargs={'normalize_embeddings': True}
    )
    
    print("✅ Embeddings model ready")
    
    return embeddings


def store_in_faiss(chunks, embeddings):
    """Store chunks in FAISS vector database"""
    print(f"\n💾 Creating vector database...")
    print(f"   Location: {FAISS_DIR}")
    print(f"   Vector store: FAISS (local, high-performance)")
    
    # Create FAISS directory
    FAISS_DIR.mkdir(parents=True, exist_ok=True)
    
    # Create FAISS vector store
    vectorstore = FAISS.from_documents(
        documents=chunks,
        embedding=embeddings
    )
    
    # Save to disk
    vectorstore.save_local(str(FAISS_DIR))
    
    print(f"✅ Stored {len(chunks)} chunks in FAISS")
    
    return vectorstore


def verify_storage(vectorstore):
    """Verify that vectors were stored correctly"""
    print(f"\n🔍 Verifying storage...")
    
    # Test similarity search
    test_queries = [
        "AI Engineer",
        "Video editing",
        "Kazakhstan"
    ]
    
    print(f"✅ Database is functional\n")
    
    for query in test_queries:
        results = vectorstore.similarity_search(query, k=2)
        
        print(f"📊 Test query: '{query}'")
        if results:
            preview = results[0].page_content[:100].replace('\n', ' ')
            print(f"   Top match: '{preview}...'")
        print()
    
    return True


def main():
    """Main ingestion pipeline"""
    print("=" * 70)
    print("🚀 THE ARCHIVIST - RAG Ingestion Pipeline")
    print("=" * 70)
    print(f"📍 Working directory: {Path.cwd()}")
    print(f"📍 Script location: {SCRIPT_DIR}")
    
    try:
        # Step 1: Clean existing database
        ensure_clean_db()
        
        # Step 2: Load user data
        documents = load_user_data()
        
        # Step 3: Split into chunks
        chunks = split_documents(documents)
        
        # Step 4: Create embeddings
        embeddings = create_embeddings()
        
        # Step 5: Store in FAISS
        vectorstore = store_in_faiss(chunks, embeddings)
        
        # Step 6: Verify
        verify_storage(vectorstore)
        
        print("=" * 70)
        print("✅ INGESTION COMPLETE - UnderDog Knowledge Base Ready!")
        print("=" * 70)
        print(f"📂 Database location: {FAISS_DIR.resolve()}")
        print(f"🎯 Ready for retrieval queries!")
        print(f"\n💡 Next step: Create query_memory.py to search your knowledge")
        print(f"🔥 Your personal AI is one step closer to the Ocean!")
        
    except Exception as e:
        print(f"\n❌ ERROR: {type(e).__name__}")
        print(f"   {str(e)}")
        import traceback
        traceback.print_exc()
        sys.exit(1)


if __name__ == "__main__":
    main()
