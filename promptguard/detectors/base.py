
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


def normalize_text(text: str) -> str:
    """Normalize text for detection without modifying the original prompt.

    Applies Unicode compatibility normalization, case folding, and removal
    of selected invisible formatting characters. Repeated-character
    reduction helps match simple obfuscations such as 'ignoooore'.
    """
    normalized = unicodedata.normalize("NFKC", text)
    normalized = _INVISIBLE_FORMAT_RE.sub("", normalized)
    normalized = normalized.casefold()
    normalized = _REPEATED_LETTERS_RE.sub(r"\1\1", normalized)
    return normalized
