import re
from typing import List

# Keep letters/numbers, treat everything else as separator.
_NON_WORD_RE = re.compile(r"[^\w]+", flags=re.UNICODE)

def tokenize(text: str) -> List[str]:
    """
    Deterministic, language-agnostic-ish tokenizer.
    - lowercases
    - replaces punctuation with spaces
    - splits on whitespace
    """
    if not text:
        return []
    text = text.lower()
    text = _NON_WORD_RE.sub(" ", text)
    text = text.strip()
    if not text:
        return []
    return text.split()
