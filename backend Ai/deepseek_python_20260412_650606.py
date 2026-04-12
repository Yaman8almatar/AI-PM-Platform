import pytest
from fastapi.testclient import TestClient
from app.main import app

client = TestClient(app)

def test_health_check():
    response = client.get("/health")
    assert response.status_code == 200
    assert response.json()["status"] == "alive"

def test_generate_plan_success():
    response = client.post("/api/generate-plan", json={"text": "مشروع إدارة المؤتمرات"})
    assert response.status_code == 200
    data = response.json()
    assert data["status"] == "success"
    assert "plan_id" in data
    assert "plan" in data

def test_generate_plan_empty_text():
    response = client.post("/api/generate-plan", json={"text": "   "})
    assert response.status_code == 400
    assert "فارغاً" in response.text

def test_generate_plan_missing_text():
    response = client.post("/api/generate-plan", json={})
    assert response.status_code == 422