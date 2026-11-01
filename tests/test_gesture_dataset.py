import json
import sys

import pytest

from scripts.export_gesture_dataset import main as export_dataset
from backend.services.gesture_dataset import (
    DATASET_VERSION,
    FEATURE_VERSION,
    DatasetValidationError,
    GestureDatasetService,
    split_records_by_participant,
)


def points(value=0.25):
    return [{"x": value, "y": value + 0.1, "z": -value} for _ in range(21)]


def static_record(sample_id="sample-1", participant_id="participant-1", session_id="session-1"):
    return {
        "dataset_version": DATASET_VERSION,
        "sample_id": sample_id,
        "participant_id": participant_id,
        "recording_session_id": session_id,
        "gesture_label": "open_palm",
        "hand_side": "Left",
        "timestamp": "2026-10-30T12:00:00.000Z",
        "landmarks": points(),
        "handedness_confidence": 0.93,
        "feature_version": FEATURE_VERSION,
        "sample_type": "static",
    }


def dynamic_record(sample_id="wave-1", participant_id="participant-1", session_id="session-1"):
    observations = []
    for index in range(5):
        observations.append({
            "timestamp": f"2026-10-30T12:00:0{index}.000Z",
            "timestamp_ms": 1000 + index * 200,
            "handedness_confidence": 0.91,
            "landmarks": points(index / 10),
        })
    return {
        "dataset_version": DATASET_VERSION,
        "sample_id": sample_id,
        "participant_id": participant_id,
        "recording_session_id": session_id,
        "gesture_label": "wave",
        "hand_side": "Right",
        "timestamp": observations[0]["timestamp"],
        "landmarks": observations,
        "feature_version": FEATURE_VERSION,
        "sample_type": "dynamic",
    }


def test_static_sample_serialization_and_session_metadata(tmp_path):
    dataset = GestureDatasetService(tmp_path / "dataset.jsonl")
    record = static_record(participant_id="pseudonym-02", session_id="recording-b")

    assert dataset.save_records([record]) == 1

    saved_line = (tmp_path / "dataset.jsonl").read_text(encoding="utf-8").splitlines()[0]
    saved = json.loads(saved_line)
    assert saved["sample_id"] == "sample-1"
    assert saved["participant_id"] == "pseudonym-02"
    assert saved["recording_session_id"] == "recording-b"
    assert saved["hand_side"] == "Left"
    assert saved["gesture_label"] == "open_palm"
    assert saved["handedness_confidence"] == pytest.approx(0.93)
    assert saved["feature_version"] == FEATURE_VERSION
    assert len(saved["landmarks"]) == 21
    assert saved["landmarks"][0] == {"x": 0.25, "y": 0.35, "z": -0.25}
    assert dataset.read_records() == [saved]


def test_dynamic_record_serializes_timestamped_observation_sequence(tmp_path):
    dataset = GestureDatasetService(tmp_path / "dataset.jsonl")
    record = dynamic_record()

    assert dataset.save_records([record]) == 1

    saved = dataset.read_records()[0]
    assert saved["sample_type"] == "dynamic"
    assert len(saved["landmarks"]) == 5
    assert [item["timestamp_ms"] for item in saved["landmarks"]] == [
        1000, 1200, 1400, 1600, 1800
    ]
    assert all(len(item["landmarks"]) == 21 for item in saved["landmarks"])
    assert all(0 <= item["handedness_confidence"] <= 1 for item in saved["landmarks"])


@pytest.mark.parametrize(
    ("mutate", "message"),
    [
        (lambda record: record.update(participant_id=""), "participant_id"),
        (lambda record: record.update(gesture_label="invented_label"), "Invalid gesture label"),
        (lambda record: record.pop("landmarks"), "exactly 21"),
        (lambda record: record["landmarks"][0].update(x=float("nan")), "finite number"),
        (lambda record: record.update(handedness_confidence=1.5), "handedness_confidence"),
    ],
)
def test_invalid_static_records_are_rejected(tmp_path, mutate, message):
    record = static_record()
    mutate(record)

    with pytest.raises(DatasetValidationError, match=message):
        GestureDatasetService(tmp_path / "dataset.jsonl").save_records([record])


def test_dynamic_record_rejects_incomplete_or_unordered_sequences(tmp_path):
    dataset = GestureDatasetService(tmp_path / "dataset.jsonl")
    incomplete = dynamic_record()
    incomplete["landmarks"] = incomplete["landmarks"][:4]

    with pytest.raises(DatasetValidationError, match="at least 5 observations"):
        dataset.save_records([incomplete])

    unordered = dynamic_record(sample_id="wave-2")
    unordered["landmarks"][2]["timestamp_ms"] = unordered["landmarks"][1]["timestamp_ms"]
    with pytest.raises(DatasetValidationError, match="strictly increasing"):
        dataset.save_records([unordered])


def test_duplicate_sample_ids_are_rejected_within_and_across_saves(tmp_path):
    dataset = GestureDatasetService(tmp_path / "dataset.jsonl")
    with pytest.raises(DatasetValidationError, match="Duplicate sample_id"):
        dataset.save_records([static_record(), static_record()])

    dataset.save_records([static_record()])
    with pytest.raises(DatasetValidationError, match="Duplicate sample_id"):
        dataset.save_records([static_record()])


def test_participant_sessions_stay_separate_and_splits_never_share_participants():
    records = [
        static_record("a1", "participant-a", "session-a1"),
        static_record("a2", "participant-a", "session-a2"),
        static_record("b1", "participant-b", "session-b1"),
        static_record("c1", "participant-c", "session-c1"),
        static_record("d1", "participant-d", "session-d1"),
    ]

    splits = split_records_by_participant(records, seed=7)
    participant_sets = [
        {record["participant_id"] for record in split}
        for split in splits.values()
    ]

    assert records[0]["recording_session_id"] != records[1]["recording_session_id"]
    assert len(participant_sets[0] | participant_sets[1] | participant_sets[2]) == 4
    assert not participant_sets[0].intersection(participant_sets[1])
    assert not participant_sets[0].intersection(participant_sets[2])
    assert not participant_sets[1].intersection(participant_sets[2])
    assert sum(map(len, splits.values())) == len(records)


def test_export_split_requires_at_least_three_participants():
    with pytest.raises(DatasetValidationError, match="three distinct participants"):
        split_records_by_participant([static_record()])


def test_export_command_writes_jsonl_splits_and_manifest(tmp_path, monkeypatch):
    input_path = tmp_path / "source.jsonl"
    output_dir = tmp_path / "splits"
    source = GestureDatasetService(input_path)
    source.save_records([
        static_record("a", "participant-a"),
        static_record("b", "participant-b"),
        static_record("c", "participant-c"),
    ])
    monkeypatch.setattr(
        sys,
        "argv",
        [
            "export_gesture_dataset.py",
            "--input",
            str(input_path),
            "--output-dir",
            str(output_dir),
            "--seed",
            "7",
        ],
    )

    assert export_dataset() == 0

    manifest = json.loads((output_dir / "split_manifest.json").read_text(encoding="utf-8"))
    assert set(manifest["participant_ids"]) == {"train", "validation", "test"}
    split_participants = [
        set(participants) for participants in manifest["participant_ids"].values()
    ]
    assert all(len(participants) == 1 for participants in split_participants)
    assert not split_participants[0].intersection(split_participants[1])
    assert not split_participants[0].intersection(split_participants[2])
    assert not split_participants[1].intersection(split_participants[2])
    assert all((output_dir / f"{split}.jsonl").exists() for split in ("train", "validation", "test"))
