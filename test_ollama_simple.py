"""
Simple Ollama connectivity test
"""
import requests
import json

print("[TEST] Testing Ollama Connection...\n")

# Test 1: Check if Ollama is running
print("[1] Checking Ollama server...")
try:
    response = requests.get("http://localhost:11434/api/tags", timeout=5)
    if response.status_code == 200:
        print("   [OK] Ollama server is running")
        models = response.json().get('models', [])
        print(f"   [MODELS] Available models: {len(models)}")
        for model in models:
            print(f"      - {model['name']}")
    else:
        print(f"   [ERROR] Server returned status: {response.status_code}")
except Exception as e:
    print(f"   [ERROR] Cannot connect to Ollama: {e}")
    exit(1)

# Test 2: Try to generate with gemma3:4b
print("\n[2] Testing gemma3:4b model...")
try:
    payload = {
        "model": "gemma3:4b",
        "prompt": "Say hello",
        "stream": False
    }
    response = requests.post(
        "http://localhost:11434/api/generate",
        json=payload,
        timeout=30
    )
    
    if response.status_code == 200:
        result = response.json()
        print(f"   [OK] Model responded: {result.get('response', '')[:100]}")
    else:
        print(f"   [ERROR] API returned {response.status_code}: {response.text}")
except Exception as e:
    print(f"   [ERROR] Generation failed: {e}")
    import traceback
    traceback.print_exc()

print("\n[COMPLETE] Test complete!")
