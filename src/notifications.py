# -*- coding: utf-8 -*-
"""
Notifications Module
Модульная система для отправки уведомлений через Telegram Bot API
Может использоваться в любом проекте в этой папке

Автор: Senior Python Architect
Дата: 2026-01-24
"""

import requests
import sys
import io
import os

# Настройка кодировки для консоли Windows
if sys.platform == "win32":
    sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8')
    sys.stderr = io.TextIOWrapper(sys.stderr.buffer, encoding='utf-8')


# ============================================
# КОНФИГУРАЦИЯ - ВСТАВЬТЕ СВОИ ЗНАЧЕНИЯ ЗДЕСЬ
# ============================================

# Telegram Bot Token (получить у @BotFather)
BOT_TOKEN = os.getenv('TELEGRAM_BOT_TOKEN', 'YOUR_BOT_TOKEN_HERE')

# Telegram Chat ID (получить у @userinfobot)
CHAT_ID = os.getenv('TELEGRAM_CHAT_ID', 'YOUR_CHAT_ID_HERE')


# ============================================
# DISCORD CONFIGURATION
# ============================================

# Discord Bot Token
DISCORD_TOKEN = os.getenv('DISCORD_BOT_TOKEN', 'YOUR_DISCORD_TOKEN_HERE')

# Discord IDs
DISCORD_CLIENT_ID = os.getenv('DISCORD_CLIENT_ID', 'YOUR_CLIENT_ID_HERE')
DISCORD_PUBLIC_ID = os.getenv('DISCORD_PUBLIC_ID', 'YOUR_PUBLIC_ID_HERE')
DISCORD_CHANNEL_ID = os.getenv('DISCORD_CHANNEL_ID', 'YOUR_CHANNEL_ID_HERE')

# Jules Webhook URL
JULES_WEBHOOK_URL = os.getenv('JULES_WEBHOOK_URL', 'YOUR_JULES_WEBHOOK_URL_HERE')

# Light Scout Webhook URL (Jules-compatible signal channel)
LIGHT_SCOUT_WEBHOOK_URL = os.getenv('LIGHT_SCOUT_WEBHOOK_URL', 'YOUR_LIGHT_SCOUT_WEBHOOK_URL_HERE')

# Google Gemini API Key
GOOGLE_API_KEY = os.getenv('GOOGLE_API_KEY', 'YOUR_GOOGLE_API_KEY_HERE')


# ============================================
# ОСНОВНАЯ ФУНКЦИЯ ДЛЯ ОТПРАВКИ СООБЩЕНИЙ
# ============================================

def send_telegram(message):
    """
    Отправляет сообщение в Telegram через Bot API
    
    Args:
        message (str): Текст сообщения для отправки (поддерживает Markdown)
    
    Returns:
        bool: True если сообщение отправлено успешно, False в противном случае
    
    Примечание:
        Функция "тихая" - не ронит программу при ошибках сети,
        а просто выводит сообщение об ошибке в консоль
    """
    # Проверка на пустое сообщение
    if not message:
        print("⚠️ [Telegram] Попытка отправить пустое сообщение")
        return False
    
    # Проверка на placeholder-значения
    if BOT_TOKEN == "YOUR_BOT_TOKEN_HERE" or CHAT_ID == "YOUR_CHAT_ID_HERE":
        print("⚠️ [Telegram] Не настроены BOT_TOKEN или CHAT_ID в notifications.py")
        return False
    
    url = f"https://api.telegram.org/bot{BOT_TOKEN}/sendMessage"
    
    payload = {
        "chat_id": CHAT_ID,
        "text": message,
        "parse_mode": "Markdown"  # Поддержка Markdown форматирования
    }
    
    try:
        response = requests.post(url, json=payload, timeout=10)
        
        if response.status_code == 200:
            print(f"✅ [Telegram] Сообщение отправлено")
            return True
        else:
            print(f"❌ [Telegram] Ошибка API: {response.status_code}")
            return False
            
    except requests.exceptions.Timeout:
        print(f"⚠️ [Telegram] Превышено время ожидания ответа")
        return False
    except requests.exceptions.ConnectionError:
        print(f"⚠️ [Telegram] Нет подключения к интернету")
        return False
    except Exception as e:
        print(f"⚠️ [Telegram] Ошибка: {str(e)}")
        return False


# ============================================
# АЛИАС ДЛЯ СОВМЕСТИМОСТИ
# ============================================

def send_alert(message):
    """
    Алиас для send_telegram() для совместимости с разными проектами
    
    Args:
        message (str): Текст сообщения
    
    Returns:
        bool: True если успешно, False если ошибка
    """
    return send_telegram(message)


# ============================================
# ТЕСТИРОВАНИЕ МОДУЛЯ
# ============================================

if __name__ == "__main__":
    print("=" * 60)
    print("🧪 Тестирование Notifications Module")
    print("=" * 60)
    
    # Тестовое сообщение
    test_message = "🚀 *[TEST]* Связь с Telegram установлена!"
    
    # Отправка
    result = send_telegram(test_message)
    
    if result:
        print("\n✅ Модуль работает корректно!")
    else:
        print("\n❌ Проверьте настройки BOT_TOKEN и CHAT_ID")
    
    print("=" * 60)
