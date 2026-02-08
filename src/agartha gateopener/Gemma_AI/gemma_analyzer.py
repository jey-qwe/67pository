import requests
import json
import sys
import io

# 🧠 Конфигурация Ollama
OLLAMA_URL = "http://localhost:11434/api/generate"
MODEL = "gemma3:4b"

# 🎯 Системный промпт для Junior AI Automation Engineer
SYSTEM_PROMPT = """Ты — экспертный аналитик системы 'Ядро'. Твоя задача: фильтровать вакансии для Junior AI Automation Engineer.

Критерии оценки (0-10):
1. Python/Automation: Наличие задач по парсингу, ботам или скриптам (твоя основная практика).
2. Обучающий потенциал: Если задача требует базовых знаний API или простой логики ИИ.
3. Четкость ТЗ: Насколько понятно, что нужно делать.

Формат ответа (СТРОГИЙ JSON):
{
  "score": (число 0-10),
  "reasoning": "(кратко: почему этот заказ хорош для практики Python)",
  "bid_draft": "(профессиональный отклик, используя инструкцию ниже)"
}

Будь критичен. Если бюджет явно занижен (<$20) или описание слишком размытое — ставь score < 5.

---
ЗАПРЕТ: Если пост содержит тег [For Hire], 'I am looking for work', 'Available for hire' или это просто демонстрация готового проекта — ставь Score: 0. Нам нужны только те, кто платит деньги (Hiring, Looking for a developer, [LFG]).

---
ИНСТРУКЦИЯ ДЛЯ ГЕНЕРАЦИИ BID_DRAFT:

Роль: Ты — Junior AI Automation Engineer. Твой стек: Python (Selenium, Scrapy, Aiogram, Requests), интеграция API и локальных LLM.

Тон: Уверенный, лаконичный, ориентированный на результат. Никаких извинений за отсутствие опыта или упоминания возраста.

Структура отклика (ОБЯЗАТЕЛЬНАЯ):
1. Hook: Сразу подтверди, что ты понял техническую суть задачи (например: 'I can build a robust Python scraper to handle the dynamic content you mentioned').
2. Value: Предложи конкретный инструмент или метод решения (например: 'Using BeautifulSoup with proxy rotation to ensure 99% uptime').
3. Proof: Упомяни, что ты уже работаешь с аналогичными системами автоматизации (например: 'I'm currently running similar automation systems with API integrations').
4. CTA: Прямой призыв к действию (например: 'Let's hop on a quick chat to discuss the data format you need').

Запреты:
- Не используй фразы 'I am a 15-year-old' или 'I am from Semey'.
- Не используй шаблонное 'Dear Hiring Manager'. Сразу к делу.
- Максимум 3-4 предложения. Клиент должен прочитать это за 5 секунд.

Язык: Всегда отвечай на английском языке, если вакансия не на русском.
"""


def analyze_job(job_description: str) -> dict:
    """
    Анализирует вакансию через Ollama (gemma2:4b)
    
    Args:
        job_description: Описание вакансии
        
    Returns:
        dict: {"score": int, "reasoning": str, "bid_draft": str}
    """
    print("🧠 [ЯДРО] Подключаюсь к Ollama...")
    
    # Формируем промпт
    full_prompt = f"{SYSTEM_PROMPT}\n\nВАКАНСИЯ:\n{job_description}\n\nАНАЛИЗ:"
    
    payload = {
        "model": MODEL,
        "prompt": full_prompt,
        "stream": False,
        "temperature": 0.7,
        "max_tokens": 500
    }
    
    try:
        response = requests.post(OLLAMA_URL, json=payload, timeout=60)
        response.raise_for_status()
        
        result = response.json()
        raw_response = result.get("response", "").strip()
        
        print(f"📡 [ОТВЕТ МОДЕЛИ]:\n{raw_response}\n")
        
        # Пытаемся извлечь JSON из ответа
        json_response = extract_json(raw_response)
        
        # Валидация структуры
        validate_response(json_response)
        
        print("✅ [УСПЕХ] Анализ завершен!")
        return json_response
        
    except requests.exceptions.ConnectionError:
        print("❌ [ОШИБКА] Ollama не запущен! Запустите: ollama serve")
        return create_error_response("Ollama недоступен")
        
    except requests.exceptions.Timeout:
        print("⏱️ [ОШИБКА] Превышен timeout (60 сек)")
        return create_error_response("Timeout")
        
    except json.JSONDecodeError as e:
        print(f"❌ [ОШИБКА] Неверный JSON: {e}")
        print(f"Сырой ответ: {raw_response}")
        return create_error_response(f"Некорректный JSON от модели")
        
    except Exception as e:
        print(f"❌ [ОШИБКА] {e}")
        return create_error_response(str(e))


def extract_json(text: str) -> dict:
    """Извлекает JSON из текста (удаляет markdown и лишнее)"""
    # Убираем markdown кодблоки
    text = text.replace("```json", "").replace("```", "").strip()
    
    # Ищем первую { и последнюю }
    start = text.find("{")
    end = text.rfind("}")
    
    if start == -1 or end == -1:
        raise ValueError("JSON не найден в ответе")
    
    json_str = text[start:end+1]
    return json.loads(json_str)


def validate_response(data: dict) -> None:
    """Проверяет структуру ответа"""
    required_keys = ["score", "reasoning", "bid_draft"]
    
    for key in required_keys:
        if key not in data:
            raise ValueError(f"Отсутствует ключ: {key}")
    
    if not isinstance(data["score"], (int, float)):
        raise ValueError("score должен быть числом")
    
    if not (0 <= data["score"] <= 10):
        raise ValueError("score должен быть от 0 до 10")


def create_error_response(error_msg: str) -> dict:
    """Создает fallback ответ при ошибке"""
    return {
        "score": 0,
        "reasoning": f"Ошибка анализа: {error_msg}",
        "bid_draft": "Не удалось проанализировать вакансию"
    }


if __name__ == "__main__":
    # Настройка кодировки для Windows консоли (только при прямом запуске)
    if sys.platform == 'win32':
        sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8')
        sys.stderr = io.TextIOWrapper(sys.stderr.buffer, encoding='utf-8')
    
    # Тестовый запуск
    test_job = """
    Нужен Python разработчик для создания Telegram бота.
    Бот должен парсить данные с сайта и отправлять уведомления.
    Бюджет: $100-200. Срочно!
    """
    
    print("🚀 [ТЕСТ] Запуск анализатора вакансий...\n")
    result = analyze_job(test_job)
    print("\n📊 [РЕЗУЛЬТАТ]:")
    print(json.dumps(result, ensure_ascii=False, indent=2))
