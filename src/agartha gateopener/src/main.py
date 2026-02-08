
import discord
from discord.ext import tasks
import json
import os
import asyncio
from datetime import datetime
from typing import Set
import sys
import io

# Set console encoding to UTF-8 for Windows
if sys.platform == 'win32':
    sys.stdout.reconfigure(encoding='utf-8')
    sys.stderr.reconfigure(encoding='utf-8')

# Import Graph
from src.core.graph import app
from src.utils import safe_print

# Config (Moved from sniper2.py or recreated)
CONFIG = {
    'BOT_TOKEN': os.getenv('DISCORD_BOT_TOKEN', 'YOUR_TOKEN_HERE'),
    'CHANNEL_ID': int(os.getenv('DISCORD_CHANNEL_ID', '0')),
    'RSS_FEEDS': [
        {'url': 'https://www.reddit.com/r/pythonjobs/.rss', 'name': 'Reddit - Python', 'platform': 'rss'},
        {'url': 'https://www.reddit.com/r/forhire/.rss', 'name': 'Reddit - For Hire', 'platform': 'rss'},
        # DOM Scraping Feeds (Examples)
        {'url': 'https://www.fiverr.com/search/gigs?query=python%20bot&source=top-bar&search_in=everywhere&search-autocomplete-original-term=python%20bot', 'name': 'Fiverr - Python Bot', 'platform': 'fiverr'},
        {'url': 'https://kwork.com/projects?c=11&attr=2106', 'name': 'Kwork - Scripts', 'platform': 'qwork'},
        
        # Advanced Feeds (Require Sessions)
        # LinkedIn Search: "Python Job" sorted by Date
        {'url': 'https://www.linkedin.com/search/results/content/?keywords=python%20job&origin=SWITCH_SEARCH_VERTICAL&sortBy=%22date_posted%22', 'name': 'LinkedIn - Content', 'platform': 'linkedin'},
        # X Search: "hiring python" (Latest)
        {'url': 'https://x.com/search?q=hiring%20python&src=typed_query&f=live', 'name': 'X - Hiring Python', 'platform': 'x'},
    ],
    'CHECK_INTERVAL': 300, # 5 minutes
    'SEEN_IDS_FILE': 'seen_job_ids.json'
}

# Setup Discord
intents = discord.Intents.default()
bot = discord.Client(intents=intents)

seen_ids: Set[str] = set()

def load_seen_ids() -> Set[str]:
    try:
        if os.path.exists(CONFIG['SEEN_IDS_FILE']):
            with open(CONFIG['SEEN_IDS_FILE'], 'r', encoding='utf-8') as f:
                return set(json.load(f))
    except Exception as e:
        print(f"⚠️ Error loading seen IDs: {e}")
    return set()

def save_seen_ids():
    try:
        with open(CONFIG['SEEN_IDS_FILE'], 'w', encoding='utf-8') as f:
            json.dump(list(seen_ids), f)
    except Exception as e:
        print(f"⚠️ Error saving seen IDs: {e}")

@bot.event
async def on_ready():
    global seen_ids
    safe_print(f"🚀 Sniper AI Agent ready as {bot.user}")
    safe_print("✅ PATCH V2: NEW RSS LOGIC APPLIED")
    seen_ids = load_seen_ids()
    safe_print(f"📂 Loaded {len(seen_ids)} seen IDs")
    
    if not job_checker.is_running():
        job_checker.start()

@tasks.loop(seconds=CONFIG['CHECK_INTERVAL'])
async def job_checker():
    global seen_ids
    channel = bot.get_channel(CONFIG['CHANNEL_ID'])
    
    if not channel:
        safe_print(f"❌ Channel {CONFIG['CHANNEL_ID']} not found")
        return

    safe_print("🔄 Checking feeds...")
    
    for feed in CONFIG['RSS_FEEDS']:
        url = feed['url']
        safe_print(f"🔎 Scanning {feed['name']}...")
        
        # Invoke Graph
        # Note: Playwright and Graph are synchronous here.
        # Ideally, run in executor to avoid blocking Discord heartbeat.
        try:
             # Run sync graph in thread
            result = await asyncio.to_thread(
                app.invoke,
                {
                    "feed_url": url, 
                    "platform": feed.get('platform', 'rss'),
                    "seen_ids": list(seen_ids)
                }
            )
            
            fetched = result.get('fetched_jobs', [])
            approved = result.get('approved_jobs', [])
            
            # Update seen IDs with ALL fetched jobs to avoid re-processing
            for job in fetched:
                seen_ids.add(job['id'])
            
            # Send Discord Notifications for Approved jobs
            for job in approved:
                embed = discord.Embed(
                    title=f"🎯 {job['title']}",
                    url=job['link'],
                    description=job['reasoning'][:400] + "...",
                    color=0x00FF00
                )
                embed.add_field(name="Score", value=str(job.get('score', 'N/A')), inline=True)
                embed.set_footer(text=f"Analyzed by Gemma • {feed['name']}")
                
                await channel.send(embed=embed)
                safe_print(f"✅ Sent Discord alert for {job['title']}")
                
            save_seen_ids()
            
        except Exception as e:
            safe_print(f"❌ Error processing {feed['name']}: {e}")

    safe_print("💤 check complete.")

@job_checker.before_loop
async def before_job_checker():
    await bot.wait_until_ready()

if __name__ == "__main__":
    bot.run(CONFIG['BOT_TOKEN'])
