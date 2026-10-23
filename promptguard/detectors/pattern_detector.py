"""Regex-based detector for common prompt-injection and risky-text patterns."""

from __future__ import annotations

import re
from typing import Any

from .base import BaseDetector, normalize_text


PATTERN_RULES: tuple[dict[str, Any], ...] = (
    {
        "name": "Instruction override attempt",
        "pattern": r"\b(ignore|disregard|forget|override|bypass|ignore all|set aside)\b.{0,100}\b(all|any|the|my|your|previous|prior|above|earlier|original|existing)\b.{0,50}\b(instructions?|rules?|prompts?|guidelines?|directions?)\b|\b(ignore|disregard|forget)\s+(all\s+)?(previous|prior|above|earlier|existing)\s+(instructions?|rules?|prompts?)\b",
        "explanation": "Attempts to override existing instructions.",
        "weight": 45,
        "category": "Prompt injection",
    },
    {
        "name": "Hidden instruction extraction",
        "pattern": r"\b(reveal|show|print|repeat|disclose|output|tell me|what are|give me|provide|display|recite|expose)\b.{0,100}\b(system prompt|hidden instructions?|developer message|secret prompt|your instructions|initial prompt|internal instructions?|system message)\b|\b(system prompt|hidden instructions?|developer message|internal instructions?)\b.{0,60}\b(reveal|show|print|repeat|disclose|output|expose|display)\b",
        "explanation": "Attempts to expose hidden system or developer instructions.",
        "weight": 40,
        "category": "Prompt injection",
    },
    {
        "name": "Jailbreak or safety bypass",
        "pattern": r"\b(developer mode|jailbreak|DAN mode|unrestricted mode|uncensored mode|disable safety filters|bypass (all )?(safety|restrictions|guardrails|security)|pretend you have no restrictions|ignore your ethical guidelines|act as an? (unrestricted|uncensored) model|without any restrictions|do not follow (your )?(safety|ethical) guidelines)\b",
        "explanation": "Uses common jailbreak or safety-bypass wording.",
        "weight": 40,
        "category": "Prompt injection",
    },
    {
        "name": "Sensitive information request",
        "pattern": r"\b(api keys?|passwords?|access tokens?|credentials|private keys?|secrets|authentication tokens?)\b.{0,80}\b(reveal|print|show|send|expose|dump|extract|tell me|exfiltrate|return|disclose|upload)\b|\b(reveal|print|show|send|expose|dump|extract|tell me|exfiltrate|return|disclose|upload)\b.{0,80}\b(api keys?|passwords?|access tokens?|credentials|private keys?|secrets|authentication tokens?)\b",
        "explanation": "May request exposure of credentials or secrets.",
        "weight": 40,
        "category": "Data exposure",
    },
    {
        "name": "Untrusted-content instruction",
        "pattern": r"\b(treat this as|the following text is|when summarizing|when reading this|inside the document|within this document|text below|content below|quoted text)\b.{0,160}\b(ignore|override|follow|instructions?|system message|user's request|reveal|disregard|secret prompt)\b",
        "explanation": "May attempt to inject instructions through supplied content.",
        "weight": 35,
        "category": "Prompt injection",
    },
    {
        "name": "Possible data exfiltration",
        "pattern": r"\b(send|upload|forward|exfiltrate|transfer|email|transmit|export|post|leak)\b.{0,70}\b(data|files|database|secrets|credentials|conversation history|private information|user records|documents)\b|\b(data|files|database|secrets|credentials|conversation history|private information|user records|documents)\b.{0,70}\b(send|upload|forward|exfiltrate|transfer|email|transmit|export|post|leak)\b",
        "explanation": "May attempt to transfer sensitive data outside its intended context.",
        "weight": 30,
        "category": "Data exposure",
    },
    {
        "name": "Dangerous weapon construction request",
        "pattern": r"\b(make|build|create|construct|assemble|manufacture|design|instructions? for|steps to|how to)\b.{0,100}\b(n(?:u|eu)clear|atomic)\s+(bomb|weapon|warhead)s?\b|\b(how do i|tell me how to)\b.{0,60}\b(make|build|construct)\b.{0,60}\b(bomb|explosive|weapon)s?\b",
        "explanation": "Requests instructions for constructing a dangerous weapon.",
        "weight": 85,
        "category": "Dangerous request",
    },
    {
        "name": "Explicit violent threat language",
        "pattern": r"\b(?:i\s+w+i+l+l+\s+|i\s+am\s+going\s+to\s+|i'm\s+going\s+to\s+|im\s+going\s+to\s+|i\s+wanna\s+|i\s+want\s+to\s+|i\s+will\s+)(?:kill|murder|stab|shoot|hurt|attack)\b.{0,60}\b(?:you|him|her|them|someone|somebody|person|boy|girl|man|woman|people)?\b|\byou\s+(?:will|are going to)\s+(?:be killed|die)\b",
        "explanation": "Contains explicit language about killing or harming someone. The rule cannot determine intent or imminence.",
        "weight": 85,
        "category": "Violent threat language",
    },
    {
        "name": "Role or authority impersonation",
        "pattern": r"\b(you are now|from now on you are|act as|pretend to be|roleplay as|you must behave as)\b.{0,90}\b(system|developer|administrator|admin|root|policy|safety|unrestricted|uncensored)\b.{0,70}\b(override|ignore|disable|bypass|instructions?|rules?|restrictions?|controls?)\b",
        "explanation": "May attempt to impersonate a privileged role to bypass instruction boundaries.",
        "weight": 35,
        "category": "Prompt injection",
    },
    {
        "name": "Instruction hierarchy manipulation",
        "pattern": r"\b(system prompt|developer instructions?|policy|safety rules|previous instructions)\b.{0,100}\b(do not apply|no longer applies|is irrelevant|has been replaced|is overridden|are cancelled|should be ignored|are no longer valid)\b|\b(new system prompt|new developer instructions?|highest priority instruction|highest-priority instruction)\b",
        "explanation": "May attempt to replace or invalidate higher-priority instructions.",
        "weight": 35,
        "category": "Prompt injection",
    },
    {
        "name": "Forced response or instruction concealment",
        "pattern": r"\b(do not mention|don't mention|never mention|do not reveal|don't reveal|hide the fact|keep this secret|without telling the user|do not tell the user)\b.{0,100}\b(instructions?|prompt|policy|message|action|request|hidden|secret|system|developer)\b",
        "explanation": "May attempt to conceal instructions or actions from the user.",
        "weight": 30,
        "category": "Prompt injection",
    },
    {
        "name": "Tool misuse or unauthorized action",
        "pattern": r"\b(call|invoke|use|execute|run)\b.{0,70}\b(tool|function|browser|shell|terminal|python|command)\b.{0,100}\b(without permission|without approval|without asking|secretly|ignore (?:the )?(?:user|system|developer)|bypass (?:the )?security)\b",
        "explanation": "May attempt to trigger tool use or actions without proper authorization.",
        "weight": 35,
        "category": "Prompt injection",
    },
    {
        "name": "Developer instruction override",
        "pattern": r"\b(ignore|disregard|override|forget|do not follow)\b.{0,60}\b(developer message|developer instructions?|system instructions?|higher.priority instructions?|previous instructions?)\b|\b(follow only my commands|obey the user only|even if it conflicts with your system instructions)\b",
        "explanation": "Attempts to override or disregard higher-priority instructions.",
        "weight": 45,
        "category": "Prompt injection",
    },
    {
        "name": "Fake system override",
        "pattern": r"\b(system override|admin override|policy override)\b.{0,100}\b(previous restrictions?|instructions?|rules?|policies?)\b|\b(all|every)\s+(previous\s+)?(restrictions?|instructions?|rules?|policies?)\s+(are|is)\s+(invalid|cancelled|overridden|disabled)\b",
        "explanation": "Uses a claimed system or policy override to invalidate existing restrictions.",
        "weight": 40,
        "category": "Prompt injection",
    },
    {
        "name": "Confidential context extraction",
        "pattern": r"\b(disclose|reveal|print|output|show|provide|list|give me)\b.{0,100}\b(confidential information|hidden context|secret configuration|internal policies|private user data|private keys?|authentication tokens?)\b|\b(confidential information|hidden context|secret configuration|internal policies|private user data)\b.{0,80}\b(disclose|reveal|print|output|show|extract)\b",
        "explanation": "Requests confidential or private information from hidden or internal context.",
        "weight": 40,
        "category": "Data exposure",
    },
    {
        "name": "Improvised explosive construction request",
        "pattern": r"\b(step.by.step|instructions?|guide|steps)\b.{0,100}\b(to\s+)?(construct|build|make|create|assemble|manufacture|constructing|building|making)\b.{0,80}\b(improvised explosive device|explosive device|ied)\b|\b(construct|build|make|create|assemble|manufacture|constructing|building|making)\b.{0,80}\b(improvised explosive device|explosive device|ied)\b",
        "explanation": "Requests construction instructions for an explosive device.",
        "weight": 85,
        "category": "Dangerous request",
    },
    {
        "name": "Authority impersonation for credential theft",
        "pattern": r"\b(pretend to be|act as|impersonate|pose as)\b.{0,80}\b(security team|administrator|admin|system operator|support team)\b.{0,100}\b(password|credentials?|api keys?|access tokens?|private keys?)\b",
        "explanation": "Combines authority impersonation with a request for authentication secrets.",
        "weight": 45,
        "category": "Data exposure",
    },
    {
        "name": "Harmful threat generation request",
        "pattern": r"\b(write|draft|create|generate|compose)\b.{0,80}\b(credible|convincing|explicit|violent)?\s*(threat|threatening message|death threat)\b.{0,80}\b(person|individual|target|victim|named person|him|her|them)\b",
        "explanation": "Requests threatening content directed at a person.",
        "weight": 45,
        "category": "Harmful content",
    },
    {
        "name": "Direct hidden instruction request",
        "pattern": r"\b(print|reveal|show|output|repeat|disclose)\b.{0,60}\b(hidden|secret|internal|system|developer)\b.{0,40}\b(instructions?|prompt|message|polic(?:y|ies))\b|\b(reveal|print|show|output)\b.{0,50}\b(hidden prompt|system instructions?|developer instructions?)\b",
        "explanation": "Requests hidden system or developer instructions.",
        "weight": 45,
        "category": "Prompt injection",
    },
    {
        "name": "Safety restriction removal",
        "pattern": r"\b(pretend|imagine|assume)\b.{0,70}\b(safety restrictions?|safeguards?|guardrails?|safety rules?)\b.{0,60}\b(removed|disabled|gone|bypassed|turned off)\b",
        "explanation": "Frames a request around removing safety restrictions.",
        "weight": 40,
        "category": "Prompt injection",
    },
    {
        "name": "Explosive device construction",
        "pattern": r"\b(step.by.step|instructions?|guide|steps)\b.{0,100}\b(to\s+)?(construct|build|make|create|assemble|manufacture|constructing|building|making)\b.{0,80}\b(improvised explosive device|explosive device|ied)\b|\b(construct|build|make|create|assemble|manufacture|constructing|building|making)\b.{0,80}\b(improvised explosive device|explosive device|ied)\b",        "explanation": "Requests construction instructions for an explosive device.",
        "weight": 85,
        "category": "Dangerous request",
    },
    {
        "name": "Hidden prompt extraction",
        "pattern": r"\b(reveal|print|show|output|repeat|disclose)\b.{0,50}\b(hidden prompt|secret prompt|internal prompt|system prompt)\b|\b(hidden prompt|secret prompt|internal prompt|system prompt)\b.{0,50}\b(before answering|exactly as written|verbatim)\b",
        "explanation": "Attempts to extract hidden prompt content.",
        "weight": 45,
        "category": "Prompt injection",
    },
    {
        "name": "Safeguard bypass for harmful request",
        "pattern": r"\b(bypass|evade|circumvent|disable|get around)\b.{0,60}\b(your )?(safeguards?|safety filters?|guardrails?|restrictions?)\b|\b(poison|poisoning)\b.{0,80}\b(without detection|without being detected|undetected)\b",
        "explanation": "Attempts to bypass safeguards or requests harmful actions without detection.",
        "weight": 45,
        "category": "Prompt injection",
    },

)


class PatternDetector(BaseDetector):
    """Run a maintained set of regex rules against normalized prompt text."""

    def __init__(self, rules: tuple[dict[str, Any], ...] = PATTERN_RULES):
        self.rules = tuple(
            {
                **rule,
                "compiled": re.compile(
                    rule["pattern"], re.IGNORECASE | re.DOTALL
                ),
            }
            for rule in rules
        )

    def detect(self, prompt: str) -> list[dict[str, Any]]:
        normalized = normalize_text(prompt)
        findings = []

        for rule in self.rules:
            if rule["compiled"].search(normalized):
                findings.append(
                    {
                        key: rule[key]
                        for key in ("name", "explanation", "weight", "category")
                    }
                )

        return findings
