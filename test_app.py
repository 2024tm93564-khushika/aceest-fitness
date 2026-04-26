# test_app.py
import pytest
import os
from ACEest_Fitness import app, DB_NAME, init_db

@pytest.fixture
def client():
    app.config['TESTING'] = True
    # Reset DB for clean testing environment
    if os.path.exists(DB_NAME):
        os.remove(DB_NAME)
    init_db()
    with app.test_client() as client:
        yield client

def test_health_check(client):
    response = client.get('/')
    assert response.status_code == 200
    assert response.get_json()["version"] == "2.0.1"

def test_add_client_to_db(client):
    payload = {"name": "DB Test User", "program": "Beginner (BG)", "weight": 70}
    response = client.post('/api/clients', json=payload)
    assert response.status_code == 201
    assert "saved to database" in response.get_json()["message"]

def test_get_clients_from_db(client):
    payload = {"name": "DB Test User", "program": "Beginner (BG)", "weight": 70}
    client.post('/api/clients', json=payload)
    response = client.get('/api/clients')
    assert response.status_code == 200
    assert len(response.get_json()["clients"]) > 0