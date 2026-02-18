"""
Trinity Context Core - Gemini Connection Test

Tests the connection to Gemini API and verifies embedding generation.
"""
import sys
from pathlib import Path

# Add project root to path
project_root = Path(__file__).parent.parent.parent
sys.path.insert(0, str(project_root))

from src.core.gemini_client import get_embedding


def test_gemini_connection():
    """
    Test Gemini API connection by generating an embedding.
    """
    print("=" * 60)
    print("Trinity Context Core - Gemini Connection Test")
    print("=" * 60)
    print()
    
    test_phrase = "Тест связи с Фукуокой"
    print(f"Тестовая фраза: '{test_phrase}'")
    print("Генерация вектора...\n")
    
    try:
        # Generate embedding
        vector = get_embedding(test_phrase)
        
        # Check if vector was generated
        if vector is None:
            print("[FAILED] Вектор не был сгенерирован (получен None)")
            print("Проверьте GEMINI_API_KEY в файле .env")
            return 1
        
        # Success output
        print("=" * 60)
        print("[SUCCESS] Вектор успешно получен!")
        print("=" * 60)
        print()
        
        # Vector dimension
        print(f"Размерность вектора: {len(vector)}")
        
        # Check if dimension is expected
        expected_dim = 3072
        if len(vector) == expected_dim:
            print(f"[OK] Размерность соответствует ожиданиям ({expected_dim})")
        else:
            print(f"[WARNING] Ожидалась размерность {expected_dim}, получено {len(vector)}")
        
        print()
        
        # Show first 5 values
        print("Первые 5 значений вектора:")
        for i, value in enumerate(vector[:5], 1):
            print(f"  [{i}] {value:.6f}")
        
        print()
        print("=" * 60)
        print("[COMPLETE] Gemini API работает корректно!")
        print("=" * 60)
        
        return 0
        
    except Exception as e:
        print("=" * 60)
        print("[ERROR] Ошибка при подключении к Gemini API")
        print("=" * 60)
        print()
        print(f"Тип ошибки: {type(e).__name__}")
        print(f"Текст ошибки: {str(e)}")
        print()
        print("Возможные причины:")
        print("  1. GEMINI_API_KEY не установлен или неверный")
        print("  2. Нет интернет-соединения")
        print("  3. API Gemini недоступен")
        print("  4. Превышен лимит запросов")
        print()
        print("Проверьте файл .env и убедитесь, что GEMINI_API_KEY корректен")
        print("=" * 60)
        
        return 1


if __name__ == "__main__":
    sys.exit(test_gemini_connection())
