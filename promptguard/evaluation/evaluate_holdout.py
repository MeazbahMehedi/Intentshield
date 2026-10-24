
"""Evaluate PromptGuard on a separate holdout dataset.

Do not tune detection rules against this dataset and then continue
describing it as an independent holdout.
"""
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


DATASET_PATH = (
    PROJECT_ROOT / "promptguard" / "data" / "holdout_cases.json"
)
VALID_LABELS = {"attack", "safe"}


def load_dataset(
    dataset_path: Path = DATASET_PATH,
) -> list[dict[str, Any]]:
    """Load and validate the holdout dataset."""
    with dataset_path.open("r", encoding="utf-8") as file:
        cases = json.load(file)

    if not isinstance(cases, list) or not cases:
        raise ValueError(
            "The holdout dataset must be a non-empty JSON list."
        )

    seen_ids: set[str] = set()

    for index, case in enumerate(cases):
        if not isinstance(case, dict):
            raise ValueError(
                f"Dataset entry {index} must be a JSON object."
            )

        for field in ("id", "prompt", "expected_label", "category"):
            if field not in case:
                raise ValueError(
                    f"Dataset entry {index} is missing field {field!r}."
                )

        case_id = case["id"]

        if not isinstance(case_id, str) or not case_id.strip():
            raise ValueError(
                f"Dataset entry {index} must have a non-empty string ID."
            )

        if case_id in seen_ids:
            raise ValueError(f"Duplicate holdout case ID: {case_id}")

        seen_ids.add(case_id)

        if not isinstance(case["prompt"], str) or not case["prompt"].strip():
            raise ValueError(
                f"Prompt in case {case_id} must be a non-empty string."
            )

        if case["expected_label"] not in VALID_LABELS:
            raise ValueError(
                f"Invalid expected label in case {case_id}: "
                f"{case['expected_label']!r}"
            )

        if not isinstance(case["category"], str):
            raise ValueError(
                f"Category in case {case_id} must be a string."
            )

    return cases


def predict_label(
    detector: CombinedDetector,
    prompt: str,
) -> str:
    """Convert a detector risk score to the evaluation label."""
    result = detector.analyze(prompt)
    harmful = result.get("harmful_content", {}).get("detected", False)
    return (
        "attack"
        if is_attack_score(result.get("score", 0)) or harmful
        else "safe"
    )


def run_evaluation(
    dataset_path: Path = DATASET_PATH,
) -> tuple[dict[str, Any], list[dict[str, Any]]]:
    """Evaluate all cases and return aggregate metrics and case details."""
    cases = load_dataset(dataset_path)
    detector = CombinedDetector()

    expected: list[str] = []
    predicted: list[str] = []
    details: list[dict[str, Any]] = []

    for case in cases:
        prediction = predict_label(detector, case["prompt"])
        actual = case["expected_label"]

        expected.append(actual)
        predicted.append(prediction)

        details.append({
            "id": case["id"],
            "category": case["category"],
            "expected": actual,
            "predicted": prediction,
            "correct": prediction == actual,
        })

    metrics = calculate_metrics(expected, predicted)
    return metrics, details


def main() -> int:
    """Print the holdout evaluation report."""
    try:
        metrics, details = run_evaluation()
    except (OSError, json.JSONDecodeError, ValueError, KeyError) as error:
        print(f"Holdout evaluation failed: {error}", file=sys.stderr)
        return 1

    print("\nPromptGuard Holdout Evaluation")
    print("=" * 34)
    print(f"Total prompts:  {metrics['total']}")
    print(f"Accuracy:       {metrics['accuracy']:.1%}")
    print(f"Precision:      {metrics['precision']:.1%}")
    print(f"Recall:         {metrics['recall']:.1%}")
    print(f"F1-score:       {metrics['f1_score']:.1%}")

    print("\nConfusion Matrix Counts")
    print(f"True positives:  {metrics['true_positive']}")
    print(f"True negatives:  {metrics['true_negative']}")
    print(f"False positives: {metrics['false_positive']}")
    print(f"False negatives: {metrics['false_negative']}")

    print("\nIndividual Results")
    print("-" * 65)

    for item in details:
        status = "PASS" if item["correct"] else "MISS"
        print(
            f"{item['id']} | {status:4} | "
            f"expected={item['expected']:5} | "
            f"predicted={item['predicted']:5} | "
            f"{item['category']}"
        )

    correct_count = sum(item["correct"] for item in details)
    print(f"\nCorrect: {correct_count}/{len(details)}")

    if correct_count != len(details):
        print(
            "Review the misses, but do not tune against this holdout "
            "and continue calling it independent."
        )

    return 0


if __name__ == "__main__":
    raise SystemExit(main())
