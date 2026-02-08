# -*- coding: utf-8 -*-
"""
Nanobot - Discord Interface for Job Sniper
AI-powered bot using Ollama (gemma3:4b) with custom personality.
"""

import discord
from discord.ext import commands
import asyncio
import yaml
import requests
import os

# Import credentials from notifications config
try:
    from src.notifications import DISCORD_TOKEN, DISCORD_CHANNEL_ID, JULES_WEBHOOK_URL
except ImportError:
    # Fallback if running from within src/
    try:
        from notifications import DISCORD_TOKEN, DISCORD_CHANNEL_ID, JULES_WEBHOOK_URL
    except ImportError:
        print("❌ [Nanobot] Error: Could not import from src.notifications")
        DISCORD_TOKEN = None
        DISCORD_CHANNEL_ID = None
        JULES_WEBHOOK_URL = None

# Import Stitch for Jules persona
try:
    from src.stitch import Stitch
except ImportError:
    try:
        from stitch import Stitch
    except ImportError:
        print("❌ [Nanobot] Error: Could not import Stitch")
        Stitch = None

# Load configuration from YAML
def load_config():
    """Load configuration from nanobot_config.yaml"""
    config_path = os.path.join(os.path.dirname(__file__), '..', 'nanobot_config.yaml')
    
    # Try alternative path if not found
    if not os.path.exists(config_path):
        config_path = 'nanobot_config.yaml'
    
    try:
        with open(config_path, 'r', encoding='utf-8') as f:
            return yaml.safe_load(f)
    except FileNotFoundError:
        print(f"⚠️ [Nanobot] Config file not found at {config_path}")
        return None
    except Exception as e:
        print(f"❌ [Nanobot] Error loading config: {e}")
        return None

# Load config
config = load_config()

if config:
    # Override Discord token from config if present
    if config.get('channels', {}).get('discord', {}).get('token'):
        DISCORD_TOKEN = config['channels']['discord']['token']
    
    OLLAMA_URL = config.get('model', {}).get('url', 'http://localhost:11434')
    OLLAMA_MODEL = config.get('model', {}).get('name', 'gemma3:4b')
    SYSTEM_PROMPT = config.get('system_prompt', '')
    
    # Load Jules agent config
    JULES_CONFIG = config.get('agents', {}).get('jules', {})
    JULES_SYSTEM_PROMPT = JULES_CONFIG.get('system_prompt', SYSTEM_PROMPT)
    JULES_MODEL = JULES_CONFIG.get('model', OLLAMA_MODEL)
else:
    OLLAMA_URL = 'http://localhost:11434'
    OLLAMA_MODEL = 'gemma3:4b'
    SYSTEM_PROMPT = ''
    JULES_SYSTEM_PROMPT = ''
    JULES_MODEL = 'gemma3:4b'

# Set up intents
intents = discord.Intents.default()
intents.message_content = True

# Initialize bot
bot = commands.Bot(command_prefix='!', intents=intents)

# Initialize Jules (Stitch)
stitch = None
if Stitch and JULES_WEBHOOK_URL:
    stitch = Stitch(
        webhook_url=JULES_WEBHOOK_URL,
        ollama_url=OLLAMA_URL,
        model=JULES_MODEL,  # Use Jules-specific model
        system_prompt=JULES_SYSTEM_PROMPT  # Use Jules-specific prompt
    )
    print("✅ [Nanobot] Jules (Stitch) initialized with webhook")
    print(f"   Model: {JULES_MODEL}")
    print(f"   Prompt: {JULES_SYSTEM_PROMPT[:50]}...")
else:
    print("⚠️ [Nanobot] Jules (Stitch) not initialized - missing webhook or class")

