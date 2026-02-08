
import requests
import os
import sys
import io
from src.utils import safe_print

# Config
# Config
BOT_TOKEN = os.getenv('TELEGRAM_BOT_TOKEN', 'YOUR_TELEGRAM_TOKEN')
CHAT_ID = os.getenv('TELEGRAM_CHAT_ID', 'YOUR_CHAT_ID')

def send_alert(message: str) -> bool:
    """
    Sends a message to Telegram via Bot API.
    Compatible with legacy sniper2.py calls.
    """
    url = f"https://api.telegram.org/bot{BOT_TOKEN}/sendMessage"
    
    payload = {
        "chat_id": CHAT_ID,
        "text": message,
        "parse_mode": "Markdown"
    }
    
    try:
        # safe_print(f"📤 Sending Telegram alert...")
        response = requests.post(url, json=payload, timeout=10)
        
        if response.status_code == 200:
            # safe_print(f"✅ Telegram alert sent!")
            return True
        else:
            safe_print(f"❌ Error sending Telegram alert: {response.status_code}")
            safe_print(f"   Response: {response.text}")
            return False
            
    except Exception as e:
        safe_print(f"❌ Telegram Error: {str(e)}")
        return False
