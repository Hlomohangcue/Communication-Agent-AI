from types import SimpleNamespace

import numpy as np

from backend.services.vision_service import VisionService


def fake_hand_landmarks(count=21):
    points = [
        SimpleNamespace(x=index / 100, y=index / 200, z=-index / 300)
        for index in range(count)
    ]
    return SimpleNamespace(landmark=points)


def test_landmark_extraction_serializes_all_coordinates_without_gesture_labels(monkeypatch):
    service = VisionService.__new__(VisionService)
    service.mediapipe_available = True
    service.hands = SimpleNamespace(process=lambda image: SimpleNamespace(
        multi_hand_landmarks=[fake_hand_landmarks()],
        multi_handedness=[SimpleNamespace(classification=[
            SimpleNamespace(label="Right", score=0.96)
        ])],
    ))
    monkeypatch.setattr(
        service,
        "_decode_image",
        lambda frame: np.zeros((8, 8, 3), dtype=np.uint8),
    )
    service._recognize_gesture = lambda *_args: (_ for _ in ()).throw(
        AssertionError("collector must not call the heuristic classifier")
    )

    result = service.extract_hand_landmarks("frame", timestamp_ms=1234.5)

    assert result["hands_detected"] == 1
    observation = result["observations"][0]
    assert observation["hand_side"] == "Right"
    assert observation["handedness_confidence"] == 0.96
    assert observation["timestamp_ms"] == 1234.5
    assert len(observation["landmarks"]) == 21
    assert observation["landmarks"][4] == {
        "x": 0.04,
        "y": 0.02,
        "z": -4 / 300,
    }
    assert "gesture" not in observation


def test_landmark_extraction_reports_missing_landmark_metadata(monkeypatch):
    service = VisionService.__new__(VisionService)
    service.mediapipe_available = True
    service.hands = SimpleNamespace(process=lambda image: SimpleNamespace(
        multi_hand_landmarks=[fake_hand_landmarks(count=20)],
        multi_handedness=[SimpleNamespace(classification=[
            SimpleNamespace(label="Left", score=0.9)
        ])],
    ))
    monkeypatch.setattr(
        service,
        "_decode_image",
        lambda frame: np.zeros((8, 8, 3), dtype=np.uint8),
    )

    result = service.extract_hand_landmarks("frame", timestamp_ms=1000)

    assert result["error_type"] == "incomplete_detection"
    assert result["hands_detected"] == 0
    assert result["observations"] == []


def test_landmark_extraction_keeps_two_hands_as_distinct_observations(monkeypatch):
    service = VisionService.__new__(VisionService)
    service.mediapipe_available = True
    service.hands = SimpleNamespace(process=lambda image: SimpleNamespace(
        multi_hand_landmarks=[fake_hand_landmarks(), fake_hand_landmarks()],
        multi_handedness=[
            SimpleNamespace(classification=[SimpleNamespace(label="Left", score=0.9)]),
            SimpleNamespace(classification=[SimpleNamespace(label="Right", score=0.8)]),
        ],
    ))
    monkeypatch.setattr(
        service,
        "_decode_image",
        lambda frame: np.zeros((8, 8, 3), dtype=np.uint8),
    )

    result = service.extract_hand_landmarks("frame", timestamp_ms=2000)

    assert result["hands_detected"] == 2
    assert [hand["hand_side"] for hand in result["observations"]] == ["Left", "Right"]
    assert [hand["handedness_confidence"] for hand in result["observations"]] == [0.9, 0.8]
    assert result["observations"][0] is not result["observations"][1]
