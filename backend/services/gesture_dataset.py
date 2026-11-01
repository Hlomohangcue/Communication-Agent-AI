import json
import math
import os
import random
import re
import threading
from contextlib import contextmanager
from datetime import datetime
from pathlib import Path
from typing import Any, Dict, Iterable, Iterator, List, Optional


DATASET_VERSION = 1
FEATURE_VERSION = "mediapipe_hand_landmarks_xyz_v1"
DEFAULT_GESTURE_LABELS = ("open_palm", "fist", "thumbs_up", "wave", "unknown")
DEFAULT_DYNAMIC_LABELS = ("wave",)
MIN_DYNAMIC_OBSERVATIONS = 5
MAX_DYNAMIC_OBSERVATIONS = 2000
MAX_RECORDS_PER_SAVE = 5000


class DatasetValidationError(ValueError):
    """Raised when a gesture dataset record does not match the dataset contract."""


class GestureDatasetService:
    def __init__(
        self,
        path: str | Path,
        gesture_labels: Optional[Iterable[str]] = None,
        dynamic_labels: Optional[Iterable[str]] = None,
    ) -> None:
        self.path = Path(path)
        self.gesture_labels = tuple(
            DEFAULT_GESTURE_LABELS if gesture_labels is None else gesture_labels
        )
        self.dynamic_labels = tuple(
            DEFAULT_DYNAMIC_LABELS if dynamic_labels is None else dynamic_labels
        )
        self._thread_lock = threading.Lock()

        if not self.gesture_labels or len(set(self.gesture_labels)) != len(self.gesture_labels):
            raise ValueError("Gesture dataset labels must be non-empty and unique")
        if any(not self._valid_label(label) for label in self.gesture_labels):
            raise ValueError("Gesture dataset labels must use lowercase snake_case")
        if not set(self.dynamic_labels).issubset(self.gesture_labels):
            raise ValueError("Dynamic gesture labels must be present in gesture_labels")

    @staticmethod
    def _valid_label(value: Any) -> bool:
        return isinstance(value, str) and re.fullmatch(r"[a-z][a-z0-9_]{0,63}", value) is not None

    @staticmethod
    def _validate_identifier(value: Any, field: str) -> str:
        if (
            not isinstance(value, str)
            or re.fullmatch(r"[A-Za-z0-9][A-Za-z0-9_-]{0,63}", value) is None
        ):
            raise DatasetValidationError(
                f"{field} must be a non-empty pseudonymous identifier (letters, digits, _ or -)"
            )
        return value

    @staticmethod
    def _validate_timestamp(value: Any, field: str) -> str:
        if not isinstance(value, str) or not value:
            raise DatasetValidationError(f"{field} must be an ISO-8601 timestamp")
        try:
            datetime.fromisoformat(value.replace("Z", "+00:00"))
        except ValueError as exc:
            raise DatasetValidationError(f"{field} must be an ISO-8601 timestamp") from exc
        return value

    @staticmethod
    def _validate_confidence(value: Any, field: str) -> float:
        if (
            isinstance(value, bool)
            or not isinstance(value, (int, float))
            or not math.isfinite(value)
            or value < 0
            or value > 1
        ):
            raise DatasetValidationError(f"{field} must be a finite number from 0 to 1")
        return float(value)

    @staticmethod
    def _validate_landmarks(landmarks: Any, field: str) -> List[Dict[str, float]]:
        if not isinstance(landmarks, list) or len(landmarks) != 21:
            raise DatasetValidationError(f"{field} must contain exactly 21 hand landmarks")

        validated = []
        for index, landmark in enumerate(landmarks):
            if not isinstance(landmark, dict):
                raise DatasetValidationError(f"{field}[{index}] must contain x, y and z")
            point = {}
            for coordinate in ("x", "y", "z"):
                value = landmark.get(coordinate)
                if (
                    isinstance(value, bool)
                    or not isinstance(value, (int, float))
                    or not math.isfinite(value)
                ):
                    raise DatasetValidationError(
                        f"{field}[{index}].{coordinate} must be a finite number"
                    )
                point[coordinate] = float(value)
            validated.append(point)
        return validated

    def validate_record(self, record: Any) -> Dict[str, Any]:
        if not isinstance(record, dict):
            raise DatasetValidationError("Each dataset record must be an object")

        sample_id = record.get("sample_id")
        if not isinstance(sample_id, str) or not sample_id.strip() or len(sample_id) > 80:
            raise DatasetValidationError("sample_id must be a non-empty string of at most 80 characters")
        if record.get("dataset_version") != DATASET_VERSION:
            raise DatasetValidationError(f"dataset_version must be {DATASET_VERSION}")

        participant_id = self._validate_identifier(record.get("participant_id"), "participant_id")
        recording_session_id = self._validate_identifier(
            record.get("recording_session_id"), "recording_session_id"
        )
        gesture_label = record.get("gesture_label")
        if gesture_label not in self.gesture_labels:
            raise DatasetValidationError(f"Invalid gesture label: {gesture_label!r}")

        hand_side = record.get("hand_side")
        if hand_side not in ("Left", "Right"):
            raise DatasetValidationError("hand_side must be 'Left' or 'Right'")
        sample_type = record.get("sample_type")
        expected_type = "dynamic" if gesture_label in self.dynamic_labels else "static"
        if sample_type != expected_type:
            raise DatasetValidationError(
                f"Gesture label {gesture_label!r} requires sample_type {expected_type!r}"
            )
        timestamp = self._validate_timestamp(record.get("timestamp"), "timestamp")
        if record.get("feature_version") != FEATURE_VERSION:
            raise DatasetValidationError(f"feature_version must be {FEATURE_VERSION!r}")

        validated = {
            "dataset_version": DATASET_VERSION,
            "sample_id": sample_id,
            "participant_id": participant_id,
            "recording_session_id": recording_session_id,
            "gesture_label": gesture_label,
            "hand_side": hand_side,
            "timestamp": timestamp,
            "feature_version": FEATURE_VERSION,
            "sample_type": sample_type,
        }

        if sample_type == "static":
            validated["landmarks"] = self._validate_landmarks(
                record.get("landmarks"), "landmarks"
            )
            validated["handedness_confidence"] = self._validate_confidence(
                record.get("handedness_confidence"), "handedness_confidence"
            )
            return validated

        observations = record.get("landmarks")
        if not isinstance(observations, list):
            raise DatasetValidationError("Dynamic landmarks must be an ordered observation list")
        if len(observations) < MIN_DYNAMIC_OBSERVATIONS:
            raise DatasetValidationError(
                f"Dynamic recordings require at least {MIN_DYNAMIC_OBSERVATIONS} observations"
            )
        if len(observations) > MAX_DYNAMIC_OBSERVATIONS:
            raise DatasetValidationError(
                f"Dynamic recordings may contain at most {MAX_DYNAMIC_OBSERVATIONS} observations"
            )

        validated_observations = []
        previous_timestamp_ms = None
        for index, observation in enumerate(observations):
            field = f"landmarks[{index}]"
            if not isinstance(observation, dict):
                raise DatasetValidationError(f"{field} must be an observation object")
            observation_timestamp = self._validate_timestamp(
                observation.get("timestamp"), f"{field}.timestamp"
            )
            timestamp_ms = observation.get("timestamp_ms")
            if (
                isinstance(timestamp_ms, bool)
                or not isinstance(timestamp_ms, (int, float))
                or not math.isfinite(timestamp_ms)
            ):
                raise DatasetValidationError(f"{field}.timestamp_ms must be a finite number")
            if previous_timestamp_ms is not None and timestamp_ms <= previous_timestamp_ms:
                raise DatasetValidationError("Dynamic observation timestamps must be strictly increasing")
            previous_timestamp_ms = timestamp_ms
            validated_observations.append({
                "timestamp": observation_timestamp,
                "timestamp_ms": float(timestamp_ms),
                "handedness_confidence": self._validate_confidence(
                    observation.get("handedness_confidence"),
                    f"{field}.handedness_confidence",
                ),
                "landmarks": self._validate_landmarks(
                    observation.get("landmarks"), f"{field}.landmarks"
                ),
            })

        if validated_observations[0]["timestamp"] != timestamp:
            raise DatasetValidationError(
                "Dynamic record timestamp must match its first observation"
            )
        validated["landmarks"] = validated_observations
        return validated

    @contextmanager
    def _exclusive_lock(self) -> Iterator[None]:
        lock_path = self.path.with_name(self.path.name + ".lock")
        lock_path.parent.mkdir(parents=True, exist_ok=True)
        with self._thread_lock, lock_path.open("a+b") as lock_file:
            if os.name == "nt":
                import msvcrt

                lock_file.seek(0)
                if lock_file.read(1) == b"":
                    lock_file.seek(0)
                    lock_file.write(b"\0")
                    lock_file.flush()
                lock_file.seek(0)
                msvcrt.locking(lock_file.fileno(), msvcrt.LK_LOCK, 1)
                try:
                    yield
                finally:
                    lock_file.seek(0)
                    msvcrt.locking(lock_file.fileno(), msvcrt.LK_UNLCK, 1)
            else:
                import fcntl

                fcntl.flock(lock_file.fileno(), fcntl.LOCK_EX)
                try:
                    yield
                finally:
                    fcntl.flock(lock_file.fileno(), fcntl.LOCK_UN)

    def read_records(self) -> List[Dict[str, Any]]:
        if not self.path.exists():
            return []
        records = []
        sample_ids = set()
        try:
            with self.path.open("r", encoding="utf-8") as dataset_file:
                for line_number, line in enumerate(dataset_file, start=1):
                    if not line.strip():
                        continue
                    try:
                        record = self.validate_record(json.loads(line))
                    except (json.JSONDecodeError, DatasetValidationError) as exc:
                        raise DatasetValidationError(
                            f"Invalid dataset record on line {line_number}: {exc}"
                        ) from exc
                    if record["sample_id"] in sample_ids:
                        raise DatasetValidationError(
                            f"Duplicate sample_id in dataset: {record['sample_id']}"
                        )
                    sample_ids.add(record["sample_id"])
                    records.append(record)
        except OSError:
            raise
        return records

    def save_records(self, records: Any) -> int:
        if not isinstance(records, list) or not records:
            raise DatasetValidationError("records must be a non-empty list")
        if len(records) > MAX_RECORDS_PER_SAVE:
            raise DatasetValidationError(
                f"A recording may contain at most {MAX_RECORDS_PER_SAVE} records"
            )

        validated = [self.validate_record(record) for record in records]
        sample_ids = [record["sample_id"] for record in validated]
        if len(sample_ids) != len(set(sample_ids)):
            raise DatasetValidationError("Duplicate sample_id in submitted records")

        with self._exclusive_lock():
            existing_ids = {record["sample_id"] for record in self.read_records()}
            duplicate_ids = existing_ids.intersection(sample_ids)
            if duplicate_ids:
                duplicate_id = sorted(duplicate_ids)[0]
                raise DatasetValidationError(f"Duplicate sample_id: {duplicate_id}")

            self.path.parent.mkdir(parents=True, exist_ok=True)
            payload = "".join(
                json.dumps(record, separators=(",", ":"), ensure_ascii=False) + "\n"
                for record in validated
            )
            with self.path.open("a", encoding="utf-8", newline="\n") as dataset_file:
                written = dataset_file.write(payload)
                if written != len(payload):
                    raise OSError("Dataset write was incomplete")
                dataset_file.flush()
                os.fsync(dataset_file.fileno())
        return len(validated)


def split_records_by_participant(
    records: Iterable[Dict[str, Any]],
    seed: int = 42,
) -> Dict[str, List[Dict[str, Any]]]:
    records = list(records)
    participant_ids = sorted({record["participant_id"] for record in records})
    if len(participant_ids) < 3:
        raise DatasetValidationError(
            "At least three distinct participants are required for train/validation/test splits"
        )

    shuffled = participant_ids[:]
    random.Random(seed).shuffle(shuffled)
    test_count = max(1, round(len(shuffled) * 0.15))
    validation_count = max(1, round(len(shuffled) * 0.15))
    train_count = len(shuffled) - test_count - validation_count
    if train_count < 1:
        raise DatasetValidationError("Not enough participants for non-empty dataset splits")

    assignments = {
        "train": set(shuffled[:train_count]),
        "validation": set(shuffled[train_count:train_count + validation_count]),
        "test": set(shuffled[train_count + validation_count:]),
    }
    return {
        split: [record for record in records if record["participant_id"] in split_participants]
        for split, split_participants in assignments.items()
    }
