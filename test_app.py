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
    assert response.get_json()["version"] == "2.2.1"

def test_add_client_to_db(client):
    payload = {"name": "Test User", "program": "Beginner (BG)", "weight": 70}
    assert client.post('/api/clients', json=payload).status_code == 201

def test_generate_chart(client):
    # Log progress first
    client.post('/api/progress', json={"client_name": "Test User", "adherence": 85})
    # Fetch chart
    response = client.get('/api/progress/Test User/chart')
    assert response.status_code == 200
    assert "chart_image" in response.get_json()