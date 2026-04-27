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
    assert response.get_json()["version"] == "3.1.2"

def test_login_success(client):
    response = client.post('/api/login', json={"username": "admin", "password": "admin"})
    assert response.status_code == 200
    assert response.get_json()["role"] == "Admin"

def test_login_fail(client):
    response = client.post('/api/login', json={"username": "admin", "password": "wrong"})
    assert response.status_code == 401

def test_ai_program_generator(client):
    # Create client
    client.post('/api/clients', json={"name": "Test User", "program": "Beginner (BG)"})
    # Generate program
    response = client.post('/api/clients/Test User/generate_program', json={"experience": "beginner"})
    assert response.status_code == 200
    data = response.get_json()
    assert "schedule" in data
    assert len(data["schedule"]) > 0

def test_pdf_report_generation(client):
    client.post('/api/clients', json={"name": "Test User", "program": "Beginner (BG)", "weight": 70})
    response = client.get('/api/clients/Test User/report')
    assert response.status_code == 200
    assert response.headers["Content-Type"] == "application/pdf"