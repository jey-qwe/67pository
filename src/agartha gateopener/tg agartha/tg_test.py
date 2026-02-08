"""
Telegram Bot Message Sender
Простой скрипт для отправки сообщений через Telegram Bot API
"""

import requests
import sys
import io

# Настройка кодировки для консоли Windows
if sys.platform == "win32":
    sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8')
    sys.stderr = io.TextIOWrapper(sys.stderr.buffer, encoding='utf-8')

# ============================================
# НАСТРОЙКИ - ВСТАВЬТЕ СВОИ ЗНАЧЕНИЯ ЗДЕСЬ
# ============================================
BOT_TOKEN = "8589971935:AAFioziazQKlbTsvN3Q0b9g_ijxVtCspIIs"
CHAT_ID = "6471138889"


def send_telegram(message):
    """
    Отправляет сообщение в Telegram через Bot API
    
    Args:
        message (str): Текст сообщения для отправки (поддерживает Markdown)
    
    Returns:
        bool: True если сообщение отправлено успешно, False в противном случае
    """
    url = f"https://api.telegram.org/bot{BOT_TOKEN}/sendMessage"
    
    payload = {
        "chat_id": CHAT_ID,
        "text": message,
        "parse_mode": "Markdown"  # Поддержка Markdown форматирования
    }
    
    try:
        print(f"📤 Отправка сообщения в Telegram...")
        response = requests.post(url, json=payload, timeout=10)
        
        if response.status_code == 200:
            print(f"✅ Сообщение успешно отправлено!")
            return True
        else:
            print(f"❌ Ошибка при отправке: {response.status_code}")
            print(f"   Ответ сервера: {response.text}")
            return False
            
    except requests.exceptions.Timeout:
        print(f"❌ Ошибка: Превышено время ожидания ответа от сервера")
        return False
    except requests.exceptions.ConnectionError:
        print(f"❌ Ошибка: Не удалось подключиться к серверу Telegram")
        return False
    except Exception as e:
        print(f"❌ Неожиданная ошибка: {str(e)}")
        return False


if __name__ == "__main__":
    print("=" * 50)
    print("🤖 Telegram Bot Message Sender")
    print("=" * 50)
    
    # Тестовое сообщение
    test_message = "🚀 *[SYSTEM]* Связь установлена успешно!"
    
    # Отправка сообщения
    send_telegram(test_message)
    
    print("=" * 50)
