
"""Evaluate PromptGuard against the labeled JSON test dataset."""

import json
import sys
from pathlib import Path

# Make the project root importable when running this script directly.
PROJECT_ROOT = Path(__file__).resolve().parents[2]
if str(PROJECT_ROOT) not in sys.path:
    sys.path.insert(0, str(PROJECT_ROOT))

from promptguard.detectors.combined_detector import CombinedDetector
from promptguard.detectors.risk_policy import is_attack_score
from promptguard.services.metrics import calculate_metrics


DATASET_PATH = PROJECT_ROOT / "promptguard" / "data" / "test_cases.json"


def load_dataset(dataset_path=DATASET_PATH):
    """Load and validate the labeled evaluation dataset."""
    with dataset_path.open("r", encoding="utf-8") as file:
        cases = json.load(file)

    if not isinstance(cases, list) or not cases:
        raise ValueError(
            "The evaluation dataset must be a non-empty JSON list."
        )

    for case in cases:
        if not isinstance(case, dict):
            raise ValueError("Each dataset entry must be a JSON object.")

        for field in ("id", "prompt", "expected_label"):
            if field not in case:
                raise ValueError(
                    f"Dataset entry is missing required field: {field}"
                )

        if case["expected_label"] not in {"attack", "safe"}:
            raise ValueError(
                f"Invalid expected label in case {case['id']}: "
                f"{case['expected_label']!r}"
            )

    return cases


def predict_label(detector, prompt):
    """Convert the detector's risk assessment into an attack/safe label."""
    result = detector.analyze(prompt)
    score = result.get("score", 0)
    return "attack" if is_attack_score(score) else "safe"


def run_evaluation(dataset_path=DATASET_PATH):
    """Evaluate all cases and return metrics and individual predictions."""
    cases = load_dataset(dataset_path)
    detector = CombinedDetector()

    expected = []
    predicted = []
    details = []

    for case in cases:
        prediction = predict_label(detector, case["prompt"])

        expected.append(case["expected_label"])
        predicted.append(prediction)

        details.append({
            "id": case["id"],
            "category": case.get("category", "uncategorized"),
            "expected": case["expected_label"],
            "predicted": prediction,
            "correct": prediction == case["expected_label"],
        })

    metrics = calculate_metrics(expected, predicted)
    return metrics, details


def main():
    try:
        metrics, details = run_evaluation()
    except (OSError, json.JSONDecodeError, ValueError, KeyError) as error:
        print(f"Evaluation failed: {error}", file=sys.stderr)
        return 1

    print("\nPromptGuard Evaluation Results")
    print("=" * 36)
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
    print("-" * 60)

    for item in details:
        status = "PASS" if item["correct"] else "MISS"
        print(
            f"{item['id']} | {status:4} | "
            f"expected={item['expected']:5} | "
            f"predicted={item['predicted']:5} | "
            f"{item['category']}"
        )

    return 0


if __name__ == "__main__":
    raise SystemExit(main())
