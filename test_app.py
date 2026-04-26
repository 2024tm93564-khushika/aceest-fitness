# test_app.py
import pytest
from app import app

@pytest.fixture
def client():
    app.config['TESTING'] = True
    with app.test_client() as client:
        yield client

def test_health_check(client):
    response = client.get('/')
    assert response.status_code == 200
    assert response.get_json()["status"] == "healthy"
    assert response.get_json()["version"] == "1.0"

def test_get_programs(client):
    response = client.get('/api/programs')
    assert response.status_code == 200
    programs = response.get_json()["programs"]
    assert "Fat Loss (FL)" in programs
    assert "Beginner (BG)" in programs

def test_get_program_details_valid(client):
    response = client.get('/api/program/Muscle Gain (MG)')
    assert response.status_code == 200
    data = response.get_json()
    assert "calorie_factor" in data
    assert data["calorie_factor"] == 35

def test_get_program_details_invalid(client):
    response = client.get('/api/program/Invalid Program')
    assert response.status_code == 404

def test_calculate_calories(client):
    payload = {"weight": 70, "program": "Beginner (BG)"} # 70 * 26 = 1820
    response = client.post('/api/calculate_calories', json=payload)
    assert response.status_code == 200
    assert response.get_json()["estimated_calories"] == 1820