from __future__ import annotations

import os
from flask import Flask, jsonify, render_template, request
from pathlib import Path

from wellness_manager import WellnessManager

DATA_FILE = Path(__file__).parent / "wellness_data.json"
DATABASE_URL = os.environ.get("DATABASE_URL")
manager = WellnessManager(DATA_FILE, db_url=DATABASE_URL)
app = Flask(__name__, static_folder="static", template_folder="templates")


@app.route("/", methods=["GET"])
def ui_index():
    return render_template("index.html")


@app.route("/api/info", methods=["GET"])
def api_info() -> tuple[dict[str, object], int]:
    return (
        {
            "app": "Mental Wellness Manager",
            "routes": [
                {"path": "/api/entries", "methods": ["GET", "POST"]},
                {"path": "/api/summary", "methods": ["GET"]},
                {"path": "/api/trends", "methods": ["GET"]},
            ],
        },
        200,
    )


@app.route("/api/entries", methods=["GET"])
def list_entries() -> tuple[list[dict[str, object]], int]:
    entries = [entry.to_dict() for entry in manager.list_entries()]
    return entries, 200


@app.route("/api/entries", methods=["POST"])
def create_entry() -> tuple[dict[str, object], int]:
    payload = request.get_json(silent=True)
    if not isinstance(payload, dict):
        return {"error": "JSON payload required"}, 400

    required_fields = ["mood", "sleep", "exercise", "water", "meditation", "stress"]
    missing = [field for field in required_fields if field not in payload]
    if missing:
        return {"error": "Missing fields", "missing": missing}, 400

    try:
        entry = manager.add_entry(
            mood=int(payload["mood"]),
            sleep_hours=float(payload["sleep"]),
            exercise_minutes=int(payload["exercise"]),
            water_glasses=int(payload["water"]),
            meditation_minutes=int(payload["meditation"]),
            stress_level=int(payload["stress"]),
            notes=str(payload.get("notes", "") or ""),
        )
    except (TypeError, ValueError) as exc:
        return {"error": "Invalid field values", "details": str(exc)}, 400

    return entry.to_dict(), 201


@app.route("/api/summary", methods=["GET"])
def summary() -> tuple[dict[str, object], int]:
    return manager.get_summary(), 200


@app.route("/api/trends", methods=["GET"])
def trends() -> tuple[dict[str, object], int]:
    return manager.get_trends(), 200


if __name__ == "__main__":
    app.run(host="0.0.0.0", port=int(__import__("os").environ.get("PORT", 8080)), debug=False)
