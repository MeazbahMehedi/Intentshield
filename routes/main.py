"""Dashboard, heuristic prompt scanning routes, and JSON API for the live UI."""

from datetime import datetime
from flask import Blueprint, jsonify, render_template, request, session

from promptguard.detectors import CombinedDetector

main_bp = Blueprint("main", __name__)
_detector = CombinedDetector()

MAX_PROMPT_CHARS = 10000
MAX_BATCH_ITEMS = 50


def analyze_prompt(prompt):
    """Compatibility wrapper around the combined local detection engine."""
    return _detector.analyze(prompt)


def _record_scan(prompt, result):
    """Update session counters/history and return the new history entry."""
    entry = {
        "time": datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
        "preview": prompt[:100].replace("\n", " "),
        "level": result["level"],
        "score": result["score"],
        "findings": len(result["findings"]),
    }
    history = session.get("history", [])
    session["scan_count"] = int(session.get("scan_count", 0)) + 1
    session["flagged_count"] = int(session.get("flagged_count", 0)) + int(result["level"] in ("Medium", "High"))
    session["high_risk_count"] = int(session.get("high_risk_count", 0)) + int(result["level"] == "High")
    history.insert(0, entry)
    session["history"] = history[:8]
    session.modified = True
    return entry


def _stats():
    history = session.get("history", [])
    return {
        "total_scans": int(session.get("scan_count", len(history))),
        "threats": int(session.get("flagged_count", sum(1 for i in history if i["level"] in ("Medium", "High")))),
        "high_risk": int(session.get("high_risk_count", sum(1 for i in history if i["level"] == "High"))),
    }


@main_bp.route("/", methods=["GET", "POST"])
def index():
    result = None
    prompt = ""
    error = None

    if request.method == "POST":
        prompt = request.form.get("prompt", "").strip()[:MAX_PROMPT_CHARS]
        if prompt:
            result = analyze_prompt(prompt)
            _record_scan(prompt, result)
        else:
            error = "Please enter a prompt before scanning."

    return render_template(
        "index.html",
        result=result,
        prompt=prompt,
        error=error,
        history=session.get("history", []),
        **_stats(),
    )


@main_bp.post("/api/scan")
def api_scan():
    """Scan one prompt and return JSON (used by the live UI, no page reload)."""
    data = request.get_json(silent=True) or {}
    prompt = str(data.get("prompt", "")).strip()[:MAX_PROMPT_CHARS]
    if not prompt:
        return jsonify({"error": "Please enter a prompt before scanning."}), 400
    result = analyze_prompt(prompt)
    entry = _record_scan(prompt, result)
    return jsonify({"result": result, "history_entry": entry, "stats": _stats()})


@main_bp.post("/api/batch")
def api_batch():
    """Scan up to MAX_BATCH_ITEMS prompts (one per line) and return summaries."""
    data = request.get_json(silent=True) or {}
    items = data.get("prompts", [])
    if not isinstance(items, list):
        return jsonify({"error": "'prompts' must be a list."}), 400
    prompts = [str(p).strip()[:MAX_PROMPT_CHARS] for p in items if str(p).strip()][:MAX_BATCH_ITEMS]
    if not prompts:
        return jsonify({"error": "Provide at least one non-empty prompt."}), 400
    rows = []
    for p in prompts:
        r = analyze_prompt(p)
        rows.append({
            "prompt": p,
            "score": r["score"],
            "level": r["level"],
            "css": r["css"],
            "categories": r["categories"],
            "findings": [f["name"] for f in r["findings"]],
        })
    return jsonify({"rows": rows, "count": len(rows)})


@main_bp.get("/health")
def health():
    return "ok", 200
