
"""Shared risk thresholds for IntentShield heuristic scoring."""

MAX_SCORE = 100

MEDIUM_RISK_THRESHOLD = 25
HIGH_RISK_THRESHOLD = 60


def risk_level_for_score(score: int) -> str:
    """Map a bounded heuristic score to its risk level."""
    if score >= HIGH_RISK_THRESHOLD:
        return "High"
    if score >= MEDIUM_RISK_THRESHOLD:
        return "Medium"
    return "Low"


def is_attack_score(score: int) -> bool:
    """Return whether a score meets the existing evaluation threshold."""
    return score >= MEDIUM_RISK_THRESHOLD
