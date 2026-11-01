from collections import OrderedDict, deque
from dataclasses import dataclass, field
import math
from typing import Deque, Dict, Iterable, Optional, Tuple


@dataclass
class _HandHistory:
    samples: Deque[Tuple[float, float, float, float, float]] = field(
        default_factory=lambda: deque(maxlen=9)
    )
    last_timestamp_ms: Optional[float] = None
    last_seen_timestamp_ms: Optional[float] = None
    wave_latched: bool = False
    wave_confidence: float = 0.0


class DynamicGestureTracker:
    """Recognize repeated horizontal open-palm movement in isolated camera streams."""

    MAX_TRACKS = 128
    MAX_SAMPLE_GAP_MS = 1250
    MAX_SEQUENCE_DURATION_MS = 4000
    WAVE_LATCH_TIMEOUT_MS = 3000
    MIN_SEGMENT_DISPLACEMENT = 0.55
    MIN_ALTERNATIONS = 3
    MIN_DYNAMIC_CONFIDENCE = 0.7
    MIN_MOVEMENT_SPEED = 0.5

    def __init__(self) -> None:
        self._streams: OrderedDict[str, Dict[str, _HandHistory]] = OrderedDict()

    @staticmethod
    def _normalized_palm_center(hand_landmarks) -> Tuple[float, float]:
        palm = [hand_landmarks.landmark[index] for index in (5, 9, 13, 17)]
        return (
            sum(point.x for point in palm) / 4,
            sum(point.y for point in palm) / 4,
        )

    @staticmethod
    def _palm_width(hand_landmarks) -> float:
        index_mcp = hand_landmarks.landmark[5]
        pinky_mcp = hand_landmarks.landmark[17]
        return math.hypot(index_mcp.x - pinky_mcp.x, index_mcp.y - pinky_mcp.y)

    @staticmethod
    def _alternating_segments(
        samples: Iterable[Tuple[float, float]], palm_width: float
    ) -> Tuple[int, Tuple[str, ...], float, float, str]:
        if palm_width <= 0:
            return 0, (), 0.0, 0.0, "stationary"

        movements = []
        samples = list(samples)
        if not samples:
            return 0, (), 0.0, 0.0, "stationary"

        extreme_time, extreme_x = samples[0]
        direction = 0
        latest_displacement = 0.0
        latest_velocity = 0.0
        latest_direction = "stationary"
        for timestamp_ms, x in samples[1:]:
            displacement = (x - extreme_x) / palm_width
            elapsed_seconds = (timestamp_ms - extreme_time) / 1000
            if elapsed_seconds <= 0:
                continue
            if direction == 0:
                if abs(displacement) < DynamicGestureTracker.MIN_SEGMENT_DISPLACEMENT:
                    continue
                velocity = displacement / elapsed_seconds
                if abs(velocity) < DynamicGestureTracker.MIN_MOVEMENT_SPEED:
                    continue
                direction = 1 if displacement > 0 else -1
                movements.append("right" if direction > 0 else "left")
                extreme_time, extreme_x = timestamp_ms, x
                latest_displacement = abs(displacement)
                latest_velocity = abs(velocity)
                latest_direction = movements[-1]
                continue

            if displacement * direction >= 0:
                if abs(displacement) >= DynamicGestureTracker.MIN_SEGMENT_DISPLACEMENT:
                    extreme_time, extreme_x = timestamp_ms, x
                    latest_displacement = abs(displacement)
                    latest_velocity = abs(displacement / elapsed_seconds)
                    latest_direction = "right" if direction > 0 else "left"
                continue

            reversal_displacement = abs(displacement)
            velocity = reversal_displacement / elapsed_seconds
            if (
                reversal_displacement >= DynamicGestureTracker.MIN_SEGMENT_DISPLACEMENT
                and velocity >= DynamicGestureTracker.MIN_MOVEMENT_SPEED
            ):
                direction *= -1
                movements.append("right" if direction > 0 else "left")
                extreme_time, extreme_x = timestamp_ms, x
                latest_displacement = reversal_displacement
                latest_velocity = velocity
                latest_direction = movements[-1]

        alternations = sum(
            1 for previous, current in zip(movements, movements[1:])
            if previous != current
        )
        return (
            alternations,
            tuple(movements),
            latest_displacement,
            latest_velocity,
            latest_direction,
        )

    @staticmethod
    def _confidence(alternations: int, movement_count: int) -> float:
        if movement_count < 2:
            return 0.0
        return min(1.0, 0.55 + 0.15 * alternations)

    def reset_stream(self, stream_id: str) -> None:
        self._streams.pop(stream_id, None)

    def reset_movement_history(self, stream_id: str) -> None:
        for history in self._streams.get(stream_id, {}).values():
            history.samples.clear()
            history.last_timestamp_ms = None

    def update(
        self,
        stream_id: str,
        timestamp_ms: float,
        hand_observations: list,
    ) -> Dict[str, Dict[str, object]]:
        if not stream_id or not math.isfinite(timestamp_ms):
            return {}

        stream = self._streams.pop(stream_id, {})
        self._streams[stream_id] = stream
        while len(self._streams) > self.MAX_TRACKS:
            self._streams.popitem(last=False)

        side_counts: Dict[str, int] = {}
        for observation in hand_observations:
            side = observation.get("hand")
            if side in ("Left", "Right") and observation.get("landmarks") is not None:
                side_counts[side] = side_counts.get(side, 0) + 1

        seen_sides = set()
        diagnostics: Dict[str, Dict[str, object]] = {}
        for observation in hand_observations:
            side = observation.get("hand")
            landmarks = observation.get("landmarks")
            if (
                side not in ("Left", "Right")
                or landmarks is None
                or side_counts.get(side) != 1
            ):
                continue

            seen_sides.add(side)
            history = stream.setdefault(side, _HandHistory())
            if (
                history.last_seen_timestamp_ms is not None
                and timestamp_ms - history.last_seen_timestamp_ms > self.WAVE_LATCH_TIMEOUT_MS
            ):
                history.wave_latched = False
                history.wave_confidence = 0.0
                history.samples.clear()
                history.last_timestamp_ms = None

            wrist = landmarks.landmark[0]
            center_x, center_y = self._normalized_palm_center(landmarks)
            palm_width = self._palm_width(landmarks)
            if (
                palm_width <= 0
                or not all(math.isfinite(value) for value in (wrist.x, wrist.y, center_x, center_y))
            ):
                history.samples.clear()
                history.last_timestamp_ms = None
                continue

            if (
                history.last_timestamp_ms is not None
                and (
                    timestamp_ms <= history.last_timestamp_ms
                    or timestamp_ms - history.last_timestamp_ms > self.MAX_SAMPLE_GAP_MS
                )
            ):
                history.samples.clear()
                history.last_timestamp_ms = None

            if history.last_timestamp_ms is None:
                history.samples.clear()
            history.samples.append((timestamp_ms, wrist.x, wrist.y, center_x, center_y))
            history.last_timestamp_ms = timestamp_ms
            history.last_seen_timestamp_ms = timestamp_ms

            if (
                history.samples
                and timestamp_ms - history.samples[0][0] > self.MAX_SEQUENCE_DURATION_MS
            ):
                while (
                    len(history.samples) > 2
                    and timestamp_ms - history.samples[0][0] > self.MAX_SEQUENCE_DURATION_MS
                ):
                    history.samples.popleft()

            alternations, movements, displacement, velocity, direction = self._alternating_segments(
                ((sample[0], sample[3]) for sample in history.samples),
                palm_width,
            )
            _, _, wrist_displacement, wrist_velocity, wrist_direction = self._alternating_segments(
                ((sample[0], sample[1]) for sample in history.samples),
                palm_width,
            )
            confidence = self._confidence(alternations, len(movements))
            static_gesture = observation.get("static_gesture")
            open_hand_pose = static_gesture in ("open_palm", "raised_hand")
            if not open_hand_pose:
                history.wave_latched = False
                history.wave_confidence = 0.0
                history.samples.clear()
                history.last_timestamp_ms = timestamp_ms
            elif (
                not history.wave_latched
                and alternations >= self.MIN_ALTERNATIONS
                and confidence >= self.MIN_DYNAMIC_CONFIDENCE
            ):
                history.wave_latched = True
                history.wave_confidence = confidence

            dynamic_gesture = "wave" if open_hand_pose and history.wave_latched else None

            diagnostics[side] = {
                "movement_direction": direction,
                "movement_displacement": displacement,
                "movement_velocity": velocity,
                "wrist_movement_direction": wrist_direction,
                "wrist_movement_displacement": wrist_displacement,
                "wrist_movement_velocity": wrist_velocity,
                "dynamic_gesture": dynamic_gesture,
                "dynamic_gesture_confidence": history.wave_confidence if dynamic_gesture else confidence,
                "alternating_movements": alternations,
                "wave_latched": history.wave_latched,
            }

        for side in tuple(stream):
            if side not in seen_sides:
                stream[side].samples.clear()
                stream[side].last_timestamp_ms = None
                last_seen = stream[side].last_seen_timestamp_ms
                if (
                    last_seen is not None
                    and timestamp_ms - last_seen > self.WAVE_LATCH_TIMEOUT_MS
                ):
                    stream[side].wave_latched = False
                    stream[side].wave_confidence = 0.0

        return diagnostics
