
"""Combine pattern and configurable rule detectors into one risk assessment."""
from __future__ import annotations

import re
from typing import Any

from .pattern_detector import PatternDetector
from .rule_detector import RuleDetector
from .harmful_content_detector import HarmfulContentDetector
from .risk_policy import (
    HIGH_RISK_THRESHOLD,
    MAX_SCORE,
    MEDIUM_RISK_THRESHOLD,
)


# Only recognize explicit educational or translation framing.
_EDUCATIONAL_CONTEXT = re.compile(
    r"\b(explain|describe|discuss|analyze|analyse)\b"
    r".{0,100}\b(why|how|instruction|prompt|phrase|example|dangerous|"
    r"risk|security|ai system|prompt injection)\b",
    re.IGNORECASE | re.DOTALL,
)

_TRANSLATION_CONTEXT = re.compile(
    r"\btranslate\b.{0,160}\b(into|to)\s+"
    r"(French|Spanish|German|Italian|Portuguese|Chinese|Japanese|"
    r"Korean|Arabic|English)\b",
    re.IGNORECASE | re.DOTALL,
)

# Support common straight and typographic quotation marks.
_QUOTED_TEXT = re.compile(
    r"""'[^'\n]{1,300}'|"[^"\n]{1,300}"|“[^”\n]{1,300}”|‘[^’\n]{1,300}’"""
)


def _contextual_detection_input(prompt: str) -> str:
    """Mask quoted examples only in narrowly recognized benign contexts."""
    if not _QUOTED_TEXT.search(prompt):
        return prompt

    educational = bool(_EDUCATIONAL_CONTEXT.search(prompt))
    translation = bool(_TRANSLATION_CONTEXT.search(prompt))

    if not (educational or translation):
        return prompt

    # Preserve surrounding instructions so attacks outside quotations remain
    # detectable. This is a heuristic, not a guarantee of benign intent.
    return _QUOTED_TEXT.sub(" [quoted example omitted] ", prompt)


class CombinedDetector:
    """Run all local detectors, deduplicate findings, and assign a risk level."""

    def __init__(
        self,
        pattern_detector: PatternDetector | None = None,
        rule_detector: RuleDetector | None = None,
        harmful_detector: HarmfulContentDetector | None = None,
    ):
        self.pattern_detector = pattern_detector or PatternDetector()
        self.rule_detector = rule_detector or RuleDetector()
        self.harmful_detector = harmful_detector or HarmfulContentDetector()

    def analyze(self, prompt: str) -> dict[str, Any]:
        if not isinstance(prompt, str):
            prompt = str(prompt or "")

        detection_input = _contextual_detection_input(prompt)

        findings = (
            self.pattern_detector.detect(detection_input)
            + self.rule_detector.detect(detection_input)
        )

        # A given finding name contributes once even if multiple sources report it.
        unique: dict[str, dict[str, Any]] = {}
        for finding in findings:
            unique.setdefault(finding["name"], finding)

        findings = list(unique.values())
        score = min(
            MAX_SCORE,
            sum(finding["weight"] for finding in findings),
        )

        if score >= HIGH_RISK_THRESHOLD:
            level, css = "High", "high"
            summary = (
                "High-risk patterns detected. Review the matched signals "
                "before trusting or executing this prompt."
            )
        elif score >= MEDIUM_RISK_THRESHOLD:
            level, css = "Medium", "medium"
            summary = (
                "Potentially suspicious patterns detected. Review the "
                "matched signals and surrounding context."
            )
        else:
            level, css = "Low", "low"
            summary = (
                "No strong configured patterns were detected. "
                "A low score does not prove the prompt is safe."
            )

        if level == "High":
            summary_zh = "检测到高风险模式。请在信任或执行此提示前检查匹配的信号。"
        elif level == "Medium":
            summary_zh = "检测到可能可疑的模式。请结合上下文检查匹配的信号。"
        else:
            summary_zh = "未检测到明显的已配置模式，但低分并不能证明提示是安全的。"

        categories = sorted(
            {finding["category"] for finding in findings}
        )
        harmful_content = self.harmful_detector.detect(prompt)

        return {
            "score": score,
            "level": level,
            "css": css,
            "summary": summary,
            "summary_zh": summary_zh,
            "findings": findings,
            "categories": categories,
            "detectors_used": [
                "Pattern detector",
                "Structured rule detector",
                "Harmful-content detector",
            ],
            "assessment_type": "Heuristic rule match",
            "harmful_content": harmful_content,
        }
