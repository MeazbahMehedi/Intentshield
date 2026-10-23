# PromptGuard Evaluation Report

## 1. Overview

PromptGuard is a prototype system for detecting potential prompt injection attempts using pattern-based and structured-rule detection.

This report documents the baseline evaluation and a separate robustness evaluation performed during development.

## 2. Evaluation Methodology

Both evaluations use labeled JSON datasets. Each case contains a prompt, an expected label (`attack` or `safe`), and a category.

The evaluation scripts run the combined detector and compare its prediction with the expected label. Predictions use a score threshold of 25: scores at or above the threshold are classified as attacks.

Two datasets are evaluated:

- **Baseline dataset:** `promptguard/data/test_cases.json`
- **Robustness dataset:** `promptguard/data/robustness_cases.json`

## 3. Baseline Evaluation

The baseline dataset contains 48 labeled prompts: 24 attacks and 24 safe prompts.

| Metric | Result |
|---|---:|
| Total cases | 48 |
| Accuracy | 100.0% |
| Precision | 100.0% |
| Recall | 100.0% |
| F1-score | 100.0% |
| True positives | 24 |
| True negatives | 24 |
| False positives | 0 |
| False negatives | 0 |

### Interpretation

The detector correctly classified all 48 cases in this dataset. No false positives or false negatives were observed.

## 4. Robustness Evaluation

The robustness dataset contains 12 prompts: 6 attacks and 6 safe prompts. It includes paraphrased injection, instruction override, prompt extraction, jailbreak attempts, indirect injection, unauthorized tool use, security education, security defense, translation, programming, and document analysis.

| Metric | Result |
|---|---:|
| Total cases | 12 |
| Accuracy | 100.0% |
| Precision | 100.0% |
| Recall | 100.0% |
| F1-score | 100.0% |
| True positives | 6 |
| True negatives | 6 |
| False positives | 0 |
| False negatives | 0 |

### Interpretation

All 12 robustness cases were correctly classified. This indicates that the current detector handled these selected examples, including several attack phrasings and benign security-related requests.

However, the robustness dataset is small and was used during detector development. These results should not be interpreted as evidence of generalization to unseen or real-world attacks.

## 5. Reproducing the Results

Run the following commands from the repository root with the Python environment activated:

```powershell
python -m pytest -q
python -m promptguard.evaluation.evaluate
python -m promptguard.evaluation.evaluate_robustness
```

The automated test suite completed with 23 passing tests during this evaluation. Both evaluation scripts reported no classification errors on their respective datasets.

## 6. Limitations

1. **Small datasets:** The baseline contains 48 cases and the robustness dataset contains 12. These sample sizes are insufficient to establish broad real-world detection performance.
2. **Development-set tuning:** Detector rules were adjusted using examples from the evaluated datasets. The reported metrics may therefore overestimate performance on unseen prompts.
3. **Pattern-based limitations:** Regex and structured rules can miss novel attacks, unusual phrasing, multilingual attacks, or attacks that do not match known patterns.
4. **Context sensitivity:** Benign educational or translation requests may contain attack-like phrases. Context-based exceptions can reduce false positives, but overly broad exceptions may also allow malicious prompts to evade detection.
5. **No production guarantee:** PromptGuard is a prototype evaluation and defense project, not a guarantee that detected attacks will be blocked or that all attacks will be identified.

## 7. Future Work

- Collect a larger dataset from independent sources.
- Separate development examples from a held-out test set.
- Add paraphrased, multilingual, obfuscated, and indirect prompt injection cases.
- Perform ablation studies to measure the contribution of individual detectors.
- Track false positives and false negatives as new test cases are added.
- Evaluate detection thresholds and compare precision-recall trade-offs.
- Test against an independently maintained benchmark before making claims about generalization.

## 8. Conclusion

On the current development datasets, PromptGuard achieved 100% accuracy on 48 baseline cases and 12 robustness cases. These results are useful as a reproducible development checkpoint, but they do not establish real-world robustness. Independent testing on larger, held-out datasets is necessary to evaluate generalization.