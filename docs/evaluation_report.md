# Evaluation report

Verified 24 October 2026. Synthetic, previously exposed data; these numbers are not evidence of unseen real-world performance. ML uses development data only. Clean runs exclude normalized exact and near overlaps against the main corpus and development split.

| Split | Mode | N | Excluded | Precision | Recall | F1 | FPR | FNR |
|---|---|---:|---:|---:|---:|---:|---:|---:|
| holdout | rules | 142 | 8 | 93.1% | 73.6% | 82.2% | 9.8% | 26.4% |
| holdout | hybrid | 142 | 8 | 94.3% | 91.2% | 92.7% | 9.8% | 8.8% |
| holdout | ml | 142 | 8 | 100.0% | 70.3% | 82.6% | 0.0% | 29.7% |
| robustness | rules | 71 | 4 | 100.0% | 90.9% | 95.2% | 0.0% | 9.1% |
| robustness | hybrid | 71 | 4 | 100.0% | 100.0% | 100.0% | 0.0% | 0.0% |
| robustness | ml | 71 | 4 | 100.0% | 81.8% | 90.0% | 0.0% | 18.2% |
| test | rules | 1292 | 0 | 98.9% | 83.9% | 90.8% | 3.0% | 16.1% |
| test | hybrid | 1292 | 0 | 99.0% | 91.4% | 95.1% | 3.0% | 8.6% |
| test | ml | 1292 | 0 | 100.0% | 56.5% | 72.2% | 0.0% | 43.5% |

Thresholds: rule/injection score ≥25; lexical ML score ≥65. Combined attack labels also include harmful-content and sensitive-data signals. These evaluation thresholds are fixed for comparability; runtime gateway decisions use the editable policy.

The audit found 0 normalized cross-split exact duplicates and 22 near-overlap candidates (10 development, 8 holdout, 4 robustness). Jaccard word-set similarity ≥0.85 flags candidates, not proven semantic duplicates. Filtered files are evaluated in memory; source datasets remain unchanged. Main/test and combined are aliases and count once.

Full fingerprints, per-category/language metrics, dependency versions and latencies: `verification_results.json`. Current ML is character TF-IDF plus logistic regression, not an embedding model or LLM. Scores are not calibrated probabilities. First inference may include model training; timings vary across machines.

Do not tune on this holdout after reading these results and then claim independent validation. Collect a new human-reviewed corpus for a stronger final research evaluation.
