import pytest

fastapi = pytest.importorskip("fastapi")
pytest.importorskip("cv2")
from fastapi.testclient import TestClient

from backend.main import app


client = TestClient(app)


def test_root_health_endpoint():
    response = client.get("/")
    assert response.status_code == 200
    body = response.json()
    assert "status" in body
    assert "version" in body


def test_verify_requires_authentication():
    response = client.get("/auth/verify")
    assert response.status_code == 401


def test_logs_requires_authentication():
    response = client.get("/logs")
    assert response.status_code == 401
