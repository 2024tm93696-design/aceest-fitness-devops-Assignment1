"""
ACEest Fitness & Gym - Pytest Test Suite
Tests all Flask API endpoints and core business logic.
"""

import pytest
from app import app, calculate_calories, calculate_bmi, PROGRAMS


# ── Fixtures ───────────────────────────────────────────────────────────────────
@pytest.fixture
def client():
    """Provide a Flask test client with a clean client store."""
    app.config["TESTING"] = True
    with app.test_client() as c:
        # Reset in-memory store before each test
        from app import clients
        clients.clear()
        yield c


# ── Helper / logic tests ───────────────────────────────────────────────────────
class TestBusinessLogic:

    def test_calculate_calories_fat_loss(self):
        result = calculate_calories(70.0, "Fat Loss (FL)")
        assert result == 1540  # 70 * 22

    def test_calculate_calories_muscle_gain(self):
        result = calculate_calories(80.0, "Muscle Gain (MG)")
        assert result == 2800  # 80 * 35

    def test_calculate_calories_beginner(self):
        result = calculate_calories(60.0, "Beginner (BG)")
        assert result == 1560  # 60 * 26

    def test_calculate_calories_unknown_program(self):
        result = calculate_calories(70.0, "Unknown Program")
        assert result == 0  # factor defaults to 0

    def test_calculate_bmi_normal(self):
        bmi = calculate_bmi(70.0, 175.0)
        assert bmi == 22.9

    def test_calculate_bmi_overweight(self):
        bmi = calculate_bmi(90.0, 170.0)
        assert bmi == 31.1

    def test_calculate_bmi_zero_height_raises(self):
        with pytest.raises(ValueError):
            calculate_bmi(70.0, 0)

    def test_programs_have_required_keys(self):
        for name, details in PROGRAMS.items():
            assert "workout" in details, f"{name} missing 'workout'"
            assert "diet" in details, f"{name} missing 'diet'"
            assert "calorie_factor" in details, f"{name} missing 'calorie_factor'"


# ── Index / Health routes ──────────────────────────────────────────────────────
class TestIndexHealth:

    def test_index_returns_200(self, client):
        resp = client.get("/")
        assert resp.status_code == 200

    def test_index_message(self, client):
        data = resp = client.get("/").get_json()
        assert "ACEest" in data["message"]
        assert data["status"] == "running"

    def test_health_endpoint(self, client):
        resp = client.get("/health")
        assert resp.status_code == 200
        assert resp.get_json()["status"] == "healthy"


# ── Programs routes ────────────────────────────────────────────────────────────
class TestPrograms:

    def test_get_programs_returns_list(self, client):
        resp = client.get("/programs")
        assert resp.status_code == 200
        data = resp.get_json()
        assert "programs" in data
        assert len(data["programs"]) == 3

    def test_get_programs_contains_fat_loss(self, client):
        data = client.get("/programs").get_json()
        assert "Fat Loss (FL)" in data["programs"]

    def test_get_single_program_ok(self, client):
        resp = client.get("/programs/Fat Loss (FL)")
        assert resp.status_code == 200
        data = resp.get_json()
        assert data["program"] == "Fat Loss (FL)"
        assert "workout" in data["details"]
        assert "diet" in data["details"]

    def test_get_unknown_program_404(self, client):
        resp = client.get("/programs/Nonexistent")
        assert resp.status_code == 404
        assert "error" in resp.get_json()


# ── Clients CRUD ───────────────────────────────────────────────────────────────
class TestClients:

    def _create(self, client, payload):
        return client.post("/clients", json=payload)

    def test_create_client_success(self, client):
        resp = self._create(client, {"name": "Arjun", "program": "Fat Loss (FL)",
                                     "weight": 75.0, "age": 28, "adherence": 80})
        assert resp.status_code == 201
        data = resp.get_json()
        assert "Arjun" in data["message"]

    def test_create_client_calories_calculated(self, client):
        resp = self._create(client, {"name": "Priya", "program": "Muscle Gain (MG)",
                                     "weight": 60.0, "age": 25})
        assert resp.get_json()["client"]["calories"] == 2100  # 60*35

    def test_create_client_missing_name_400(self, client):
        resp = self._create(client, {"program": "Fat Loss (FL)"})
        assert resp.status_code == 400

    def test_create_client_unknown_program_400(self, client):
        resp = self._create(client, {"name": "Test", "program": "Ghost Program"})
        assert resp.status_code == 400

    def test_list_clients_empty(self, client):
        resp = client.get("/clients")
        assert resp.status_code == 200
        assert resp.get_json()["clients"] == []

    def test_list_clients_after_create(self, client):
        self._create(client, {"name": "Karthik", "program": "Beginner (BG)", "weight": 70})
        data = client.get("/clients").get_json()
        assert "Karthik" in data["clients"]

    def test_get_client_not_found_404(self, client):
        resp = client.get("/clients/NoOne")
        assert resp.status_code == 404

    def test_get_client_found(self, client):
        self._create(client, {"name": "Meena", "program": "Fat Loss (FL)", "weight": 55.0})
        resp = client.get("/clients/Meena")
        assert resp.status_code == 200
        assert resp.get_json()["name"] == "Meena"

    def test_delete_client(self, client):
        self._create(client, {"name": "Raj", "program": "Beginner (BG)", "weight": 65.0})
        resp = client.delete("/clients/Raj")
        assert resp.status_code == 200
        assert client.get("/clients/Raj").status_code == 404

    def test_delete_nonexistent_client_404(self, client):
        resp = client.delete("/clients/Ghost")
        assert resp.status_code == 404


# ── Calories endpoint ──────────────────────────────────────────────────────────
class TestCaloriesEndpoint:

    def test_calories_valid(self, client):
        resp = client.post("/calories", json={"weight": 70, "program": "Fat Loss (FL)"})
        assert resp.status_code == 200
        assert resp.get_json()["estimated_calories"] == 1540

    def test_calories_zero_weight_400(self, client):
        resp = client.post("/calories", json={"weight": 0, "program": "Fat Loss (FL)"})
        assert resp.status_code == 400

    def test_calories_unknown_program_400(self, client):
        resp = client.post("/calories", json={"weight": 70, "program": "X"})
        assert resp.status_code == 400


# ── BMI endpoint ───────────────────────────────────────────────────────────────
class TestBMIEndpoint:

    def test_bmi_normal_category(self, client):
        resp = client.post("/bmi", json={"weight": 70, "height": 175})
        assert resp.status_code == 200
        data = resp.get_json()
        assert data["category"] == "Normal"
        assert data["bmi"] == 22.9

    def test_bmi_underweight(self, client):
        resp = client.post("/bmi", json={"weight": 45, "height": 170})
        assert resp.get_json()["category"] == "Underweight"

    def test_bmi_overweight(self, client):
        resp = client.post("/bmi", json={"weight": 85, "height": 169})
        assert resp.get_json()["category"] == "Overweight"

    def test_bmi_obese(self, client):
        resp = client.post("/bmi", json={"weight": 110, "height": 170})
        assert resp.get_json()["category"] == "Obese"

    def test_bmi_missing_fields_400(self, client):
        resp = client.post("/bmi", json={"weight": 70})
        assert resp.status_code == 400
