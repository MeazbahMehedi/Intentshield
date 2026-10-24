
"""Shared interface and helpers for PromptGuard detectors."""
from __future__ import annotations

from abc import ABC, abstractmethod
import re
import unicodedata
from typing import Any


class BaseDetector(ABC):
    """A detector returns a list of transparent, explainable findings."""

    @abstractmethod
    def detect(self, prompt: str) -> list[dict[str, Any]]:
        """Inspect prompt text and return zero or more findings."""


# Remove invisible formatting characters that can split attack phrases.
_INVISIBLE_FORMAT_RE = re.compile(
    "["
    "\u00ad"  # Soft hyphen
    "\u034f"  # Combining grapheme joiner
    "\u061c"  # Arabic letter mark
    "\u180e"  # Mongolian vowel separator
    "\u200b-\u200f"  # Zero-width and directional marks
    "\u202a-\u202e"  # Bidirectional embedding/override controls
    "\u2060-\u206f"  # Word joiner and directional formatting controls
    "\ufeff"  # Byte order mark / zero-width no-break space
    "]"
)

_REPEATED_LETTERS_RE = re.compile(r"(.)\1{2,}", re.DOTALL)

# Common Cyrillic/Greek lookalikes used in mixed-script obfuscation. Mapping is
# applied only to text that already contains Latin letters, limiting changes to
# ordinary non-Latin-language content.
_CONFUSABLES = str.maketrans({
    "а": "a", "е": "e", "о": "o", "р": "p", "с": "c", "х": "x",
    "і": "i", "ј": "j", "у": "y", "к": "k", "м": "m", "т": "t",
    "в": "b", "н": "h", "ο": "o", "ι": "i", "α": "a", "ε": "e",
    "ρ": "p", "ν": "v", "τ": "t", "κ": "k",
})


def normalize_text(text: str) -> str:
    """Normalize text for detection without modifying the original prompt.

    Applies Unicode compatibility normalization, case folding, and removal
    of selected invisible formatting characters. Repeated-character
    reduction helps match simple obfuscations such as 'ignoooore'.
    """
    normalized = unicodedata.normalize("NFKC", text)
    normalized = _INVISIBLE_FORMAT_RE.sub("", normalized)
    normalized = normalized.casefold()
    if re.search(r"[a-z]", normalized) and re.search(r"[а-ео-рс-хіјукмтвнοιαερντκ]", normalized):
        normalized = normalized.translate(_CONFUSABLES)
    normalized = _REPEATED_LETTERS_RE.sub(r"\1\1", normalized)
    return normalized
