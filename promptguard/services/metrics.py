
"""Evaluation metrics for PromptGuard's binary prompt classifier."""


def calculate_metrics(expected_labels, predicted_labels):
    """Calculate binary classification metrics.

    Labels must be "attack" or "safe".
    Treat "attack" as the positive class.
    """
    if len(expected_labels) != len(predicted_labels):
        raise ValueError(
            "Expected labels and predicted labels must have equal lengths."
        )

    if not expected_labels:
        raise ValueError("At least one labeled example is required.")

    valid_labels = {"attack", "safe"}

    for label in expected_labels + predicted_labels:
        if label not in valid_labels:
            raise ValueError(
                f"Invalid label: {label!r}. Use 'attack' or 'safe'."
            )

    true_positive = sum(
        expected == "attack" and predicted == "attack"
        for expected, predicted in zip(expected_labels, predicted_labels)
    )
    true_negative = sum(
        expected == "safe" and predicted == "safe"
        for expected, predicted in zip(expected_labels, predicted_labels)
    )
    false_positive = sum(
        expected == "safe" and predicted == "attack"
        for expected, predicted in zip(expected_labels, predicted_labels)
    )
    false_negative = sum(
        expected == "attack" and predicted == "safe"
        for expected, predicted in zip(expected_labels, predicted_labels)
    )

    total = len(expected_labels)

    precision = (
        true_positive / (true_positive + false_positive)
        if true_positive + false_positive else 0.0
    )
    recall = (
        true_positive / (true_positive + false_negative)
        if true_positive + false_negative else 0.0
    )
    f1_score = (
        2 * precision * recall / (precision + recall)
        if precision + recall else 0.0
    )
    accuracy = (true_positive + true_negative) / total

    return {
        "total": total,
        "true_positive": true_positive,
        "true_negative": true_negative,
        "false_positive": false_positive,
        "false_negative": false_negative,
        "accuracy": round(accuracy, 4),
        "precision": round(precision, 4),
        "recall": round(recall, 4),
        "f1_score": round(f1_score, 4),
    }
