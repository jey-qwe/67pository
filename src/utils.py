"""
UTF-8 Sanitization Utilities
Ensures all text data is properly encoded for storage and transmission
Prevents gRPC client errors from invalid UTF-8 byte sequences
"""

import unicodedata
import sys
import io
from typing import Optional


# Fix Windows encoding (Handled via PYTHONIOENCODING now)
# sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8')


def sanitize_text(text: str, replacement: str = '') -> str:
    """
    Clean text by removing or replacing invalid UTF-8 characters
    
    Args:
        text: Input text that may contain invalid UTF-8
        replacement: String to replace invalid characters with (default: empty string)
        
    Returns:
        Sanitized text safe for UTF-8 encoding
    """
    if not isinstance(text, str):
        text = str(text)
    
    # Encode to UTF-8, replacing errors with the replacement string
    # Then decode back to ensure we have valid UTF-8
    try:
        # First pass: encode with 'ignore' to drop invalid bytes
        clean_bytes = text.encode('utf-8', errors='ignore')
        clean_text = clean_bytes.decode('utf-8', errors='ignore')
        
        # Second pass: normalize Unicode to NFC (canonical composition)
        # This ensures consistent representation of accented characters
        normalized = unicodedata.normalize('NFC', clean_text)
        
        return normalized
    except Exception as e:
        # If all else fails, convert to ASCII
        return text.encode('ascii', errors='ignore').decode('ascii')


def safe_encode(text: str, encoding: str = 'utf-8', errors: str = 'replace') -> bytes:
    """
    Safely encode text to bytes with error handling
    
    Args:
        text: Text to encode
        encoding: Target encoding (default: utf-8)
        errors: Error handling strategy ('replace', 'ignore', 'strict')
        
    Returns:
        Encoded bytes
    """
    if not isinstance(text, str):
        text = str(text)
    
    return text.encode(encoding, errors=errors)


def normalize_unicode(text: str, form: str = 'NFC') -> str:
    """
    Normalize Unicode text to a canonical form
    
    Args:
        text: Text to normalize
        form: Normalization form ('NFC', 'NFD', 'NFKC', 'NFKD')
        
    Returns:
        Normalized text
    """
    if not isinstance(text, str):
        text = str(text)
    
    return unicodedata.normalize(form, text)


def remove_control_characters(text: str, keep_newlines: bool = True) -> str:
    """
    Remove control characters that might cause encoding issues
    
    Args:
        text: Input text
        keep_newlines: Whether to preserve newline characters
        
    Returns:
        Text with control characters removed
    """
    if not isinstance(text, str):
        text = str(text)
    
    # Characters to keep
    keep_chars = ['\n', '\r', '\t'] if keep_newlines else []
    
    # Filter out control characters
    cleaned = ''.join(
        char for char in text
        if not unicodedata.category(char).startswith('C') or char in keep_chars
    )
    
    return cleaned


def ascii_safe(text: str, replace_emojis: bool = True) -> str:
    """
    Make text ASCII-safe by replacing or removing non-ASCII characters
    Useful for systems that don't handle Unicode well
    
    Args:
        text: Input text
        replace_emojis: If True, replace common emojis with text equivalents
        
    Returns:
        ASCII-safe text
    """
    if not isinstance(text, str):
        text = str(text)
    
    if replace_emojis:
        # Common emoji replacements
        emoji_map = {
            '🚀': '[ROCKET]',
            '🧠': '[BRAIN]',
            '✅': '[CHECKMARK]',
            '❌': '[X]',
            '🔥': '[FIRE]',
            '⚡': '[LIGHTNING]',
            '💡': '[BULB]',
            '📊': '[CHART]',
            '🤔': '[THINKING]',
            '🗑️': '[TRASH]',
            '📂': '[FOLDER]',
            '📖': '[BOOK]',
            '✂️': '[SCISSORS]',
            '💾': '[DISK]',
            '🔍': '[SEARCH]',
            '📍': '[PIN]',
            '🎯': '[TARGET]',
            '⏳': '[HOURGLASS]',
        }
        
        for emoji, replacement in emoji_map.items():
            text = text.replace(emoji, replacement)
    
    # Convert to ASCII, replacing non-ASCII chars
    ascii_text = text.encode('ascii', errors='ignore').decode('ascii')
    
    return ascii_text


