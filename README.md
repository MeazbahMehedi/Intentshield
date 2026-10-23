# PromptGuard — Phase 2: Detection engine and UI improvements

PromptGuard is a local Flask application for exploring prompt-injection detection. This phase improves the existing heuristic engine and dashboard; it does **not** call or require an AI model.

## Run on Windows / PyCharm

1. Extract the ZIP and open the project folder containing `app.py` in PyCharm.
2. Open the PyCharm terminal and run:

```powershell
python -m venv .venv
.\.venv\Scripts\Activate.ps1
python -m pip install --upgrade pip
pip install -r requirements.txt
python app.py
```

3. Open http://127.0.0.1:5000/ in your browser.
4. Stop the server with `Ctrl+C` in the terminal.

If PowerShell blocks activation, run `Set-ExecutionPolicy -Scope Process -ExecutionPolicy Bypass` in that terminal and activate again.

## Phase 2 improvements

- Added a `PatternDetector` for common instruction overrides, hidden-prompt extraction, jailbreak phrasing, credential exposure, data exfiltration, role impersonation, dangerous weapon-construction requests, and explicit violent-threat phrasing.
- Added a configurable `RuleDetector` that loads multi-signal rules from `promptguard/data/rules.json`.
- Added a `CombinedDetector` that merges findings, avoids duplicate finding names, caps the weighted score at 100, and returns consistent Low / Medium / High risk metadata.
- Kept `analyze_prompt()` as a compatibility wrapper so existing route tests and UI flow continue to work.
- Improved the dashboard with combined-engine status, a risk-scale guide, detector metadata, clearer score interpretation, a clear-input control, a more useful character counter, and a submitting state.
- Session statistics now count all scans and flagged results for the current session while the history table retains only the latest eight entries.
- Added detector unit tests alongside the original route tests.

## Detection behavior and limitations

The displayed score is a weighted rule-match indicator, **not** a probability of maliciousness. Pattern and phrase matching can miss novel attacks and can flag benign text discussing attacks. The engine cannot determine actual intent or imminence from text alone. A Low score is not a safety guarantee. Do not paste real credentials, API keys, or private information.

Scan history is stored in the Flask browser session, not in a permanent database. This phase does not add AI inference, model downloads, or external API calls.

## Tests

With dependencies installed in the active environment:

```powershell
python -m pytest -v
```

The suite covers the existing route smoke tests plus detector normalization, combined findings, structured rules, score bounds, and UI metadata.

## Project layout

- `app.py` — starts the local Flask development server.
- `promptguard/detectors/base.py` — shared detector interface and normalization.
- `promptguard/detectors/pattern_detector.py` — regex-based signal detection.
- `promptguard/detectors/rule_detector.py` — configurable multi-signal rules.
- `promptguard/detectors/combined_detector.py` — unified assessment and risk scoring.
- `promptguard/data/rules.json` — configurable structured rules.
- `promptguard/routes/main.py` — homepage, prompt scan, session statistics, and health endpoint.
- `promptguard/templates/` — dashboard templates.
- `promptguard/static/css/style.css` — responsive dashboard styling.
- `promptguard/static/js/app.js` — character counter, sample/clear controls, and form feedback.
- `tests/` — route and detector tests.
