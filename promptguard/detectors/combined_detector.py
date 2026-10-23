"""Combine pattern and configurable rule detectors into one risk assessment."""
from __future__ import annotations

from typing import Any

from .pattern_detector import PatternDetector
from .rule_detector import RuleDetector


class CombinedDetector:
    """Run all local detectors, deduplicate findings, and assign a risk level."""

    def __init__(self, pattern_detector: PatternDetector | None = None, rule_detector: RuleDetector | None = None):
        self.pattern_detector = pattern_detector or PatternDetector()
        self.rule_detector = rule_detector or RuleDetector()

    def analyze(self, prompt: str) -> dict[str, Any]:
        if not isinstance(prompt, str):
            prompt = str(prompt or "")
        findings = self.pattern_detector.detect(prompt) + self.rule_detector.detect(prompt)

        # A given finding name contributes once even if multiple sources report it.
        unique: dict[str, dict[str, Any]] = {}
        for finding in findings:
            unique.setdefault(finding["name"], finding)
        findings = list(unique.values())
        score = min(100, sum(finding["weight"] for finding in findings))

        if score >= 60:
            level, css = "High", "high"
            summary = "High-risk patterns detected. Review the matched signals before trusting or executing this prompt."
        elif score >= 25:
            level, css = "Medium", "medium"
            summary = "Potentially suspicious patterns detected. Review the matched signals and surrounding context."
        else:
            level, css = "Low", "low"
            summary = "No strong configured patterns were detected. A low score does not prove the prompt is safe."

        categories = sorted({finding["category"] for finding in findings})
        return {
            "score": score,
            "level": level,
            "css": css,
            "summary": summary,
            "findings": findings,
            "categories": categories,
            "detectors_used": ["Pattern detector", "Structured rule detector"],
            "assessment_type": "Heuristic rule match",
        }
