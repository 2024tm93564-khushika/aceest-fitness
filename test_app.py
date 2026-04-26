# test_app.py
import pytest
from ACEest_Fitness import app, clients

@pytest.fixture
def client():
    app.config['TESTING'] = True
    clients.clear() # Clear memory between tests
    with app.test_client() as client:
        yield client

def test_health_check(client):
    response = client.get('/')
    assert response.status_code == 200
    assert response.get_json()["version"] == "1.1.2"

def test_add_client(client):
    payload = {"name": "Test User", "program": "Beginner (BG)", "weight": 70}
    response = client.post('/api/clients', json=payload)
    assert response.status_code == 201
    assert "saved successfully" in response.get_json()["message"]

def test_export_csv(client):
    response = client.get('/api/export')
    assert response.status_code == 200
    assert "Exported" in response.get_json()["message"]