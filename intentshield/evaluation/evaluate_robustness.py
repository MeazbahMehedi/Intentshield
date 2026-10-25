
"""Evaluate IntentShield against robustness test cases."""

import json
import sys
from pathlib import Path

# Make the project root importable when running this script directly.
PROJECT_ROOT = Path(__file__).resolve().parents[2]
if str(PROJECT_ROOT) not in sys.path:
    sys.path.insert(0, str(PROJECT_ROOT))

from intentshield.detectors.combined_detector import CombinedDetector
from intentshield.detectors.risk_policy import is_attack_score
from intentshield.services.metrics import calculate_metrics


DATASET_PATH = PROJECT_ROOT / "intentshield" / "data" / "robustness_cases.json"


def load_dataset(dataset_path=DATASET_PATH):
    """Load and validate the robustness evaluation dataset."""
    with dataset_path.open("r", encoding="utf-8") as file:
        cases = json.load(file)

    if not isinstance(cases, list) or not cases:
        raise ValueError(
            "The robustness dataset must be a non-empty JSON list."
        )

    seen_ids = set()

    for case in cases:
        if not isinstance(case, dict):
            raise ValueError(
                "Each robustness dataset entry must be a JSON object."
            )

        for field in ("id", "prompt", "expected_label"):
            if field not in case:
                raise ValueError(
                    f"Dataset entry is missing required field: {field}"
                )

        if not isinstance(case["prompt"], str):
            raise ValueError(
                f"Prompt in case {case['id']} must be a string."
            )

        if case["expected_label"] not in {"attack", "safe"}:
            raise ValueError(
                f"Invalid expected label in case {case['id']}: "
                f"{case['expected_label']!r}"
            )

        if case["id"] in seen_ids:
            raise ValueError(
                f"Duplicate case ID in robustness dataset: {case['id']}"
            )

        seen_ids.add(case["id"])

    return cases


def predict_label(detector, prompt):
    """Convert a detector score into an attack/safe label."""
    result = detector.analyze(prompt)
    score = result.get("score", 0)
    harmful = result.get("harmful_content", {}).get("detected", False)
    return "attack" if is_attack_score(score) or harmful else "safe"


def run_evaluation(dataset_path=DATASET_PATH):
    """Evaluate robustness cases and return metrics and predictions."""
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
    """Print the robustness evaluation report."""
    try:
        metrics, details = run_evaluation()
    except (OSError, json.JSONDecodeError, ValueError, KeyError) as error:
        print(
            f"Robustness evaluation failed: {error}",
            file=sys.stderr,
        )
        return 1

    print("\nIntentShield Robustness Evaluation Results")
    print("=" * 42)
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
