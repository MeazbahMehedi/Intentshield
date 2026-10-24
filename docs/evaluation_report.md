# PromptGuard Evaluation Report

## 1. Overview

PromptGuard is a local prototype for detecting prompt-injection patterns and independently warning about potentially harmful or dangerous requests. It combines regex-based patterns, structured rules, text normalization, and a separate harmful-content detector.

This report records the current evaluation snapshot after expanding the datasets and adding the bilingual harmful-content warning. The results are useful for reproducible coursework evaluation, not as a production security guarantee.

## 2. Evaluation Methodology

The evaluation scripts compare predicted labels with the `expected_label` (`attack` or `safe`) in the JSON datasets.

A prompt is classified as `attack` for combined evaluation when either:
- the injection score meets the configured medium-risk threshold; or
- the independent harmful-content detector triggers a warning.

This combined label is used for corpus-level metrics. The UI still reports the injection score and harmful-content warning separately.

## 3. Dataset Sizes

| Dataset | Total | Attack | Safe |
|---|---:|---:|---:|
| Main (`test_cases.json`) | 1,292 | 992 | 300 |
| Development | 120 | 80 | 40 |
| Holdout | 150 | 96 | 54 |
| Robustness | 75 | 48 | 27 |

`combined_cases.json` and `test_cases.json` are synchronized copies under the project's current convention. Their records should not be counted twice when reporting unique examples.

## 4. Evaluation Snapshot

Results from the current detector and datasets:

| Dataset | Accuracy | Precision | Recall | F1-score | True positives | True negatives | False positives | False negatives |
|---|---:|---:|---:|---:|---:|---:|---:|---:|
| Main (1,292) | 86.9% | 98.9% | 83.9% | 90.8% | 832 | 291 | 9 | 160 |
| Development (120) | 94.2% | 98.7% | 92.5% | 95.5% | 74 | 39 | 1 | 6 |
| Holdout (150) | 80.7% | 93.5% | 75.0% | 83.2% | 72 | 49 | 5 | 24 |
| Robustness (75) | 93.3% | 100.0% | 89.6% | 94.5% | 43 | 27 | 0 | 5 |

### Interpretation

The current detector has high precision on the main corpus, but recall is lower: some attack prompts do not match the configured patterns or harmful-content rules. The holdout set is more challenging and demonstrates that development performance does not automatically transfer to unseen examples.

The main corpus is attack-heavy (992 attack examples versus 300 safe examples), so accuracy should not be reported alone. Precision, recall, F1-score, false positives, and false negatives are also important.

## 5. Reproducing Results

Run the following commands from the repository root with the project's Python environment activated:

```powershell
python -m pytest -q
python -m promptguard.evaluation.evaluate
python -m promptguard.evaluation.evaluate_development
python -m promptguard.evaluation.evaluate_holdout
python -m promptguard.evaluation.evaluate_robustness
```

Validate the main dataset's label counts and unique IDs:

```powershell
python -c "import json,collections; d=json.load(open('promptguard/data/test_cases.json',encoding='utf-8')); print('Total:',len(d)); print('Labels:',dict(collections.Counter(x['expected_label'] for x in d))); print('Unique IDs:',len({x['id'] for x in d}))"
```

## 6. Limitations

1. **Synthetic and curated data:** The datasets cover many techniques but do not represent every real-world prompt or model.
2. **Pattern-based detection:** Regex and structured rules may miss new attacks, indirect context-dependent behavior, or paraphrases that do not match known signals.
3. **False positives and negatives:** Benign educational or translation requests can contain attack-like wording; some harmful or injection prompts may not match a configured rule.
4. **Harmful-content warning scope:** The warning is a separate heuristic signal. It does not determine a person's intent, execute a block on an external model, or guarantee safe handling.
5. **Holdout integrity:** Use the development set to tune rules. Do not repeatedly change patterns based on holdout failures and then present the same holdout metrics as independent evidence.
6. **No production guarantee:** PromptGuard is a screening and evaluation prototype. It does not enforce access control on an external language model or guarantee that every attack will be detected.

## 7. Future Work

- Add human-reviewed, independently sourced evaluation examples.
- Report per-category precision, recall, and false-negative analysis.
- Add ablation experiments for pattern, structured-rule, normalization, and harmful-content components.
- Consider optional semantic detection, separately evaluated from the transparent rule-based baseline.
- Add versioned datasets and an evaluation manifest so results can be reproduced exactly.
- If the system is later connected to real tools or models, add authorization gates, logging controls, and explicit approval for sensitive actions.

## 8. Conclusion

PromptGuard now includes a much larger multilingual evaluation corpus, a multi-page dashboard, and an independent bilingual harmful-content warning. Current metrics show useful detection performance on the selected examples, but the holdout false negatives confirm that the system should be treated as a prototype and improved through independent testing.
