# -*- coding: utf-8 -*-
"""
Light Scout - Multimodal News Agent
Uses Google Gemini 1.5 Flash for text + vision analysis
"""

import aiohttp
import asyncio
import json
import feedparser
import logging
from typing import List, Dict, Optional
from dataclasses import dataclass
from langchain_google_genai import ChatGoogleGenerativeAI
from langchain_core.messages import HumanMessage
import base64

# Setup logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    handlers=[
        logging.FileHandler('light_scout.log'),
        logging.StreamHandler()
    ]
)
logger = logging.getLogger('LightScout')


@dataclass
class NewsItem:
    """Data class for news items"""
    title: str
    link: str
    summary: str
    image_url: Optional[str] = None
    image_bytes: Optional[bytes] = None
    source: str = ""


class LightScout:
    """
    Multimodal News Agent using Google Gemini 1.5 Flash.
    Harvests feeds, analyzes content (text + images), dispatches to Discord.
    """
    
    def __init__(self, gemini_api_key: str, webhook_url: str):
        """
        Initialize Light Scout.
        
        Args:
            gemini_api_key: Google Gemini API key
            webhook_url: Discord webhook URL for notifications
        """
        self.gemini_api_key = gemini_api_key
        self.webhook_url = webhook_url
        
        # Initialize Gemini 2.0 Flash (2025 model)
        self.llm = ChatGoogleGenerativeAI(
            model="gemini-2.0-flash",
            google_api_key=gemini_api_key,
            temperature=0
        )
        
        print("[Light Scout] Initialized with Gemini 2.0 Flash")
    
    async def harvest(self, source: Dict) -> List[NewsItem]:
        """
        Harvest news items from a feed source.
        
        Args:
            source: Feed source dict with 'name', 'url', 'type'
            
        Returns:
            List of NewsItem objects
        """
        items = []
        
        try:
            # Reddit requires User-Agent header
            headers = {
                'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36'
            }
            
            async with aiohttp.ClientSession() as session:
                async with session.get(source['url'], headers=headers, timeout=aiohttp.ClientTimeout(total=10)) as response:
                    content = await response.text()
            
            if source['type'] == 'rss':
                items = await self._parse_rss(content, source['name'])
            elif source['type'] == 'json':
                items = await self._parse_json(content, source['name'])
            
            print(f"[Light Scout] Harvested {len(items)} items from {source['name']}")
            
        except Exception as e:
            print(f"[Light Scout] Error harvesting {source['name']}: {e}")
        
        return items
    
    async def _parse_rss(self, content: str, source_name: str) -> List[NewsItem]:
        """Parse RSS feed"""
        items = []
        feed = feedparser.parse(content)
        
        for entry in feed.entries[:10]:  # Limit to 10 items
            # Extract image URL from media content or enclosures
            image_url = None
            if hasattr(entry, 'media_content') and entry.media_content:
                image_url = entry.media_content[0].get('url')
            elif hasattr(entry, 'enclosures') and entry.enclosures:
                for enc in entry.enclosures:
                    if 'image' in enc.get('type', ''):
                        image_url = enc.get('href')
                        break
            
            item = NewsItem(
                title=entry.get('title', 'No Title'),
                link=entry.get('link', ''),
                summary=entry.get('summary', entry.get('description', 'No summary')),
                image_url=image_url,
                source=source_name
            )
            
            # Download image if URL found
            if image_url:
                item.image_bytes = await self._download_image(image_url)
            
            items.append(item)
        
        return items
    
    async def _parse_json(self, content: str, source_name: str) -> List[NewsItem]:
        """Parse JSON feed (Reddit format)"""
        items = []
        
        try:
            data = json.loads(content)
            posts = data.get('data', {}).get('children', [])
            
            for post_data in posts[:10]:  # Limit to 10 items
                post = post_data.get('data', {})
                
                # Extract image URL from preview
                image_url = None
                if 'preview' in post and 'images' in post['preview']:
                    images = post['preview']['images']
                    if images:
                        image_url = images[0].get('source', {}).get('url')
                        if image_url:
                            # Reddit URLs have &amp; which needs to be fixed
                            image_url = image_url.replace('&amp;', '&')
                
                # Also check thumbnail
                if not image_url and post.get('thumbnail', '').startswith('http'):
                    image_url = post['thumbnail']
                
                item = NewsItem(
                    title=post.get('title', 'No Title'),
                    link=f"https://reddit.com{post.get('permalink', '')}",
                    summary=post.get('selftext', '')[:500] or 'No summary',
                    image_url=image_url,
                    source=source_name
                )
                
                # Download image if URL found
                if image_url:
                    item.image_bytes = await self._download_image(image_url)
                
                items.append(item)
        
        except Exception as e:
            print(f"[Light Scout] Error parsing JSON: {e}")
        
        return items
    
    async def _download_image(self, url: str) -> Optional[bytes]:
        """Download image bytes"""
        try:
            async with aiohttp.ClientSession() as session:
                async with session.get(url, timeout=aiohttp.ClientTimeout(total=5)) as response:
                    if response.status == 200:
                        return await response.read()
        except Exception as e:
            print(f"[Light Scout] Failed to download image: {e}")
        return None
    
    async def analyze(self, text: str, image_bytes: Optional[bytes] = None) -> Dict:
        """
        Analyze content with Gemini 1.5 Flash (multimodal).
        
        Args:
            text: Text content to analyze
            image_bytes: Optional image bytes for vision analysis
            
        Returns:
            Analysis dict with score, summary, action
        """
        system_prompt = """You are an Elite AI Filter for a 15-year-old Engineer. Analyze this news item.

Look for: Open Source LLMs, Agent Frameworks, Hardware Optimizations, AI Automation.

VISION LOGIC: If an image is provided, analyze it carefully.
- Generic Stock Photo/Meme -> Ignore image, rely on text.
- Diagram/Code Screenshot/Benchmark Chart -> BOOST SCORE (+2).

Rate from 1-10. If Score > 7, return JSON with action='READ'.

Output STRICT JSON:
{
  "score": <int 1-10>,
  "summary": "<Punchy 1-sentence takeaway>",
  "action": "<READ or SKIP>"
}"""
        
        try:
            # Build message content
            if image_bytes:
                # Multimodal: text + image
                import base64
                image_b64 = base64.b64encode(image_bytes).decode('utf-8')
                
                message = HumanMessage(
                    content=[
                        {"type": "text", "text": f"{system_prompt}\n\nText: {text}"},
                        {
                            "type": "image_url",
                            "image_url": f"data:image/jpeg;base64,{image_b64}"
                        }
                    ]
                )
                logger.debug(f"Analyzing with image ({len(image_bytes)} bytes)")
            else:
                # Text only
                message = HumanMessage(content=f"{system_prompt}\n\nText: {text}")
                logger.debug("Analyzing text only")
            
            # Query Gemini
            logger.info("Sending to Gemini API...")
            response = self.llm.invoke([message])
            logger.info(f"Gemini response received: {len(response.content)} chars")
            
            # Parse JSON from response
            response_text = response.content.strip()
            
            # Extract JSON if wrapped in code blocks
            if '```json' in response_text:
                response_text = response_text.split('```json')[1].split('```')[0].strip()
            elif '```' in response_text:
                response_text = response_text.split('```')[1].split('```')[0].strip()
            
            result = json.loads(response_text)
            logger.info(f"Analysis result: score={result.get('score')}, action={result.get('action')}")
            return result
            
        except Exception as e:
            logger.error(f"Analysis error: {e}", exc_info=True)
            print(f"[Light Scout] Analysis error: {e}")
            return {"score": 0, "summary": "Analysis failed", "action": "SKIP"}
    
    async def dispatch(self, item: NewsItem, analysis: Dict):
        """
        Dispatch high-value items to Discord.
        
        Args:
            item: NewsItem to dispatch
            analysis: Analysis results
        """
        if analysis.get('action') != 'READ':
            logger.debug(f"Skipping item (action={analysis.get('action')})")
            return
        
        logger.info(f"Dispatching: {item.title[:50]}...")
        
        # Build Discord embed
        embed = {
            "title": item.title,
            "url": item.link,
            "description": analysis.get('summary', 'No summary'),
            "color": 0x00ff00,  # Green
            "fields": [
                {
                    "name": "Score",
                    "value": f"{analysis.get('score', 0)}/10",
                    "inline": True
                },
                {
                    "name": "Source",
                    "value": item.source,
                    "inline": True
                }
            ]
        }
        
        # Add image to embed if available
        if item.image_url:
            embed["image"] = {"url": item.image_url}
        
        payload = {
            "embeds": [embed]
        }
        
        try:
            async with aiohttp.ClientSession() as session:
                async with session.post(self.webhook_url, json=payload) as response:
                    if response.status == 204:
                        print(f"[Light Scout] Dispatched: {item.title[:50]}...")
                    else:
                        print(f"[Light Scout] Webhook error: {response.status}")
        except Exception as e:
            print(f"[Light Scout] Dispatch error: {e}")
    
    async def run(self, sources: List[Dict]):
        """
        Main run loop: harvest -> analyze -> dispatch
        Runs continuously with delays to respect API limits.
        
        Args:
            sources: List of feed sources
        """
        print("[Light Scout] Starting continuous monitoring...")
        
        while True:
            for source in sources:
                # Harvest
                items = await self.harvest(source)
                
                # Analyze and dispatch (limit to 5 fresh items per source to save quota)
                for item in items[:5]:
                    analysis = await self.analyze(
                        text=f"{item.title}\n\n{item.summary}",
                        image_bytes=item.image_bytes
                    )
                    
                    await self.dispatch(item, analysis)
                    
                    # Rate Limit Handling: Wait 30 seconds between items for Free Tier
                    logger.info("Waiting 30s to respect Gemini Free Tier rate limits...")
                    await asyncio.sleep(30)
            
            logger.info("Cycle complete. Sleeping for 5 minutes...")
            print("[Light Scout] Cycle complete. Sleeping for 5 minutes...")
            await asyncio.sleep(300)
        
        print("[Light Scout] Run complete")


# ============================================
# STANDALONE USAGE
# ============================================

async def main():
    """Test Light Scout"""
    import sys
    import os
    
    # Add parent directory to path for imports
    sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
    
    from src.notifications import GOOGLE_API_KEY, LIGHT_SCOUT_WEBHOOK_URL
    
    # Load sources
    with open('data/sources.json', 'r') as f:
        sources = json.load(f)
    
    # Initialize Light Scout
    scout = LightScout(
        gemini_api_key=GOOGLE_API_KEY,
        webhook_url=LIGHT_SCOUT_WEBHOOK_URL
    )
    
    # Run
    await scout.run(sources)


if __name__ == "__main__":
    asyncio.run(main())