def transliterate_unicode(text: str) -> str:
    """
    Transliterate problematic Unicode characters to ASCII equivalents
    Handles Greek letters, mathematical symbols, subscripts, etc.
    
    Args:
        text: Text with Unicode characters
        
    Returns:
        Text with Unicode replaced by ASCII equivalents
    """
    if not isinstance(text, str):
        text = str(text)
    
    # Greek letters (common in math formulas)
    greek_map = {
        'α': 'alpha', 'β': 'beta', 'γ': 'gamma', 'δ': 'delta',
        'ε': 'epsilon', 'ζ': 'zeta', 'η': 'eta', 'θ': 'theta',
        'ι': 'iota', 'κ': 'kappa', 'λ': 'lambda', 'μ': 'mu',
        'ν': 'nu', 'ξ': 'xi', 'ο': 'omicron', 'π': 'pi',
        'ρ': 'rho', 'σ': 'sigma', 'τ': 'tau', 'υ': 'upsilon',
        'φ': 'phi', 'χ': 'chi', 'ψ': 'psi', 'ω': 'omega',
        'Α': 'Alpha', 'Β': 'Beta', 'Γ': 'Gamma', 'Δ': 'Delta',
        'Ε': 'Epsilon', 'Ζ': 'Zeta', 'Η': 'Eta', 'Θ': 'Theta',
        'Ι': 'Iota', 'Κ': 'Kappa', 'Λ': 'Lambda', 'Μ': 'Mu',
        'Ν': 'Nu', 'Ξ': 'Xi', 'Ο': 'Omicron', 'Π': 'Pi',
        'Ρ': 'Rho', 'Σ': 'Sigma', 'Τ': 'Tau', 'Υ': 'Upsilon',
        'Φ': 'Phi', 'Χ': 'Chi', 'Ψ': 'Psi', 'Ω': 'Omega',
    }
    
    # Subscripts and superscripts
    subscript_map = {
        '₀': '0', '₁': '1', '₂': '2', '₃': '3', '₄': '4',
        '₅': '5', '₆': '6', '₇': '7', '₈': '8', '₉': '9',
        '⁰': '0', '¹': '1', '²': '2', '³': '3', '⁴': '4',
        '⁵': '5', '⁶': '6', '⁷': '7', '⁸': '8', '⁹': '9',
        'ₐ': 'a', 'ₑ': 'e', 'ₒ': 'o', 'ₓ': 'x', 'ₕ': 'h',
        'ₖ': 'k', 'ₗ': 'l', 'ₘ': 'm', 'ₙ': 'n', 'ₚ': 'p',
        'ₛ': 's', 'ₜ': 't', 'ₙ': 'n', 'ᵢ': 'i', 'ⱼ': 'j',
    }
    
    # Mathematical and other symbols
    symbol_map = {
        '·': '*', '×': 'x', '÷': '/', '±': '+/-', '∓': '-/+',
        '≤': '<=', '≥': '>=', '≠': '!=', '≈': '~=', '∞': 'inf',
        '∑': 'sum', '∏': 'prod', '√': 'sqrt', '∫': 'integral',
        '∂': 'd', '∇': 'nabla', '∈': 'in', '∉': 'not in',
        '⊂': 'subset', '⊃': 'superset', '∪': 'union', '∩': 'intersect',
        '→': '->', '←': '<-', '↔': '<->', '⇒': '=>', '⇐': '<=',
        '°': 'deg', '′': "'", '″': '"', '‴': "'''",
        '…': '...', '—': '-', '–': '-', ''': "'", ''': "'",
        '"': '"', '"': '"', '„': '"', '«': '<<', '»': '>>',
    }
    
    # Apply all replacements
    for char, replacement in greek_map.items():
        text = text.replace(char, replacement)
    
    for char, replacement in subscript_map.items():
        text = text.replace(char, replacement)
    
    for char, replacement in symbol_map.items():
        text = text.replace(char, replacement)
    
    return text


def sanitize_for_grpc(text: str) -> str:
    """
    Comprehensive sanitization for gRPC transmission
    Combines all sanitization methods to ensure gRPC compatibility
    
    Args:
        text: Text to sanitize
        
    Returns:
        Clean text safe for gRPC transmission
    """
    if not isinstance(text, str):
        text = str(text)
    
    # Step 1: Remove control characters (keep newlines)
    text = remove_control_characters(text, keep_newlines=True)
    
    # Step 2: Transliterate problematic Unicode (Greek letters, math symbols)
    # Optional: Keep this if you want to normalize math, but maybe not needed for Russian
    text = transliterate_unicode(text)
    
    # Step 3: Replace emojis with ASCII equivalents (Only emojis, not all unicode!)
    # We will modify ascii_safe to NOT be used here, or use it only for emojis if needed.
    # But for now, let's just attempt to normalize and keep UTF-8.
    # If we really hate emojis, we can replace them, but let's try to keep text.
    
    # text = ascii_safe(text, replace_emojis=True) # REMOVED: Deletes Russian
    
    # Alternative: Just replace emojis? 
    # For now, let's just rely on sanitize_text which uses 'ignore' in encode/decode cycle to drop BAD bytes,
    # but keeps valid UTF-8 (like Russian).
    
    # Step 4: Normalize Unicode to NFC
    text = normalize_unicode(text, 'NFC')
    
    # Step 5: Final sanitization pass (validates UTF-8)
    text = sanitize_text(text)
    
    return text


# ============================================================================
# TESTING
# ============================================================================

if __name__ == "__main__":
    print("=" * 70)
    print("UTF-8 SANITIZATION UTILITIES - Test Suite")
    print("=" * 70)
    print()
    
    # Test cases with problematic characters
    test_cases = [
        "Normal ASCII text",
        "Text with émojis: 🚀 🧠 ✅",
        "Unicode math: ω₁ · Ic + ω₂ · It",
        "Mixed: Hello 世界 Привет",
        "Control chars: Line1\x00\x01Line2",
    ]
    
    for i, test in enumerate(test_cases, 1):
        print(f"Test {i}: {test[:50]}...")
        print(f"  Sanitized: {sanitize_for_grpc(test)[:50]}...")
        print()
    
    print("=" * 70)
    print("All tests completed successfully!")
    print("=" * 70)
