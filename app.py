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


@app.route("/clients", methods=["GET"])
def list_clients():
    """Return all saved clients."""
    return jsonify({"clients": list(clients.keys())})


@app.route("/clients", methods=["POST"])
def create_client():
    """Create or update a client profile."""
    data = request.get_json(force=True)

    name = (data.get("name") or "").strip()
    if not name:
        return jsonify({"error": "name is required"}), 400

    program = data.get("program", "")
    if program and program not in PROGRAMS:
        return jsonify({"error": f"Unknown program: {program}"}), 400

    weight = float(data.get("weight", 0))
    age = int(data.get("age", 0))
    adherence = int(data.get("adherence", 0))

    calories = calculate_calories(weight, program) if weight and program else 0

    clients[name] = {
        "age": age,
        "weight": weight,
        "program": program,
        "adherence": adherence,
        "calories": calories,
    }
    return jsonify({"message": f"Client '{name}' saved", "client": clients[name]}), 201


@app.route("/clients/<name>", methods=["GET"])
def get_client(name: str):
    """Return a single client's profile."""
    client = clients.get(name)
    if client is None:
        return jsonify({"error": f"Client '{name}' not found"}), 404
    return jsonify({"name": name, "profile": client})


@app.route("/clients/<name>", methods=["DELETE"])
def delete_client(name: str):
    """Delete a client profile."""
    if name not in clients:
        return jsonify({"error": f"Client '{name}' not found"}), 404
    del clients[name]
    return jsonify({"message": f"Client '{name}' deleted"})

@app.route("/calories", methods=["POST"])
def estimate_calories():
    """Estimate daily calories for a given weight and program."""
    data = request.get_json(force=True)
    weight = float(data.get("weight", 0))
    program = data.get("program", "")

    if weight <= 0:
        return jsonify({"error": "weight must be > 0"}), 400
    if program not in PROGRAMS:
        return jsonify({"error": f"Unknown program: {program}"}), 400

    return jsonify({"weight_kg": weight, "program": program,
                    "estimated_calories": calculate_calories(weight, program)})


@app.route("/bmi", methods=["POST"])
def bmi():
    """Calculate BMI and return risk category."""
    data = request.get_json(force=True)
    try:
        weight = float(data["weight"])
        height = float(data["height"])
        bmi_value = calculate_bmi(weight, height)
    except (KeyError, TypeError, ValueError) as exc:
        return jsonify({"error": str(exc)}), 400

    if bmi_value < 18.5:
        category, risk = "Underweight", "Potential nutrient deficiency."
    elif bmi_value < 25:
        category, risk = "Normal", "Low risk if active and strong."
    elif bmi_value < 30:
        category, risk = "Overweight", "Moderate risk; focus on adherence."
    else:
        category, risk = "Obese", "Higher risk; prioritize fat loss."

    return jsonify({"bmi": bmi_value, "category": category, "risk_note": risk})


# ── Entry point ────────────────────────────────────────────────────────────────
if __name__ == "__main__":
    app.run(host="0.0.0.0", port=5000, debug=False)
