# PromptGuard — Prompt Injection Detection and Defense Evaluation System

PromptGuard is a local Flask application for exploring prompt-injection detection and evaluating heuristic detection methods. It combines pattern-based detection with configurable structured rules, a dashboard for analyzing prompts, and a labeled dataset for measuring detector performance.

The project is developed in phases. The current implementation uses a heuristic detection engine and does **not** require an AI model or external API calls.

## Features

- Regex-based detection of common prompt-injection patterns and suspicious instructions.
- Configurable multi-signal detection rules.
- Combined detector that merges findings and produces a unified risk score.
- Web dashboard for submitting and analyzing prompts.
- Session-based scan statistics and recent scan history.
- Labeled test dataset containing attack and safe prompts.
- Evaluation metrics, including accuracy, precision, recall, and F1-score.
- Automated tests for detectors, metrics, evaluation, and application routes.

## Run on Windows / PyCharm

### 1. Open the project

Open the project folder containing `app.py` in PyCharm.

### 2. Set up the virtual environment

In the PyCharm terminal, run:

```powershell
python -m venv .venv
.\.venv\Scripts\Activate.ps1
python -m pip install --upgrade pip
pip install -r requirements.txt
```

If PowerShell blocks virtual environment activation, run:

```powershell
Set-ExecutionPolicy -Scope Process -ExecutionPolicy Bypass
.\.venv\Scripts\Activate.ps1
```

### 3. Start the application

```powershell
python app.py
```

Open [http://127.0.0.1:5000/](http://127.0.0.1:5000/) in your browser.

Stop the development server with `Ctrl+C` in the terminal.

## Detection engine

PromptGuard uses a heuristic approach to identify suspicious prompts.

### PatternDetector

Uses regular expressions to identify patterns associated with:

- Instruction overrides and hierarchy manipulation.
- Hidden prompt and confidential-context extraction.
- Jailbreak language and safety-restriction bypasses.
- Credential theft and sensitive-information requests.
- Data exfiltration and unauthorized disclosure.
- Role or authority impersonation.
- Dangerous requests and explicit violent-threat phrasing.

### RuleDetector

Loads configurable multi-signal rules from `promptguard/data/rules.json`. These rules allow related signals to be combined when evaluating a prompt.

### CombinedDetector

Combines detector findings into a unified assessment, avoids duplicate finding names, caps the weighted score at 100, and returns risk metadata.

The existing `analyze_prompt()` compatibility wrapper preserves the application's established route and UI flow.

## Dataset

The labeled evaluation dataset is located at:

`promptguard/data/test_cases.json`

The dataset contains **48 labeled prompts**:

| Label | Number of prompts |
|---|---:|
| Attack | 24 |
| Safe | 24 |
| **Total** | **48** |

Each test case includes an identifier, prompt text, expected label, and category.

The dataset structure is documented in `docs/dataset_schema.md`.

## Evaluation results

The evaluation script is located at:

`promptguard/evaluation/evaluate.py`

Run the evaluation from the project root:

```powershell
python -m promptguard.evaluation.evaluate
```

### Latest evaluation

| Metric | Result |
|---|---:|
| Total prompts | 48 |
| Accuracy | 100.0% |
| Precision | 100.0% |
| Recall | 100.0% |
| F1-score | 100.0% |
| True positives | 24 |
| True negatives | 24 |
| False positives | 0 |
| False negatives | 0 |

These results reflect the latest run against the current 48-prompt dataset. They do not guarantee perfect performance on unseen prompts. A larger, independent dataset and additional adversarial testing are needed to assess generalization.

### Metric definitions

- **Accuracy:** The proportion of all prompts classified correctly.
- **Precision:** The proportion of prompts predicted as attacks that are labeled attacks.
- **Recall:** The proportion of labeled attacks correctly detected.
- **F1-score:** The harmonic mean of precision and recall.

The evaluation converts detector risk scores into attack/safe predictions using the configured threshold. The threshold and evaluation logic are implemented in the evaluation module.

## Tests

Run the automated test suite:

```powershell
python -m pytest -q
```

For more detailed output:

```powershell
python -m pytest -v
```

The latest verified test run completed with **23 passed**.

The test suite covers application routes, detector behavior, normalization, structured rules, combined findings, score bounds, metrics, and evaluation logic.

## Detection behavior and limitations

The displayed risk score is a weighted rule-match indicator, **not a probability of maliciousness**.

Pattern matching can miss novel attacks, and it can flag benign text that discusses attacks. A detector cannot reliably determine intent or imminence from text alone. A Low score is not a safety guarantee.

The reported 100% evaluation metrics apply only to the current labeled dataset. They should not be interpreted as proof of perfect detection in real-world usage.

Do not paste real credentials, API keys, or private information into the application.

Scan history is stored in the Flask browser session rather than a permanent database. The current implementation does not require AI inference, model downloads, or external API calls.

## Project layout

```text
promptguard/
├── app.py
├── requirements.txt
├── README.md
├── docs/
│   └── dataset_schema.md
├── promptguard/
│   ├── detectors/
│   │   ├── base.py
│   │   ├── pattern_detector.py
│   │   ├── rule_detector.py
│   │   └── combined_detector.py
│   ├── data/
│   │   ├── rules.json
│   │   └── test_cases.json
│   ├── evaluation/
│   │   └── evaluate.py
│   ├── services/
│   │   └── metrics.py
│   ├── routes/
│   ├── templates/
│   └── static/
└── tests/
```

Some directories may contain additional files as development continues.

## Development status

- **Phase 1:** Initial Flask application, detector foundation, and tests.
- **Phase 2:** Detection engine improvements, structured rules, combined scoring, and dashboard enhancements.
- **Phase 3:** Labeled dataset, evaluation metrics, repeatable evaluation script, and detector performance analysis.

The current 48-prompt evaluation achieves 100% accuracy, precision, recall, and F1-score on the included dataset. Further work can evaluate generalization, expand the dataset, and investigate additional defense approaches.
