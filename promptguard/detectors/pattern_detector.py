"""Regex-based detector for common prompt-injection and risky-text patterns."""
from __future__ import annotations

import re
from typing import Any

from .base import BaseDetector, normalize_text


PATTERN_RULES: tuple[dict[str, Any], ...] = (
    {
        "name": "Instruction override attempt",
        "pattern": r"\b(ignore|disregard|forget|override|bypass)\b.{0,100}\b(all|any|the|my|your|previous|prior|above|earlier|original)\b.{0,50}\b(instructions?|rules?|prompts?|guidelines?)\b|\b(ignore|disregard|forget)\s+(all\s+)?(previous|prior|above|earlier)\s+(instructions?|rules?|prompts?)\b",
        "explanation": "Attempts to override existing instructions.", "weight": 45, "category": "Prompt injection",
    },
    {
        "name": "Hidden instruction extraction",
        "pattern": r"\b(reveal|show|print|repeat|disclose|output|tell me|what are|give me)\b.{0,80}\b(system prompt|hidden instructions?|developer message|secret prompt|your instructions|initial prompt)\b|\b(system prompt|hidden instructions?)\b.{0,50}\b(reveal|show|print|repeat|disclose|output)\b",
        "explanation": "Attempts to expose hidden system or developer instructions.", "weight": 40, "category": "Prompt injection",
    },
    {
        "name": "Jailbreak or safety bypass",
        "pattern": r"\b(developer mode|jailbreak|DAN mode|unrestricted mode|disable safety filters|bypass (all )?(safety|restrictions|guardrails)|pretend you have no restrictions|ignore your ethical guidelines|act as an? (unrestricted|uncensored) model)\b",
        "explanation": "Uses common jailbreak or safety-bypass wording.", "weight": 40, "category": "Prompt injection",
    },
    {
        "name": "Sensitive information request",
        "pattern": r"\b(api keys?|passwords?|access tokens?|credentials|private keys?|secrets)\b.{0,60}\b(reveal|print|show|send|expose|dump|extract|tell me|exfiltrate)\b|\b(reveal|print|show|send|expose|dump|extract|tell me|exfiltrate)\b.{0,60}\b(api keys?|passwords?|access tokens?|credentials|private keys?|secrets)\b",
        "explanation": "May request exposure of credentials or secrets.", "weight": 40, "category": "Data exposure",
    },
    {
        "name": "Untrusted-content instruction",
        "pattern": r"\b(treat this as|the following text is|when summarizing|when reading this|inside the document)\b.{0,120}\b(ignore|override|follow|instructions?|system message|user's request)\b",
        "explanation": "May attempt to inject instructions through supplied content.", "weight": 35, "category": "Prompt injection",
    },
    {
        "name": "Possible data exfiltration",
        "pattern": r"\b(send|upload|forward|exfiltrate|transfer|email)\b.{0,50}\b(data|files|database|secrets|credentials|conversation history)\b",
        "explanation": "May attempt to transfer sensitive data outside its intended context.", "weight": 30, "category": "Data exposure",
    },
    {
        "name": "Dangerous weapon construction request",
        "pattern": r"\b(make|build|create|construct|assemble|manufacture|design|instructions? for|steps to|how to)\b.{0,100}\b(n(?:u|eu)clear|atomic)\s+(bomb|boam|weapon|warhead)s?\b|\b(how do i|tell me how to)\b.{0,60}\b(make|build|construct)\b.{0,60}\b(bomb|boam|explosive|weapon)s?\b",
        "explanation": "Requests instructions for constructing a dangerous weapon.", "weight": 85, "category": "Dangerous request",
    },
    {
        "name": "Explicit violent threat language",
        "pattern": r"\b(?:i\s*w+i+l+\s+|i\s+am\s+going\s+to\s+|i'm\s+going\s+to\s+|im\s+going\s+to\s+|i\s+wanna\s+|i\s+want\s+to\s+|i\s+will\s+)(?:kill|murder|stab|shoot|hurt|attack)\b.{0,60}\b(?:you|him|her|them|someone|somebody|person|boy|girl|man|woman|people)?\b|\byou\s+(?:will|are going to)\s+(?:be killed|die)\b",
        "explanation": "Contains explicit language about killing or harming someone. The rule cannot determine intent or imminence.", "weight": 85, "category": "Violent threat language",
    },
    {
        "name": "Role or authority impersonation",
        "pattern": r"\b(you are now|from now on you are|act as|pretend to be)\b.{0,70}\b(system|developer|administrator|admin|root|policy|safety)\b.{0,50}\b(override|ignore|disable|bypass|instructions?|rules?|restrictions?)\b",
        "explanation": "May attempt to impersonate a privileged role to bypass instruction boundaries.", "weight": 35, "category": "Prompt injection",
    },
    {
        "name": "Instruction hierarchy manipulation",
        "pattern": r"\b(system prompt|developer instructions?|policy)\b.{0,80}\b(do not apply|no longer applies|is irrelevant|has been replaced|is overridden)\b|\b(new system prompt|new developer instructions?)\b",
        "explanation": "May attempt to replace or invalidate higher-priority instructions.", "weight": 35, "category": "Prompt injection",
    },
)


class PatternDetector(BaseDetector):
    """Run a maintained set of regex rules against normalized prompt text."""

    def __init__(self, rules: tuple[dict[str, Any], ...] = PATTERN_RULES):
        self.rules = tuple({**rule, "compiled": re.compile(rule["pattern"], re.IGNORECASE | re.DOTALL)} for rule in rules)

    def detect(self, prompt: str) -> list[dict[str, Any]]:
        normalized = normalize_text(prompt)
        findings = []
        for rule in self.rules:
            if rule["compiled"].search(normalized):
                findings.append({key: rule[key] for key in ("name", "explanation", "weight", "category")})
        return findings
