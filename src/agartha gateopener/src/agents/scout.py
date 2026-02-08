
import logging
import os
import feedparser
import time
from typing import List, Dict, Optional
from playwright.sync_api import sync_playwright, Page
from fake_useragent import UserAgent
from src.utils import safe_print
import requests

# Configure logging (Safe for Windows)
logger = logging.getLogger("Scout")

class ScoutAgent:
    """
    Stealth Scout Agent.
    Supports:
    1. RSS Feeds (Reddit, etc.)
    2. DOM Scraping (Fiverr, Qwork, etc.)
    """
    
    # Configuration for DOM Scraping
    SELECTORS = {
        'fiverr': {
            'wait_for': '.gig-card-layout', 
            'card': '.gig-card-layout',
            'title': 'h3, .gig-title, [title]', # Multiple fallbacks
            'link': 'h3 a, .gig-title a, a[href^="/"]', 
            'price': '.price, .gig-price, .price-label',
            'description': '' # Fiverr cards often don't have descriptions, only titles
        },
        'qwork': {
            'wait_for': '.kwork-card',
            'card': '.kwork-card',
            'title': '.kwork-card-title',
            'link': '.kwork-card-title a',
            'price': '.kwork-card-price',
            'description': '.kwork-card-description'
        },
        'linkedin': {
            'wait_for': '.feed-shared-update-v2',
            'card': '.feed-shared-update-v2',
            # LinkedIn is tricky; text often contains the "title"
            'title': '.update-components-text span[dir="ltr"]', 
            'link': '.update-components-actor__meta a', # Profile link usually, specific post link is hard
            'price': '',
            'description': '.update-components-text'
        },
        'x': {
            'wait_for': 'article[data-testid="tweet"]',
            'card': 'article[data-testid="tweet"]',
            'title': 'div[data-testid="tweetText"]', # Tweet text is the title
            'link': 'a[href*="/status/"]',
            'price': '',
            'description': 'div[data-testid="tweetText"]'
        }
    }

    def __init__(self):
        self.ua = UserAgent()

    def fetch(self, url: str, platform: str = 'rss') -> List[Dict]:
        """
        Main entry point. Routes to specific fetcher based on platform.
        """
        logger.info(f"🕵️ Scout fetching: {url} ({platform})")
        
        if platform == 'rss' or url.endswith('.rss') or url.endswith('.xml'):
            return self._fetch_rss(url)
        elif platform in self.SELECTORS:
            return self._scrape_dom(url, platform)
        else:
            safe_print(f"⚠️ Unknown platform '{platform}', defaulting to RSS/Text")
            return self._fetch_rss(url)

    def _fetch_rss(self, url: str) -> List[Dict]:
        """
        Fetch RSS feed using requests (lighter and more reliable for XML than Playwright).
        """
        try:
            # Standard headers to mimic a browser and avoid 403 Forbidden
            # Use random UA to avoid fingerprinting
            headers = {
                'User-Agent': self.ua.random,
                'Accept': 'application/rss+xml, application/xml, text/xml, */*'
            }
            
            response = requests.get(url, headers=headers, timeout=10)
            
            if response.status_code != 200:
                logger.error(f"❌ RSS Fetch Error {response.status_code}: {url}")
                return []
                
            content = response.text
            feed = feedparser.parse(content)
            
            if not feed.entries:
                logger.warning(f"⚠️ No entries found in RSS: {url}")
                # Debug: Print first 500 chars if failed
                safe_print(f"Debug Content: {content[:500]}")
                return []
            
            jobs = []
            for entry in feed.entries:
                jobs.append({
                    'id': entry.get('id', entry.get('link', '')),
                    'title': entry.get('title', 'No Title'),
                    'link': entry.get('link', ''),
                    'description': entry.get('summary', entry.get('description', '')),
                    'price': 'N/A', # RSS rarely has structured price
                    'platform': 'rss',
                    'published': entry.get('published', '')
                })
            
            safe_print(f"✅ Fetched {len(jobs)} items from RSS: {url}")
            return jobs

        except Exception as e:
            logger.error(f"❌ RSS Error: {e}")
            return []

    def _scrape_dom(self, url: str, platform: str) -> List[Dict]:
        """
        New: DOM Scraping using Selectors
        """
        config = self.SELECTORS.get(platform)
        if not config:
            return []
            
        try:
            with sync_playwright() as p:
                browser = self._launch_browser(p)
                
                # Check for saved session
                session_file = f"sessions/{platform}.json"
                context_args = {'user_agent': self.ua.random}
                
                if os.path.exists(session_file):
                    safe_print(f"🔑 Loading authenticated session: {session_file}")
                    context_args['storage_state'] = session_file
                
                context = browser.new_context(**context_args)
                page = context.new_page()
                
                safe_print(f"🌍 Visiting {url}...")
                page.goto(url, wait_until='networkidle', timeout=60000)
                
                # Check for captchas or human verification?
                # Stealth mode is usually enough for view-only.
                
                if config.get('wait_for'):
                    try:
                        page.wait_for_selector(config['wait_for'], timeout=10000)
                    except:
                        safe_print("⚠️ Timeout waiting for selectors. Page might be blocked or changed.")
                        # Take screenshot for debug?
                        # page.screenshot(path="debug_scout.png")
                
                # Extract Cards
                # We do this logic inside the browser context (evaluate) for speed
                # Pass configuration to the browser
                jobs = page.evaluate("""
                    (config) => {
                        const results = [];
                        const cards = document.querySelectorAll(config.card);
                        
                        cards.forEach(card => {
                            const get = (sel) => {
                                if (!sel) return '';
                                const el = card.querySelector(sel);
                                return el ? el.innerText.trim() : '';
                            };
                            
                            const getLink = (sel) => {
                                if (!sel) return '';
                                const el = card.querySelector(sel);
                                return el ? el.href : '';
                            };

                            const title = get(config.title);
                            const link = getLink(config.link);
                            
                            if (title && link) {
                                results.push({
                                    id: link, // Use link as unique ID
                                    title: title,
                                    link: link,
                                    price: get(config.price) || 'N/A',
                                    description: get(config.description) || title, // Fallback to title
                                    platform: config.platform
                                });
                            }
                        });
                        return results;
                    }
                """, {**config, 'platform': platform})
                
                browser.close()
                
                safe_print(f"✅ Scraped {len(jobs)} items from {platform}")
                return jobs

        except Exception as e:
            logger.error(f"❌ DOM Scraping Error: {e}")
            return []

    def _launch_browser(self, p):
        """Helper to launch configured browser"""
        return p.chromium.launch(
            headless=True,
            args=['--disable-blink-features=AutomationControlled']
        )

    def _get_page_content(self, url: str, wait_for: Optional[str]) -> str:
        """Helper for raw content fetching"""
        try:
            with sync_playwright() as p:
                browser = self._launch_browser(p)
                page = browser.new_page(user_agent=self.ua.random)
                page.goto(url, wait_until='networkidle', timeout=60000)
                if wait_for:
                    page.wait_for_selector(wait_for, timeout=5000)
                content = page.content()
                browser.close()
                return content
        except Exception as e:
            logger.error(f"FETCH Error: {e}")
            return ""

if __name__ == "__main__":
    # Test
    scout = ScoutAgent()
    # Test Fiverr (Logic check only, url needs to be real search)
    # jobs = scout.fetch("https://www.fiverr.com/search/gigs?query=python", "fiverr")
    # print(f"Fiverr: {len(jobs)}")
