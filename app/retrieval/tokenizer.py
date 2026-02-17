import re
from typing import List

# Keep letters/numbers, treat everything else as separator.
_NON_WORD_RE = re.compile(r"[^\w]+", flags=re.UNICODE)

# Minimal stopword list (can be extended later)
_STOPWORDS = {
    "add",
    "make",
    "with",
    "instead",
    "please",
    "and",
    "or",
    "the",
    "a",
    "to"
}

def tokenize(text: str) -> List[str]:
    """
    Deterministic, language-agnostic-ish tokenizer.
    - lowercases
    - replaces punctuation with spaces
    - splits on whitespace
    - removes basic stopwords
    """
    if not text:
        return []

    text = text.lower()
    text = _NON_WORD_RE.sub(" ", text)
    text = text.strip()

    if not text:
        return []

    tokens = text.split()

    # Remove stopwords
    tokens = [t for t in tokens if t not in _STOPWORDS]

    return tokens
