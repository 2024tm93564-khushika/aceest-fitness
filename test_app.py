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
    assert response.get_json()["version"] == "2.2.4"

def test_add_workout(client):
    payload = {"client_name": "Test User", "date": "2026-04-26", "workout_type": "Strength", "duration_min": 45}
    response = client.post('/api/workouts', json=payload)
    assert response.status_code == 201
    assert "Workout logged" in response.get_json()["message"]

def test_add_metrics(client):
    payload = {"client_name": "Test User", "date": "2026-04-26", "weight": 72.5, "waist": 80.0, "bodyfat": 15.5}
    response = client.post('/api/metrics', json=payload)
    assert response.status_code == 201
    assert "Metrics logged" in response.get_json()["message"]