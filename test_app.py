# test_app.py
import pytest
import os
from ACEest_Fitness import app, DB_NAME, init_db

@pytest.fixture
def client():
    app.config['TESTING'] = True
    # Reset DB for a clean testing environment
    if os.path.exists(DB_NAME):
        os.remove(DB_NAME)
    init_db()
    with app.test_client() as client:
        yield client

def test_health_check(client):
    response = client.get('/')
    assert response.status_code == 200
    assert response.get_json()["version"] == "3.2.4"

def test_login_success(client):
    response = client.post('/api/login', json={"username": "admin", "password": "admin"})
    assert response.status_code == 200
    assert response.get_json()["role"] == "Admin"

def test_client_membership_creation(client):
    # 1. Add a new client
    payload = {"name": "Test User", "program": "Beginner (BG)", "weight": 75}
    client.post('/api/clients', json=payload)
    
    # 2. Check that the default 30-day membership was automatically applied
    response = client.get('/api/clients/Test User/membership')
    assert response.status_code == 200
    
    data = response.get_json()
    assert data["status"] == "Active"
    assert "renewal_date" in data