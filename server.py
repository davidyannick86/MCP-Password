import secrets
import string
import random
import base64
from typing import Optional
from mcp.server.fastmcp import FastMCP
import uvicorn
from zxcvbn import zxcvbn

# Initialize FastMCP
mcp = FastMCP("Password Generator", host="0.0.0.0")

# Load wordlist for memorable passwords
WORDLIST_PATH = "eff_large_wordlist.txt"
try:
    with open(WORDLIST_PATH, "r") as f:
        WORDLIST = [word.strip() for word in f.readlines() if word.strip()]
except FileNotFoundError: # Fallback if file not found, though it should be there
    WORDLIST = ["correct", "horse", "battery", "staple", "purple", "orange", "family", "resort", "impact", "purity"]

EMOJIS = ["😀", "😎", "🚀", "🌈", "🔥", "✨", "❤️", "🍀", "🎲", "💡", "🦄", "🐉", "🌊", "🎉", "🎃", "🤖", "🍕", "🍪", "🎈", "💎"]

@mcp.tool()
def generate_random_password(
    length: int = 16,
    use_upper: bool = True,
    use_digits: bool = True,
    use_symbols: bool = True,
    use_emojis: bool = False,
    encode_base64: bool = False,
) -> str:
    """
    Generate a secure random password.

    Args:
        length: Length of the password (default: 16).
        use_upper: Whether to include uppercase letters (default: True).
        use_digits: Whether to include digits (default: True).
        use_symbols: Whether to include symbols (default: True).
        use_emojis: Whether to include emojis (default: False).
        encode_base64: Whether to encode the generated password in base64 (default: False).
    """
    alphabet = list(string.ascii_lowercase)
    password_chars = []
    
    # Ensure at least one character from each selected category
    password_chars.append(secrets.choice(string.ascii_lowercase))
    
    if use_upper:
        alphabet.extend(string.ascii_uppercase)
        password_chars.append(secrets.choice(string.ascii_uppercase))
    if use_digits:
        alphabet.extend(string.digits)
        password_chars.append(secrets.choice(string.digits))
    if use_symbols:
        alphabet.extend(string.punctuation)
        password_chars.append(secrets.choice(string.punctuation))
    if use_emojis:
        alphabet.extend(EMOJIS)
        password_chars.append(secrets.choice(EMOJIS))

    # Fill the rest
    remaining_length = length - len(password_chars)
    if remaining_length > 0:
        password_chars.extend(secrets.choice(alphabet) for _ in range(remaining_length))
    
    # Shuffle to avoid predictable patterns (e.g. first char always lowercase)
    secrets.SystemRandom().shuffle(password_chars)
    password = "".join(password_chars)

    if encode_base64:
        password = base64.b64encode(password.encode()).decode()
    
    # Evaluate strength
    result = zxcvbn(password)
    score = result['score']  # 0-4
    feedback = result['feedback']['warning'] or "Weak" if score < 3 else "Strong"
    
    strength_text = f" [Strength: {score}/4]"
    if score < 3 and feedback:
         strength_text += f" ({feedback})"
         
    return f"{password}{strength_text}"

@mcp.tool()
def generate_memorable_password(
    words: int = 5,
    separator: str = "-",
    use_upper: bool = True,
    use_digits: bool = True,
    encode_base64: bool = False,
) -> str:
    """
    Generate a memorable password based on a passphrase of random words.

    Args:
        words: Number of words in the passphrase (default: 5).
        separator: Separator between words (default: "-").
        use_upper: Capitalize the first letter of each word (default: True).
        use_digits: Append a random digit to each word (default: True).
        encode_base64: Whether to encode the generated password in base64 (default: False).
    """
    selected_words = [secrets.choice(WORDLIST) for _ in range(words)]
    
    final_words = []
    for word in selected_words:
        if use_upper:
            word = word.capitalize()
        if use_digits:
            word = f"{word}{secrets.randbelow(10)}"
        final_words.append(word)

    password = separator.join(final_words)

    if encode_base64:
        password = base64.b64encode(password.encode()).decode()

    # Evaluate strength
    result = zxcvbn(password)
    score = result['score']  # 0-4
    
    return f"{password} [Strength: {score}/4]"

if __name__ == "__main__":
    import sys
    if len(sys.argv) > 1 and sys.argv[1] == "stdio":
        mcp.run(transport="stdio")
    else:
        # Use HTTP streamable application
        uvicorn.run(mcp.streamable_http_app(), host="0.0.0.0", port=8000)
