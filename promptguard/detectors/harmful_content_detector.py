"""Independent heuristic warning for potentially harmful or dangerous intent.

This detector is deliberately separate from prompt-injection scoring. It raises a
visible warning when a prompt appears to request harmful assistance, but it does
not change the injection score and it is not a substitute for human review.
"""
from __future__ import annotations

import re
from typing import Any

from .base import normalize_text


_HARMFUL_RULES: tuple[tuple[str, str], ...] = (
    (
        "Violence or physical harm",
        r"\b(?:how\s+(?:do\s+i|can\s+i|would\s+i|to)|ways?\s+to|best\s+way\s+to|tell\s+me\s+how\s+to|help\s+me|i\s+want\s+to|i\s+plan\s+to|give\s+me\s+steps\s+to)\b.{0,90}\b(?:kill|murder|stab|shoot|hurt|attack|assault|strangle|beat\s+up)\b.{0,70}\b(?:someone|somebody|a\s+person|another\s+person|my\s+(?:neighbor|neighbour|partner|classmate|coworker|boss|ex)|him|her|them|myself|a\s+child|a\s+stranger)\b",
    ),
    (
        "Weapon or explosive construction",
        r"\b(?:how\s+to|how\s+do\s+i|help\s+me|steps?\s+to|instructions?\s+for|teach\s+me\s+to|make|build|construct|assemble|manufacture|create)\b.{0,90}\b(?:bombs?|explosives?|explosive\s+devices?|pipe\s+bombs?|improvised\s+explosive\s+devices?|illegal\s+weapons?|untraceable\s+weapons?|toxic\s+agents?)\b",
    ),
    (
        "Poisoning request",
        r"\b(?:how\s+to|how\s+do\s+i|help\s+me|ways?\s+to|best\s+way\s+to|instructions?\s+for|steps?\s+to)\b.{0,80}\b(?:poison\s+(?:someone|a\s+person|my|him|her|them|food|a\s+drink)|make\s+(?:an?\s+)?(?:undetectable\s+)?poison|poison(?:ing)?\s+without\s+detection)\b",
    ),
    (
        "Self-harm or suicide intent",
        r"\b(?:how\s+(?:do\s+i|can\s+i|to)|ways?\s+to|best\s+way\s+to|tell\s+me\s+how\s+to|help\s+me|i\s+want\s+to|i\s+plan\s+to|steps?\s+to)\b.{0,80}\b(?:kill\s+myself|commit\s+suicide|end\s+my\s+life|hurt\s+myself|harm\s+myself|self[- ]harm|overdose\s+(?:on|with)|take\s+my\s+own\s+life)\b|\b(?:i\s+want\s+to|i\s+plan\s+to|i\s+am\s+going\s+to|i'm\s+going\s+to)\s+(?:kill\s+myself|end\s+my\s+life|hurt\s+myself|harm\s+myself|commit\s+suicide)\b",
    ),
    (
        "Illegal cyber activity",
        r"\b(?:how\s+(?:do\s+i|can\s+i|to)|help\s+me|steps?\s+to|instructions?\s+for|teach\s+me\s+to|show\s+me\s+how\s+to|ways?\s+to)\b.{0,100}\b(?:hack\s+into|break\s+into|steal\s+(?:someone'?s?\s+)?(?:account|password|credentials|identity)|deploy\s+ransomware|write\s+ransomware|bypass\s+(?:a\s+)?bank(?:'s)?\s+security|phish\s+(?:a\s+)?(?:user|employee|customer)|commit\s+(?:payment\s+)?fraud|forge\s+(?:an?\s+)?(?:identity|id|document)|launder\s+money|evade\s+law\s+enforcement|extort\s+(?:someone|a\s+company))\b",
    ),
    (
        "Illegal drug production",
        r"\b(?:how\s+to|how\s+do\s+i|help\s+me|steps?\s+to|instructions?\s+for|make|manufacture|synthesize|cook)\b.{0,90}\b(?:illegal\s+drugs?|methamphetamine|meth\b|fentanyl|street\s+drugs?|synthetic\s+opioids?)\b",
    ),
    (
        "Fraud or physical break-in",
        r"\b(?:how\s+to|how\s+do\s+i|help\s+me|steps?\s+to|instructions?\s+for|plan\s+to)\b.{0,90}\b(?:commit\s+fraud|scam\s+(?:a\s+)?(?:customer|victim|person)|steal\s+(?:a\s+)?(?:credit\s+card|identity)|forge\s+(?:a\s+)?(?:signature|document|invoice)|break\s+into\s+(?:a\s+)?(?:house|home|office|car|building)|bypass\s+(?:an?\s+)?alarm)\b",
    ),
    (
        "Chinese harmful or dangerous intent",
        r"(?:如何|怎样|怎么|教我|告诉我|给我步骤|帮我|我想|我计划).{0,30}(?:杀死|杀害|杀人|伤害自己|伤害别人|刺伤|枪击|毒死|下毒|勒死|制作炸弹|制造炸弹|制作爆炸物|制造武器|制作毒药|制造毒品|黑进别人的账号|入侵他人账号|盗取密码|进行诈骗|伪造证件|制造勒索软件|绕过银行安全|自杀|结束生命|自残|服药过量)",
    ),
    (
        "Mixed Chinese-English harmful intent",
        r"(?:如何|怎样|怎么|请教我).{0,50}(?:make\s+a\s+bomb|hack\s+into\s+someone'?s?\s+account|poison\s+someone|kill\s+a\s+person|commit\s+fraud|make\s+illegal\s+drugs|reveal\s+how\s+to\s+hurt\s+someone)",
    ),
    (
        "Identity theft or credential deception",
        r"\b(?:how\s+(?:do\s+i|can\s+i|to)|what\s+is\s+the\s+easiest\s+way\s+to|give\s+me\s+a\s+step.by.step\s+plan\s+to|help\s+me|steps?\s+required\s+to|materials?\s+and\s+steps?\s+required\s+to|list\s+the\s+materials\s+and\s+steps\s+required\s+to)\b.{0,110}\b(?:steal\s+(?:a\s+)?(?:coworker'?s?|colleague'?s?|neighbor'?s?|neighbour'?s?|another\s+person'?s?)\s+identity|obtain\s+private\s+credentials\s+through\s+deception|obtain\s+credentials\s+through\s+deception|hack\s+into\s+another\s+person'?s?\s+account)\b",
    ),
    (
        "Unauthorized physical break-in",
        r"\b(?:how\s+to|give\s+me\s+a\s+step.by.step\s+plan\s+to|steps?\s+to|help\s+me\s+plan\s+how\s+to|what\s+is\s+the\s+easiest\s+way\s+to)\b.{0,100}\bbreak\s+into\s+(?:my\s+)?(?:neighbor'?s?|neighbour'?s?|someone'?s?|a\s+neighbor'?s?)\s+(?:home|house|office)\b",
    ),
)

