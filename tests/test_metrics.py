
import pytest

from promptguard.services.metrics import calculate_metrics


def test_perfect_predictions():
    result = calculate_metrics(
        ["attack", "attack", "safe", "safe"],
        ["attack", "attack", "safe", "safe"],
    )

    assert result["accuracy"] == 1.0
    assert result["precision"] == 1.0
    assert result["recall"] == 1.0
    assert result["f1_score"] == 1.0


def test_mixed_predictions():
    result = calculate_metrics(
        ["attack", "attack", "safe", "safe"],
        ["attack", "safe", "attack", "safe"],
    )

    assert result["true_positive"] == 1
    assert result["true_negative"] == 1
    assert result["false_positive"] == 1
    assert result["false_negative"] == 1
    assert result["accuracy"] == 0.5
    assert result["precision"] == 0.5
    assert result["recall"] == 0.5
    assert result["f1_score"] == 0.5


def test_zero_division_returns_zero():
    result = calculate_metrics(
        ["safe", "safe"],
        ["safe", "safe"],
    )

    assert result["precision"] == 0.0
    assert result["recall"] == 0.0
    assert result["f1_score"] == 0.0
    assert result["accuracy"] == 1.0


def test_mismatched_lengths_raise_error():
    with pytest.raises(ValueError):
        calculate_metrics(["attack"], ["attack", "safe"])


def test_empty_dataset_raises_error():
    with pytest.raises(ValueError):
        calculate_metrics([], [])


def test_invalid_label_raises_error():
    with pytest.raises(ValueError):
        calculate_metrics(["unknown"], ["attack"])
