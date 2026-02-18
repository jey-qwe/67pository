"""
Trinity Context Core - Application Entry Point

Run this file from the project root to start the server.
"""
import sys
from pathlib import Path

# Add project root to Python path
project_root = Path(__file__).parent
sys.path.insert(0, str(project_root))

# Now import and run the app
if __name__ == "__main__":
    import uvicorn
    
    print("=" * 60)
    print("Trinity Context Core - Starting Server")
    print("=" * 60)
    print(f"Project root: {project_root}")
    print()
    
    uvicorn.run(
        "src.main:app",
        host="0.0.0.0",
        port=8000,
        reload=True
    )
