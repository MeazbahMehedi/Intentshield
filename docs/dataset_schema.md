# PromptGuard Evaluation Dataset

## Purpose

The labeled datasets evaluate PromptGuard's ability to identify prompt-injection attempts and potentially harmful prompts while distinguishing them from benign requests. The labels are expected outcomes for evaluation, not a guarantee that the detector will be correct.

## Current dataset sizes

| Dataset | Total | Attack | Safe |
|---|---:|---:|---:|
| `combined_cases.json` | 1,292 | 992 | 300 |
| `test_cases.json` | 1,292 | 992 | 300 |
| `development_cases.json` | 120 | 80 | 40 |
| `holdout_cases.json` | 150 | 96 | 54 |
| `robustness_cases.json` | 75 | 48 | 27 |

`combined_cases.json` and `test_cases.json` are synchronized copies under the current project convention. Do not count their duplicate records twice when reporting unique examples.

## Fields

The main combined/test files preserve this schema:

| Field | Type | Description |
|---|---|---|
| `id` | String | Unique identifier for a record in the file |
| `prompt` | String | Text submitted to the detector |
| `expected_label` | String | Expected classification: `attack` or `safe` |
| `category` | String | Main prompt technique or benign category |
| `reason` | String | Explanation for the assigned label |

The development, holdout, and robustness datasets preserve their original four-field structure: `id`, `prompt`, `expected_label`, and `category`.

## Coverage

Attack examples cover instruction override, prompt extraction, jailbreaks, authority impersonation, indirect injection, unauthorized tool use, data exfiltration, credential theft, policy bypass, mixed Chinese-English prompts, Chinese-language injection, Unicode and encoding tricks, emotional pressure, nested/multi-step instructions, retrieval poisoning, code-comment injection, persistent instructions, structured-format injection, and potentially harmful requests.

Safe examples cover ordinary writing, programming, education, translation, planning, security education, defensive cybersecurity, privacy compliance, prevention/support requests, science safety, document analysis, data processing, and creative writing.

## Labels and limitations

- `attack`: a prompt intended to exercise prompt-injection or potentially harmful-request detection.
- `safe`: a benign request, including defensive or educational content that may discuss security risks.

PromptGuard's current implementation is heuristic. False positives and false negatives are expected. The separate harmful-content warning is not the same as the injection score. Evaluate the combined classifier and each detector separately when reporting results.
