"""
ACEest Fitness & Gym - Flask Web Application
DevOps Assignment - Introduction to DevOps (CSIZG514/SEZG514/SEUSZG514)
"""

from flask import Flask, jsonify, request

app = Flask(__name__)

clients = {}  # { name: { age, weight, program, adherence } }


# ── Helper ─────────────────────────────────────────────────────────────────────
def calculate_calories(weight_kg: float, program_name: str) -> int:
    """Return estimated daily calorie target for a client."""
    factor = PROGRAMS.get(program_name, {}).get("calorie_factor", 0)
    return int(weight_kg * factor)


def calculate_bmi(weight_kg: float, height_cm: float) -> float:
    """Return BMI rounded to one decimal place."""
    if height_cm <= 0:
        raise ValueError("height_cm must be > 0")
    return round(weight_kg / (height_cm / 100) ** 2, 1)


# ── Routes ─────────────────────────────────────────────────────────────────────
@app.route("/")
def index():
    return jsonify({"message": "ACEest Fitness & Gym API", "status": "running"})


@app.route("/health")
def health():
    return jsonify({"status": "healthy"})

# ── Entry point ────────────────────────────────────────────────────────────────
if __name__ == "__main__":
    app.run(host="0.0.0.0", port=5000, debug=False)
