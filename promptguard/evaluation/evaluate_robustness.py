
"""Evaluate PromptGuard on a separate robustness dataset."""

import json
import sys
from pathlib import Path

PROJECT_ROOT = Path(__file__).resolve().parents[2]

if str(PROJECT_ROOT) not in sys.path:
    sys.path.insert(0, str(PROJECT_ROOT))

from promptguard.detectors.combined_detector import CombinedDetector
from promptguard.services.metrics import calculate_metrics


DATASET_PATH = (
    PROJECT_ROOT / "promptguard" / "data" / "robustness_cases.json"
)


def load_dataset(dataset_path=DATASET_PATH):
    """Load and validate the robustness dataset."""
    with dataset_path.open("r", encoding="utf-8") as file:
        cases = json.load(file)

    if not isinstance(cases, list) or not cases:
        raise ValueError(
            "The robustness dataset must be a non-empty JSON list."
        )

    seen_ids = set()

    for case in cases:
        if not isinstance(case, dict):
            raise ValueError("Each dataset entry must be a JSON object.")

        for field in ("id", "prompt", "expected_label"):
            if field not in case:
                raise ValueError(
                    f"Dataset entry is missing required field: {field}"
                )

        if not isinstance(case["prompt"], str) or not case["prompt"].strip():
            raise ValueError(
                f"Case {case['id']} must contain a non-empty prompt."
            )

        if case["expected_label"] not in {"attack", "safe"}:
            raise ValueError(
                f"Invalid expected label in case {case['id']}: "
                f"{case['expected_label']!r}"
            )

        if case["id"] in seen_ids:
            raise ValueError(f"Duplicate case ID: {case['id']}")

        seen_ids.add(case["id"])

    return cases


def predict_label(detector, prompt):
    """Apply the same threshold as the main evaluation."""
    result = detector.analyze(prompt)
    score = result.get("score", 0)
    return "attack" if score >= 25 else "safe"


def run_evaluation(dataset_path=DATASET_PATH):
    """Return robustness metrics and individual predictions."""
    cases = load_dataset(dataset_path)
    detector = CombinedDetector()

    expected = []
    predicted = []
    details = []

    for case in cases:
        prediction = predict_label(detector, case["prompt"])
        actual = case["expected_label"]

        expected.append(actual)
        predicted.append(prediction)

        details.append({
            "id": case["id"],
            "category": case.get("category", "uncategorized"),
            "expected": actual,
            "predicted": prediction,
            "correct": prediction == actual,
        })

    metrics = calculate_metrics(expected, predicted)
    return metrics, details


def main():
    try:
        metrics, details = run_evaluation()
    except (OSError, json.JSONDecodeError, ValueError, KeyError) as error:
        print(f"Robustness evaluation failed: {error}", file=sys.stderr)
        return 1

    print("\nPromptGuard Robustness Evaluation")
    print("=" * 38)
    print(f"Dataset:        {DATASET_PATH.name}")
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
    print("-" * 70)

    for item in details:
        status = "PASS" if item["correct"] else "MISS"
        print(
            f"{item['id']} | {status:4} | "
            f"expected={item['expected']:5} | "
            f"predicted={item['predicted']:5} | "
            f"{item['category']}"
        )

    misses = [item for item in details if not item["correct"]]

    if misses:
        print("\nCases to Investigate")
        for item in misses:
            print(
                f"- {item['id']} ({item['category']}): "
                f"expected {item['expected']}, "
                f"predicted {item['predicted']}"
            )
    else:
        print("\nNo classification errors on this dataset.")

    return 0


if __name__ == "__main__":
    raise SystemExit(main())
