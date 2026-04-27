# test_app.py
import pytest
import os
from ACEest_Fitness import app, DB_NAME, init_db

@pytest.fixture
def client():
    app.config['TESTING'] = True
    if os.path.exists(DB_NAME):
        os.remove(DB_NAME)
    init_db()
    with app.test_client() as client:
        yield client

def test_health_check(client):
    response = client.get('/')
    assert response.status_code == 200
    assert response.get_json()["version"] == "3.0.1"

def test_bmi_calculator(client):
    # Add a client with height and weight
    payload = {"name": "Test User", "program": "Beginner (BG)", "height": 180, "weight": 80}
    client.post('/api/clients', json=payload)
    
    # Test BMI calculation (80 / 1.8^2 = 24.7)
    response = client.get('/api/clients/Test User/bmi')
    assert response.status_code == 200
    data = response.get_json()
    assert data["bmi"] == 24.7
    assert data["category"] == "Normal"

def test_weight_chart_generation(client):
    client.post('/api/metrics', json={"client_name": "Test User", "date": "2026-04-26", "weight": 80})
    response = client.get('/api/metrics/Test User/chart')
    assert response.status_code == 200
    assert "chart_image" in response.get_json()