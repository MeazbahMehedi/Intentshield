"""Evaluate PromptGuard on the development dataset."""
from __future__ import annotations

import json
import sys
from pathlib import Path
from typing import Any

PROJECT_ROOT = Path(__file__).resolve().parents[2]
if str(PROJECT_ROOT) not in sys.path:
    sys.path.insert(0, str(PROJECT_ROOT))

from promptguard.detectors.combined_detector import CombinedDetector
from promptguard.detectors.risk_policy import is_attack_score
from promptguard.services.metrics import calculate_metrics

DATASET_PATH = PROJECT_ROOT / "promptguard" / "data" / "development_cases.json"
VALID_LABELS = {"attack", "safe"}


def load_dataset(path: Path = DATASET_PATH) -> list[dict[str, Any]]:
    with path.open("r", encoding="utf-8-sig") as file:
        cases = json.load(file)

    if not isinstance(cases, list) or not cases:
        raise ValueError("Dataset must be a non-empty JSON list.")

    seen_ids: set[str] = set()
    for index, case in enumerate(cases):
        if not isinstance(case, dict):
            raise ValueError(f"Entry {index} must be an object.")

        for field in ("id", "prompt", "expected_label", "category"):
            if field not in case:
                raise ValueError(f"Entry {index} is missing {field!r}.")

        case_id = case["id"]
        if not isinstance(case_id, str) or not case_id.strip():
            raise ValueError(f"Entry {index} has an invalid ID.")
        if case_id in seen_ids:
            raise ValueError(f"Duplicate case ID: {case_id}")
        seen_ids.add(case_id)

        if not isinstance(case["prompt"], str) or not case["prompt"].strip():
            raise ValueError(f"Prompt in {case_id} must be non-empty.")
        if case["expected_label"] not in VALID_LABELS:
            raise ValueError(f"Invalid label in {case_id}.")
        if not isinstance(case["category"], str):
            raise ValueError(f"Category in {case_id} must be a string.")

    return cases


def run_evaluation() -> tuple[dict[str, Any], list[dict[str, Any]]]:
    cases = load_dataset()
    detector = CombinedDetector()
    expected: list[str] = []
    predicted: list[str] = []
    details: list[dict[str, Any]] = []

    for case in cases:
        result = detector.analyze(case["prompt"])
        prediction = (
            "attack"
            if is_attack_score(result.get("score", 0))
            else "safe"
        )
        actual = case["expected_label"]
        expected.append(actual)
        predicted.append(prediction)
        details.append({
            "id": case["id"],
            "category": case["category"],
            "expected": actual,
            "predicted": prediction,
            "correct": actual == prediction,
        })

    return calculate_metrics(expected, predicted), details


def main() -> int:
    try:
        metrics, details = run_evaluation()
    except (OSError, json.JSONDecodeError, ValueError, KeyError) as error:
        print(f"Development evaluation failed: {error}", file=sys.stderr)
        return 1

    print("\nPromptGuard Development Evaluation")
    print("=" * 38)
    print(f"Total prompts: {metrics['total']}")
    print(f"Accuracy:      {metrics['accuracy']:.1%}")
    print(f"Precision:     {metrics['precision']:.1%}")
    print(f"Recall:        {metrics['recall']:.1%}")
    print(f"F1-score:      {metrics['f1_score']:.1%}")
    print("\nIndividual Results")
    print("-" * 65)

    for item in details:
        status = "PASS" if item["correct"] else "MISS"
        print(
            f"{item['id']} | {status:4} | "
            f"expected={item['expected']:5} | "
            f"predicted={item['predicted']:5} | {item['category']}"
        )

    return 0


if __name__ == "__main__":
    raise SystemExit(main())