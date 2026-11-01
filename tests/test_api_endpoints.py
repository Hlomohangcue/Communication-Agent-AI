from types import SimpleNamespace

import pytest

fastapi = pytest.importorskip("fastapi")
pytest.importorskip("cv2")
from fastapi.testclient import TestClient

from backend.main import app, get_current_user, vision_service
from backend.services.gesture_dataset import GestureDatasetService
from backend.services.vision_service import VisionService


client = TestClient(app)

def test_root_redirects_to_ui():
    response = client.get("/", follow_redirects=False)
    assert response.status_code in (302, 307)
    assert response.headers["location"] == "/ui"


def test_health_endpoint():
    response = client.get("/health")
    assert response.status_code == 200
    body = response.json()
    assert body["status"] == "healthy"
    assert "version" in body


def test_verify_requires_authentication():
    response = client.get("/auth/verify")
    assert response.status_code == 401


def test_logs_requires_authentication():
    response = client.get("/logs")
    assert response.status_code == 401


@pytest.mark.parametrize("frame_data", ["", "not-base64", "data:image/jpeg;base64,"])
def test_invalid_frame_data_returns_error_not_zero_hand_result(frame_data):
    service = VisionService.__new__(VisionService)
    service.mediapipe_available = True

    result = service.process_frame(frame_data)

    assert "error" in result
    assert "hands_detected" not in result
    assert "gestures" not in result


def test_base64_that_is_not_an_image_returns_error_not_zero_hand_result():
    service = VisionService.__new__(VisionService)
    service.mediapipe_available = True

    result = service.process_frame("bm90IGFuIGltYWdl")

    assert "error" in result
    assert "valid image" in result["error"]
    assert "hands_detected" not in result
    assert "gestures" not in result


def test_interpret_gesture_returns_details_for_each_detected_hand(monkeypatch):
    monkeypatch.setitem(
        app.dependency_overrides,
        get_current_user,
        lambda: {"id": 1},
    )
    response = client.post(
        "/vision/interpret-gesture",
        json={
            "gestures": [
                {"gesture": "wave", "hand": "Left", "confidence": 0.91},
                {"gesture": "wave", "hand": "Right", "confidence": 0.87},
            ]
        },
    )

    assert response.status_code == 200
    details = response.json()["interpretation"]["gesture_details"]
    assert [detail["hand"] for detail in details] == ["Left", "Right"]
    assert [detail["gesture"] for detail in details] == ["wave", "wave"]
    assert [detail["confidence"] for detail in details] == [0.91, 0.87]
    assert all(detail["suggested_response"] for detail in details)


def test_gesture_collection_config_requires_authentication():
    response = client.get("/vision/collection-config")

    assert response.status_code == 401


def test_gesture_collection_requires_an_allowlisted_collector(monkeypatch):
    monkeypatch.setitem(
        app.dependency_overrides,
        get_current_user,
        lambda: {"id": "user-1"},
    )
    monkeypatch.setattr(
        "backend.main.settings",
        SimpleNamespace(gesture_dataset_collector_ids=["user-2"]),
    )

    response = client.get("/vision/collection-config")

    assert response.status_code == 403


def test_collect_frame_uses_landmark_extraction_without_classifier(monkeypatch):
    monkeypatch.setitem(
        app.dependency_overrides,
        get_current_user,
        lambda: {"id": "1"},
    )
    monkeypatch.setattr(
        "backend.main.settings",
        SimpleNamespace(gesture_dataset_collector_ids=["1"]),
    )
    expected = {
        "hands_detected": 1,
        "observations": [{
            "hand_side": "Left",
            "handedness_confidence": 0.94,
            "timestamp": "2026-10-30T12:00:00+00:00",
            "timestamp_ms": 1500.0,
            "landmarks": [{"x": 0.1, "y": 0.2, "z": 0.3}] * 21,
        }],
    }
    monkeypatch.setattr(
        vision_service,
        "extract_hand_landmarks",
        lambda frame, timestamp_ms: expected,
    )

    response = client.post(
        "/vision/collect-frame",
        json={"frame": "data:image/jpeg;base64,abc", "frame_timestamp_ms": 1500},
    )

    assert response.status_code == 200
    observation = response.json()["observations"][0]
    assert len(observation["landmarks"]) == 21
    assert observation["handedness_confidence"] == 0.94
    assert observation["timestamp_ms"] == 1500
    assert "gesture" not in observation


def test_save_gesture_dataset_recording_endpoint(monkeypatch, tmp_path):
    monkeypatch.setitem(
        app.dependency_overrides,
        get_current_user,
        lambda: {"id": "1"},
    )
    monkeypatch.setattr(
        "backend.main.settings",
        SimpleNamespace(gesture_dataset_collector_ids=["1"]),
    )
    dataset = GestureDatasetService(tmp_path / "dataset.jsonl")
    monkeypatch.setattr("backend.main.gesture_dataset_service", dataset)
    points = [{"x": 0.1, "y": 0.2, "z": 0.3} for _ in range(21)]
    record = {
        "dataset_version": 1,
        "sample_id": "api-sample-1",
        "participant_id": "participant-1",
        "recording_session_id": "session-1",
        "gesture_label": "open_palm",
        "hand_side": "Right",
        "timestamp": "2026-10-30T12:00:00.000Z",
        "landmarks": points,
        "handedness_confidence": 0.92,
        "feature_version": "mediapipe_hand_landmarks_xyz_v1",
        "sample_type": "static",
    }

    response = client.post(
        "/vision/dataset/recordings",
        json={"records": [record]},
    )

    assert response.status_code == 200
    assert response.json()["saved_count"] == 1
    assert len(dataset.read_records()) == 1
