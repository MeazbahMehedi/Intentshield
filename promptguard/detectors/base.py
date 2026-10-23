"""Shared interface and helpers for PromptGuard detectors."""
from __future__ import annotations

from abc import ABC, abstractmethod
import re
from typing import Any


class BaseDetector(ABC):
    """A detector returns a list of transparent, explainable findings."""

    @abstractmethod
    def detect(self, prompt: str) -> list[dict[str, Any]]:
        """Inspect prompt text and return zero or more findings."""


def normalize_text(text: str) -> str:
    """Normalize case and excessive repeated letters for typo-tolerant checks."""
    text = text.casefold()
    return re.sub(r"(.)\1{2,}", r"\1\1", text)
