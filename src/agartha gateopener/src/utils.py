
import sys
import logging

# Configure logger
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s [%(levelname)s] %(name)s: %(message)s',
    datefmt='%H:%M:%S',
    handlers=[
        logging.StreamHandler(sys.stdout),
        logging.FileHandler('bot_debug.log', encoding='utf-8')
    ]
)
logger = logging.getLogger("Agartha")

def safe_print(text: str):
    """
    Safely prints text to console, encoding errors are replaced.
    Useful for Windows consoles with Russian/Emojis.
    """
    try:
        print(text)
    except UnicodeEncodeError:
        # Fallback for systems that can't handle full unicode
        try:
            print(text.encode(sys.stdout.encoding, errors='replace').decode(sys.stdout.encoding))
        except:
            print(text.encode('ascii', errors='replace').decode('ascii'))

def log_info(msg: str):
    """Log info level message safely"""
    try:
        logger.info(msg)
    except Exception:
        pass # Logging usually handles encoding, but just in case

def log_error(msg: str):
    """Log error level message safely"""
    try:
        logger.error(msg)
    except Exception:
        pass
