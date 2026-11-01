from types import SimpleNamespace

import numpy as np

from backend.services.vision_service import VisionService


def fake_hand_landmarks(count=21):
    return [
        SimpleNamespace(x=index / 100, y=index / 200, z=-index / 300)
        for index in range(count)
    ]


def test_gesture_heuristics_read_mediapipe_tasks_landmark_lists():
    landmarks = fake_hand_landmarks()
    landmarks[4] = SimpleNamespace(x=0.4, y=0.5, z=0.0)
    landmarks[3] = SimpleNamespace(x=0.4, y=0.5, z=0.0)
    landmarks[8] = SimpleNamespace(x=0.5, y=0.2, z=0.0)
    landmarks[6] = SimpleNamespace(x=0.5, y=0.4, z=0.0)
    landmarks[12] = SimpleNamespace(x=0.6, y=0.2, z=0.0)
    landmarks[10] = SimpleNamespace(x=0.6, y=0.4, z=0.0)
    landmarks[16] = SimpleNamespace(x=0.7, y=0.6, z=0.0)
    landmarks[14] = SimpleNamespace(x=0.7, y=0.4, z=0.0)
    landmarks[20] = SimpleNamespace(x=0.8, y=0.6, z=0.0)
    landmarks[18] = SimpleNamespace(x=0.8, y=0.4, z=0.0)

    service = VisionService.__new__(VisionService)

    assert service._recognize_gesture(landmarks, "Right") == "peace"


def test_landmark_extraction_serializes_all_coordinates_without_gesture_labels(monkeypatch):
    service = VisionService.__new__(VisionService)
    service.mediapipe_available = True
    service._detect_hands = lambda image: SimpleNamespace(
        hand_landmarks=[fake_hand_landmarks()],
        handedness=[[SimpleNamespace(category_name="Right", score=0.96)]],
    )
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
    service._detect_hands = lambda image: SimpleNamespace(
        hand_landmarks=[fake_hand_landmarks(count=20)],
        handedness=[[SimpleNamespace(category_name="Left", score=0.9)]],
    )
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
    service._detect_hands = lambda image: SimpleNamespace(
        hand_landmarks=[fake_hand_landmarks(), fake_hand_landmarks()],
        handedness=[
            [SimpleNamespace(category_name="Left", score=0.9)],
            [SimpleNamespace(category_name="Right", score=0.8)],
        ],
    )
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


def test_tasks_landmarks_flow_through_gesture_interpretation(monkeypatch):
    service = VisionService.__new__(VisionService)
    service.mediapipe_available = True
    service.gesture_to_emoji = {"open_palm": "🖐️"}
    service.dynamic_gesture_tracker = None
    service._detect_hands = lambda image: SimpleNamespace(
        hand_landmarks=[fake_hand_landmarks()],
        handedness=[[SimpleNamespace(category_name="Right", score=0.96)]],
    )
    monkeypatch.setattr(
        service,
        "_decode_image",
        lambda frame: np.zeros((8, 8, 3), dtype=np.uint8),
    )
    monkeypatch.setattr(service, "_recognize_gesture", lambda *_args: "open_palm")

    result = service.process_frame("frame")

    assert result["hands_detected"] == 1
    assert result["gestures"] == [{
        "gesture": "open_palm",
        "hand": "Right",
        "confidence": 0.96,
        "movement_direction": "unavailable",
        "movement_displacement": 0.0,
        "movement_velocity": 0.0,
        "wrist_movement_direction": "unavailable",
        "wrist_movement_displacement": 0.0,
        "wrist_movement_velocity": 0.0,
        "dynamic_gesture_confidence": 0.0,
    }]
    assert result["emojis"] == ["🖐️"]
