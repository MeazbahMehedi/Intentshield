"""Configurable multi-signal rules loaded from data/rules.json."""
from __future__ import annotations

import json
from pathlib import Path
from typing import Any

from .base import BaseDetector, normalize_text


DEFAULT_RULES_PATH = Path(__file__).resolve().parents[1] / "data" / "rules.json"


class RuleDetector(BaseDetector):
    """Apply simple explainable rules that combine multiple textual signals."""

    def __init__(self, rules_path: str | Path | None = None):
        self.rules_path = Path(rules_path) if rules_path else DEFAULT_RULES_PATH
        try:
            data = json.loads(self.rules_path.read_text(encoding="utf-8"))
        except (OSError, json.JSONDecodeError):
            data = {"structured_rules": []}
        rules = data.get("structured_rules", [])
        self.rules = [rule for rule in rules if isinstance(rule, dict) and rule.get("name")]

    def detect(self, prompt: str) -> list[dict[str, Any]]:
        text = normalize_text(prompt)
        findings = []
        for rule in self.rules:
            all_terms = [str(term).casefold() for term in rule.get("all_terms", [])]
            any_terms = [str(term).casefold() for term in rule.get("any_terms", [])]
            if all_terms and not all(term in text for term in all_terms):
                continue
            if any_terms and not any(term in text for term in any_terms):
                continue
            if not all_terms and not any_terms:
                continue
            findings.append({
                "name": str(rule["name"]),
                "explanation": str(rule.get("explanation", "A configured combination of suspicious signals was detected.")),
                "weight": max(0, min(100, int(rule.get("weight", 20)))),
                "category": str(rule.get("category", "Configured rule")),
            })
        return findings