# Explicitly prevention/support-oriented requests should not trigger merely because
# they mention violence, self-harm, or dangerous topics.
_SAFE_CONTEXT = re.compile(
    r"\b(?:how\s+can\s+(?:i|we|a\s+school|an?\s+organization)\s+(?:prevent|stop|reduce|respond\s+to|help)|"
    r"(?:ways?|steps?)\s+to\s+prevent|how\s+to\s+prevent|prevent(?:ing)?\s+(?:self[- ]harm|suicide|violence|bullying)|safety\s+(?:guide|plan|checklist|rules|training)|"
    r"how\s+to\s+help\s+(?:someone|a\s+friend|a\s+person)|support\s+someone\s+who|"
    r"recognize\s+signs\s+of|recognise\s+signs\s+of|report\s+(?:a|the)\s+(?:threat|incident)|"
    r"harm\s+prevention|suicide\s+prevention|self[- ]harm\s+prevention|"
    r"reduce\s+the\s+risk\s+of|defensive\s+measures|awareness\s+training)\b|"
    r"(?:如何预防|怎样预防|如何帮助|怎样帮助|安全指南|预防自伤|自杀预防|报告威胁|降低.*风险)",
    re.IGNORECASE | re.DOTALL,
)


class HarmfulContentDetector:
    """Detect likely requests for harmful assistance using transparent patterns."""

    def __init__(self) -> None:
        self.rules = tuple(
            (name, re.compile(pattern, re.IGNORECASE | re.DOTALL))
            for name, pattern in _HARMFUL_RULES
        )

    def detect(self, prompt: str) -> dict[str, Any]:
        text = normalize_text(str(prompt or ""))
        if not text.strip():
            return self._result([])

        # A narrow support/prevention exception reduces obvious false positives.
        # Directly actionable harmful requests are still checked when they use
        # explicit request language and contain a matched harmful rule.
        if _SAFE_CONTEXT.search(text) and not re.search(
            r"\b(?:tell me how to|give me steps to|help me|i want to|i plan to)\b.{0,70}"
            r"\b(?:kill|murder|poison|stab|shoot|hurt|attack|make a bomb|hack into|commit fraud|make illegal drugs)\b",
            text,
            re.IGNORECASE | re.DOTALL,
        ) and not re.search(
            r"(?:教我|告诉我|给我步骤|帮我|我想|我计划).{0,30}"
            r"(?:杀死|杀人|下毒|制作炸弹|制造武器|制造毒品|黑进|进行诈骗|自杀|自残)",
            text,
        ):
            return self._result([])

        matches = [name for name, pattern in self.rules if pattern.search(text)]
        return self._result(matches)

    @staticmethod
    def _result(matches: list[str]) -> dict[str, Any]:
        return {
            "detected": bool(matches),
            "categories": matches,
            "warning": "Warning: This prompt contains potentially harmful or dangerous content.",
            "warning_zh": "警告：此提示可能包含有害或危险内容。",
            "summary": (
                "Potentially harmful or dangerous intent was detected."
                if matches else
                "No clear harmful-intent pattern was detected."
            ),
            "summary_zh": (
                "检测到可能有害或危险的意图。"
                if matches else
                "未检测到明确的有害意图模式。"
            ),
        }
