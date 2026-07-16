import uuid
import importlib.util
import sys
import types

import pytest

fastapi = pytest.importorskip("fastapi")

if importlib.util.find_spec("cv2") is None:
    sys.modules.setdefault("cv2", types.ModuleType("cv2"))

from fastapi.testclient import TestClient

from backend import main as main_module
from backend.coordinator.orchestrator import Coordinator
from backend.database.db import Database
from backend.simulation.classroom_sim import ClassroomSimulation


def _auth_headers(token: str) -> dict:
    return {"Authorization": f"Bearer {token}"}


def _signup_and_login(client: TestClient, email: str, name: str) -> tuple[str, str]:
    signup_response = client.post(
        "/auth/signup",
        json={"name": name, "email": email, "password": "Password123"},
    )
    assert signup_response.status_code == 200
    user_id = signup_response.json()["user"]["id"]

    login_response = client.post(
        "/auth/login",
        json={"email": email, "password": "Password123"},
    )
    assert login_response.status_code == 200
    token = login_response.json()["token"]
    return token, user_id


@pytest.fixture
def client_and_db(tmp_path):
    test_db = Database(str(tmp_path / "session_ownership.db"))
    test_db.init_gesture_tables()

    original_db = main_module.db
    original_coordinator = main_module.coordinator
    original_simulation = main_module.simulation

    main_module.db = test_db
    main_module.coordinator = Coordinator(test_db)
    main_module.simulation = ClassroomSimulation(main_module.coordinator, test_db)

    client = TestClient(main_module.app)

    try:
        yield client, test_db
    finally:
        client.close()
        main_module.db = original_db
        main_module.coordinator = original_coordinator
        main_module.simulation = original_simulation


def test_session_creation_stores_correct_user_id(client_and_db):
    client, db = client_and_db
    owner_token, owner_user_id = _signup_and_login(client, "owner1@example.com", "Owner One")

    start_response = client.post("/simulate/start", headers=_auth_headers(owner_token))
    assert start_response.status_code == 200

    session_id = start_response.json()["session_id"]
    session = db.get_session_by_id(session_id)

    assert session is not None
    assert session["user_id"] == owner_user_id


def test_owner_can_read_update_history_and_delete_session(client_and_db):
    client, _ = client_and_db
    owner_token, _ = _signup_and_login(client, "owner2@example.com", "Owner Two")

    start_response = client.post("/simulate/start", headers=_auth_headers(owner_token))
    assert start_response.status_code == 200
    session_id = start_response.json()["session_id"]

    read_response = client.get(f"/session/{session_id}", headers=_auth_headers(owner_token))
    assert read_response.status_code == 200

    update_response = client.post(
        "/save_message",
        headers=_auth_headers(owner_token),
        json={
            "session_id": session_id,
            "input_text": "Hi",
            "output_text": "Hello",
            "intent": "manual_save",
            "confidence": 1.0,
        },
    )
    assert update_response.status_code == 200

    translate_response = client.post(
        "/translate/text-to-gesture",
        headers=_auth_headers(owner_token),
        json={"text": "hello", "session_id": session_id},
    )
    assert translate_response.status_code == 200

    history_response = client.get(
        f"/gesture-history/{session_id}",
        headers=_auth_headers(owner_token),
    )
    assert history_response.status_code == 200
    assert len(history_response.json()["history"]) >= 1

    delete_response = client.delete(f"/session/{session_id}", headers=_auth_headers(owner_token))
    assert delete_response.status_code == 200

    deleted_read_response = client.get(f"/session/{session_id}", headers=_auth_headers(owner_token))
    assert deleted_read_response.status_code == 404


def test_different_authenticated_user_gets_403(client_and_db):
    client, _ = client_and_db
    owner_token, _ = _signup_and_login(client, "owner3@example.com", "Owner Three")
    attacker_token, _ = _signup_and_login(client, "attacker@example.com", "Attacker")

    start_response = client.post("/simulate/start", headers=_auth_headers(owner_token))
    assert start_response.status_code == 200
    session_id = start_response.json()["session_id"]

    assert client.get(f"/session/{session_id}", headers=_auth_headers(attacker_token)).status_code == 403

    assert client.post(
        "/save_message",
        headers=_auth_headers(attacker_token),
        json={
            "session_id": session_id,
            "input_text": "attack",
            "output_text": "attack",
            "intent": "manual_save",
            "confidence": 1.0,
        },
    ).status_code == 403

    assert client.get(
        f"/gesture-history/{session_id}",
        headers=_auth_headers(attacker_token),
    ).status_code == 403

    assert client.delete(f"/session/{session_id}", headers=_auth_headers(attacker_token)).status_code == 403


def test_anonymous_user_gets_401(client_and_db):
    client, _ = client_and_db
    owner_token, _ = _signup_and_login(client, "owner4@example.com", "Owner Four")

    start_response = client.post("/simulate/start", headers=_auth_headers(owner_token))
    assert start_response.status_code == 200
    session_id = start_response.json()["session_id"]

    response = client.get(f"/session/{session_id}")
    assert response.status_code == 401

    delete_response = client.delete(f"/session/{session_id}")
    assert delete_response.status_code == 401

    save_response = client.post(
        "/save_message",
        json={
            "session_id": session_id,
            "input_text": "anon",
            "output_text": "anon",
            "intent": "manual_save",
            "confidence": 1.0,
        },
    )
    assert save_response.status_code == 401

    history_response = client.get(f"/gesture-history/{session_id}")
    assert history_response.status_code == 401


def test_invalid_session_returns_404(client_and_db):
    client, _ = client_and_db
    owner_token, _ = _signup_and_login(client, "owner5@example.com", "Owner Five")
    invalid_session_id = str(uuid.uuid4())

    read_response = client.get(f"/session/{invalid_session_id}", headers=_auth_headers(owner_token))
    assert read_response.status_code == 404

    delete_response = client.delete(f"/session/{invalid_session_id}", headers=_auth_headers(owner_token))
    assert delete_response.status_code == 404