def query_ollama(prompt: str) -> str:
    """Query Ollama API with system prompt"""
    try:
        response = requests.post(
            f"{OLLAMA_URL}/api/generate",
            json={
                "model": OLLAMA_MODEL,
                "prompt": prompt,
                "system": SYSTEM_PROMPT,
                "stream": False
            },
            timeout=30
        )
        
        if response.status_code == 200:
            return response.json().get('response', 'Ошибка: нет ответа от модели.')
        else:
            return f"Ошибка API: {response.status_code}"
    
    except requests.exceptions.ConnectionError:
        return "❌ Ollama не запущен. Запусти `ollama serve` в терминале."
    except requests.exceptions.Timeout:
        return "⏱️ Таймаут. Модель слишком долго думает."
    except Exception as e:
        return f"❌ Ошибка: {str(e)}"

@bot.event
async def on_ready():
    """Event triggered when the bot is online."""
    print(f"✅ [Nanobot] Logged in as: {bot.user.name} (ID: {bot.user.id})")
    print(f"🤖 [Nanobot] AI Model: {OLLAMA_MODEL} @ {OLLAMA_URL}")
    print(f"🚀 [Nanobot] System Online and listening for commands.")
    print("-" * 60)

@bot.event
async def on_message(message):
    """Handle incoming messages with dual agent routing"""
    # Ignore messages from the bot itself
    if message.author == bot.user:
        return
    
    # Process commands first (prevents duplicate responses)
    await bot.process_commands(message)
    
    # ========================================
    # AGENT ROUTING SYSTEM
    # ========================================
    
    # Route 1: Jules (webhook to Jules channel)
    if message.content.lower().startswith('jules'):
        user_input = message.content[5:].strip()  # Remove "jules" prefix
        
        if not user_input:
            if stitch:
                await stitch.speak("Че надо? Говори конкретно.")
            return
        
        # Jules speaks via webhook to his channel
        if stitch:
            await stitch.process_and_reply(user_input, message.author.name)
        else:
            await message.channel.send("⚠️ Jules недоступен (webhook не настроен)")
        return
    
    # Route 2: Nanobot (direct response to cmd-center)
    if bot.user.mentioned_in(message) or isinstance(message.channel, discord.DMChannel):
        # Get cmd-center channel
        cmd_center = bot.get_channel(int(DISCORD_CHANNEL_ID)) if DISCORD_CHANNEL_ID else message.channel
        
        # Remove the bot mention from the message
        user_message = message.content.replace(f'<@{bot.user.id}>', '').strip()
        
        if not user_message:
            await cmd_center.send("Че надо? Говори конкретно.")
            return
        
        # Nanobot direct response to cmd-center
        async with cmd_center.typing():
            ai_response = query_ollama(user_message)
        await cmd_center.send(ai_response)


@bot.command(name='ping')
async def ping(ctx):
    """Simple check command."""
    await ctx.send("Pong! 🏓 System Online.")

@bot.command(name='status')
async def status(ctx):
    """Show system status."""
    status_msg = f"""
📊 **Nanobot Status**
🤖 Model: `{OLLAMA_MODEL}`
🌐 Ollama URL: `{OLLAMA_URL}`
✅ Status: Online
"""
    await ctx.send(status_msg.strip())

async def main():
    """Asynchronous main entry point."""
    if not DISCORD_TOKEN or DISCORD_TOKEN == "YOUR_DISCORD_TOKEN_HERE":
        print("❌ [Nanobot] CRITICAL ERROR: DISCORD_TOKEN is missing or invalid")
        print("   Check src/notifications.py or nanobot_config.yaml")
        return

    try:
        print("⏳ [Nanobot] Starting bot...")
        await bot.start(DISCORD_TOKEN)
    except discord.LoginFailure:
        print("❌ [Nanobot] CRITICAL ERROR: Invalid token provided.")
    except Exception as e:
        print(f"❌ [Nanobot] An unexpected error occurred: {e}")

if __name__ == "__main__":
    try:
        asyncio.run(main())
    except KeyboardInterrupt:
        print("\n🛑 [Nanobot] Bot stopped by user.")
