# test_app.py
import pytest
from ACEest_Fitness import app

@pytest.fixture
def client():
    app.config['TESTING'] = True
    with app.test_client() as client:
        yield client

def test_health_check(client):
    response = client.get('/')
    assert response.status_code == 200
    assert response.get_json()["status"] == "healthy"
    assert response.get_json()["version"] == "1.1"

def test_preview_client_valid(client):
    payload = {"name": "John Doe", "weight": 70, "program": "Beginner (BG)", "adherence": 90}
    response = client.post('/api/client/preview', json=payload)
    assert response.status_code == 200
    data = response.get_json()
    assert data["estimated_calories"] == 1820  # 70 kg * 26 factor

def test_preview_client_invalid_program(client):
    payload = {"name": "John Doe", "weight": 70, "program": "Nonexistent Program"}
    response = client.post('/api/client/preview', json=payload)
    assert response.status_code == 400
    assert response.get_json()["error"] == "Invalid Program"

def test_preview_client_missing_data(client):
    payload = {"name": "John Doe"}  # Missing 'program'
    response = client.post('/api/client/preview', json=payload)
    assert response.status_code == 400
    assert response.get_json()["error"] == "Missing client data"