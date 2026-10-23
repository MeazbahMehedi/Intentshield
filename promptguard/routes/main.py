
"""Dashboard and heuristic prompt scanning routes."""

from datetime import datetime
from flask import Blueprint, render_template, request, session

from promptguard.detectors import CombinedDetector

main_bp = Blueprint("main", __name__)
_detector = CombinedDetector()


def analyze_prompt(prompt):
    """Compatibility wrapper around the combined local detection engine."""
    return _detector.analyze(prompt)


@main_bp.route("/", methods=["GET", "POST"])
def index():
    result = None
    prompt = ""
    error = None

    if request.method == "POST":
        prompt = request.form.get("prompt", "").strip()[:10000]

        if prompt:
            result = analyze_prompt(prompt)

            history = session.get("history", [])
            session["scan_count"] = int(session.get("scan_count", 0)) + 1
            session["flagged_count"] = int(session.get("flagged_count", 0)) + int(result["level"] in ("Medium", "High"))
            session["high_risk_count"] = int(session.get("high_risk_count", 0)) + int(result["level"] == "High")
            history.insert(0, {
                "time": datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
                "preview": prompt[:100].replace("\n", " "),
                "level": result["level"],
                "score": result["score"],
                "findings": len(result["findings"]),
            })

            session["history"] = history[:8]
            session.modified = True
        else:
            error = "Please enter a prompt before scanning."

    history = session.get("history", [])

    return render_template(
        "index.html",
        result=result,
        prompt=prompt,
        error=error,
        history=history,
        total_scans=int(session.get("scan_count", len(history))),
        threats=int(session.get("flagged_count", sum(1 for item in history if item["level"] in ("Medium", "High")))),
        high_risk=int(session.get("high_risk_count", sum(1 for item in history if item["level"] == "High"))),
    )


@main_bp.get("/health")
def health():
    return "ok", 200
