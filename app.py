"""
ACEest Fitness & Gym - Flask Web Application
DevOps Assignment - Introduction to DevOps (CSIZG514/SEZG514/SEUSZG514)
"""

from flask import Flask, jsonify, request

app = Flask(__name__)

# ── In-memory data store ───────────────────────────────────────────────────────
PROGRAMS = {
    "Fat Loss (FL)": {
        "workout": (
            "Mon: Back Squat 5x5 + Core\n"
            "Tue: EMOM 20min Assault Bike\n"
            "Wed: Bench Press + 21-15-9\n"
            "Thu: Deadlift + Box Jumps\n"
            "Fri: Zone 2 Cardio 30min"
        ),
        "diet": (
            "Breakfast: Egg Whites + Oats\n"
            "Lunch: Grilled Chicken + Brown Rice\n"
            "Dinner: Fish Curry + Millet Roti\n"
            "Target: ~2000 kcal"
        ),
        "calorie_factor": 22,
    },
    "Muscle Gain (MG)": {
        "workout": (
            "Mon: Squat 5x5\n"
            "Tue: Bench 5x5\n"
            "Wed: Deadlift 4x6\n"
            "Thu: Front Squat 4x8\n"
            "Fri: Incline Press 4x10\n"
            "Sat: Barbell Rows 4x10"
        ),
        "diet": (
            "Breakfast: Eggs + Peanut Butter Oats\n"
            "Lunch: Chicken Biryani\n"
            "Dinner: Mutton Curry + Rice\n"
            "Target: ~3200 kcal"
        ),
        "calorie_factor": 35,
    },
    "Beginner (BG)": {
        "workout": (
            "Full Body Circuit:\n"
            "- Air Squats\n"
            "- Ring Rows\n"
            "- Push-ups\n"
            "Focus: Technique & Consistency"
        ),
        "diet": (
            "Balanced Tamil Meals\n"
            "Idli / Dosa / Rice + Dal\n"
            "Protein Target: 120g/day"
        ),
        "calorie_factor": 26,
    },
}

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


@app.route("/programs", methods=["GET"])
def get_programs():
    """Return all available fitness programs."""
    return jsonify({"programs": list(PROGRAMS.keys())})


@app.route("/programs/<program_name>", methods=["GET"])
def get_program(program_name: str):
    """Return details for a specific program."""
    program = PROGRAMS.get(program_name)
    if not program:
        return jsonify({"error": f"Program '{program_name}' not found"}), 404
    return jsonify({"program": program_name, "details": program})

# ── Entry point ────────────────────────────────────────────────────────────────
if __name__ == "__main__":
    app.run(host="0.0.0.0", port=5000, debug=False)
