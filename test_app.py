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
    assert response.get_json()["version"] == "2.1.2"

def test_add_client_to_db(client):
    payload = {"name": "DB Test User", "program": "Beginner (BG)", "weight": 70}
    response = client.post('/api/clients', json=payload)
    assert response.status_code == 201

def test_add_and_get_progress(client):
    # First, save progress
    payload = {"client_name": "Test User", "adherence": 85}
    response_post = client.post('/api/progress', json=payload)
    assert response_post.status_code == 201
    assert "logged" in response_post.get_json()["message"]

    # Then, retrieve it
    response_get = client.get('/api/progress/Test User')
    assert response_get.status_code == 200
    data = response_get.get_json()
    assert len(data["progress"]) == 1
    assert data["progress"][0]["adherence"] == 85