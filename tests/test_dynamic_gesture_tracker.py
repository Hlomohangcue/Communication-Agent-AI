from types import SimpleNamespace
import pytest

from backend.services.dynamic_gesture_tracker import DynamicGestureTracker


def hand(center_x, side="Left", static_gesture="open_palm"):
    landmarks = [SimpleNamespace(x=center_x, y=0.5, z=0.0) for _ in range(21)]
    landmarks[0] = SimpleNamespace(x=center_x, y=0.8, z=0.0)
    landmarks[5] = SimpleNamespace(x=center_x - 0.1, y=0.5, z=0.0)
    landmarks[9] = SimpleNamespace(x=center_x - 0.03, y=0.48, z=0.0)
    landmarks[13] = SimpleNamespace(x=center_x + 0.03, y=0.48, z=0.0)
    landmarks[17] = SimpleNamespace(x=center_x + 0.1, y=0.5, z=0.0)
    return {
        "hand": side,
        "landmarks": SimpleNamespace(landmark=landmarks),
        "static_gesture": static_gesture,
    }


def alternating_wave(tracker, stream="camera-a", side="Left", start_time=0):
    results = []
    for frame, x in enumerate((0.45, 0.58, 0.45, 0.58, 0.45)):
        result = tracker.update(stream, start_time + frame * 500, [hand(x, side)])
        results.append(result[side])
    return results


def test_direction_and_displacement_use_timestamped_landmark_positions():
    alternations, directions, displacement, velocity, direction = (
        DynamicGestureTracker._alternating_segments(
            [(1000, 0.4), (1500, 0.54)],
            0.2,
        )
    )

    assert alternations == 0
    assert directions == ("right",)
    assert displacement == pytest.approx(0.7)
    assert velocity == pytest.approx(1.4)
    assert direction == "right"


def test_wave_requires_repeated_alternating_horizontal_movement():
    tracker = DynamicGestureTracker()

    results = alternating_wave(tracker)

    assert [frame["dynamic_gesture"] for frame in results[:-1]] == [None] * 4
    assert results[-1]["dynamic_gesture"] == "wave"
    assert results[-1]["alternating_movements"] >= tracker.MIN_ALTERNATIONS
    assert results[-1]["dynamic_gesture_confidence"] >= tracker.MIN_DYNAMIC_CONFIDENCE


def test_single_direction_movement_does_not_count_as_wave():
    tracker = DynamicGestureTracker()
    result = {}

    for frame, x in enumerate((0.4, 0.48, 0.56, 0.64, 0.72)):
        result = tracker.update("camera-a", frame * 500, [hand(x)])

    assert result["Left"]["dynamic_gesture"] is None
    assert result["Left"]["movement_direction"] == "right"
    assert result["Left"]["alternating_movements"] == 0


def test_wave_threshold_rejects_small_or_slow_motion():
    tracker = DynamicGestureTracker()
    small_motion = {}
    for frame, x in enumerate((0.45, 0.48, 0.45, 0.48, 0.45)):
        small_motion = tracker.update("small", frame * 500, [hand(x)])
    assert small_motion["Left"]["dynamic_gesture"] is None

    slow_positions = (
        0.45, 0.48, 0.51, 0.54, 0.56,
        0.54, 0.51, 0.48, 0.45,
        0.48, 0.51, 0.54, 0.56,
        0.54, 0.51, 0.48, 0.45,
    )
    slow_motion = {}
    for frame, x in enumerate(slow_positions):
        slow_motion = tracker.update("slow", frame * 500, [hand(x)])
    assert slow_motion["Left"]["dynamic_gesture"] is None


def test_tracking_gap_resets_movement_history():
    tracker = DynamicGestureTracker()
    for frame, x in enumerate((0.45, 0.58, 0.45)):
        tracker.update("camera-a", frame * 500, [hand(x)])

    result = tracker.update("camera-a", 3000, [hand(0.58)])

    assert result["Left"]["dynamic_gesture"] is None
    assert result["Left"]["alternating_movements"] == 0


def test_camera_session_and_hand_side_keep_tracks_independent():
    tracker = DynamicGestureTracker()
    alternating_wave(tracker, stream="camera-a", side="Left")

    new_session = tracker.update("camera-b", 2500, [hand(0.45, side="Left")])
    other_side = tracker.update("camera-a", 2500, [hand(0.45, side="Right")])

    assert new_session["Left"]["dynamic_gesture"] is None
    assert other_side["Right"]["dynamic_gesture"] is None


def test_intermittent_tracking_loss_resets_samples_but_keeps_wave_latch():
    tracker = DynamicGestureTracker()
    results = alternating_wave(tracker)
    assert results[-1]["dynamic_gesture"] == "wave"

    tracker.update("camera-a", 2500, [])
    resumed = tracker.update("camera-a", 3000, [hand(0.45)])

    assert resumed["Left"]["dynamic_gesture"] == "wave"
    assert resumed["Left"]["alternating_movements"] == 0
    assert resumed["Left"]["wave_latched"] is True


def test_unreliable_tracking_resets_movement_history_without_releasing_wave_latch():
    tracker = DynamicGestureTracker()
    assert alternating_wave(tracker)[-1]["wave_latched"] is True

    tracker.reset_movement_history("camera-a")
    resumed = tracker.update("camera-a", 2500, [hand(0.45)])

    assert resumed["Left"]["dynamic_gesture"] == "wave"
    assert resumed["Left"]["alternating_movements"] == 0


def test_tracker_uses_wrist_and_palm_landmark_positions():
    tracker = DynamicGestureTracker()
    motion = tracker.update("camera-a", 0, [hand(0.45)])["Left"]
    assert motion["wrist_movement_direction"] == "stationary"
    assert motion["movement_direction"] == "stationary"

    motion = tracker.update("camera-a", 500, [hand(0.58)])["Left"]
    assert motion["wrist_movement_direction"] == "right"
    assert motion["movement_direction"] == "right"
    assert motion["wrist_movement_displacement"] > 0
    assert motion["movement_displacement"] > 0


def test_unreliable_handedness_does_not_assign_a_tracking_identity():
    tracker = DynamicGestureTracker()
    result = tracker.update("camera-a", 0, [hand(0.45, side=None)])

    assert result == {}
    assert tracker._streams["camera-a"] == {}


def test_duplicate_handedness_labels_are_not_treated_as_stable_hand_identity():
    tracker = DynamicGestureTracker()
    result = tracker.update(
        "camera-a",
        0,
        [hand(0.45, side="Left"), hand(0.58, side="Left")],
    )

    assert result == {}
    assert tracker._streams["camera-a"] == {}


def test_one_continuous_wave_episode_stays_latched():
    tracker = DynamicGestureTracker()
    results = alternating_wave(tracker)
    assert results[-1]["dynamic_gesture"] == "wave"

    subsequent = []
    for frame, x in enumerate((0.58, 0.45, 0.58, 0.45), start=5):
        subsequent.append(tracker.update("camera-a", frame * 500, [hand(x)])["Left"])

    assert all(result["dynamic_gesture"] == "wave" for result in subsequent)
    assert all(result["wave_latched"] for result in subsequent)


def test_non_open_hand_pose_ends_wave_episode():
    tracker = DynamicGestureTracker()
    alternating_wave(tracker)

    result = tracker.update("camera-a", 2500, [hand(0.45, static_gesture="fist")])

    assert result["Left"]["dynamic_gesture"] is None
    assert result["Left"]["wave_latched"] is False
