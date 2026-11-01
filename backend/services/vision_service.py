import cv2
import numpy as np
from typing import Dict, Any, Optional, List
import base64
import binascii
import logging
import os
from datetime import datetime, timezone
from pathlib import Path

from .dynamic_gesture_tracker import DynamicGestureTracker


logger = logging.getLogger(__name__)


class VisionService:
    """
    Computer vision service for hand gesture recognition
    Uses MediaPipe Tasks for real-time hand landmark detection.
    """

    LANDMARK_INDEX = {
        "WRIST": 0,
        "THUMB_IP": 3,
        "THUMB_TIP": 4,
        "INDEX_FINGER_MCP": 5,
        "INDEX_FINGER_PIP": 6,
        "INDEX_FINGER_TIP": 8,
        "MIDDLE_FINGER_MCP": 9,
        "MIDDLE_FINGER_PIP": 10,
        "MIDDLE_FINGER_TIP": 12,
        "RING_FINGER_MCP": 13,
        "RING_FINGER_PIP": 14,
        "RING_FINGER_TIP": 16,
        "PINKY_FINGER_MCP": 17,
        "PINKY_FINGER_PIP": 18,
        "PINKY_FINGER_TIP": 20,
    }

    def __init__(self):
        self.dynamic_gesture_tracker = DynamicGestureTracker()
        self.mp = None
        self.hand_landmarker = None
        try:
            import mediapipe as mp

            model_path = Path(
                os.environ.get(
                    "MEDIAPIPE_HAND_LANDMARKER_MODEL_PATH",
                    Path(__file__).resolve().parents[2]
                    / "models"
                    / "hand_landmarker.task",
                )
            )
            options = mp.tasks.vision.HandLandmarkerOptions(
                base_options=mp.tasks.BaseOptions(model_asset_path=str(model_path)),
                running_mode=mp.tasks.vision.RunningMode.IMAGE,
                num_hands=2,
                min_hand_detection_confidence=0.5,
                min_hand_presence_confidence=0.5,
                min_tracking_confidence=0.5,
            )
            self.mp = mp
            self.hand_landmarker = (
                mp.tasks.vision.HandLandmarker.create_from_options(options)
            )
            self.mediapipe_available = True
            logger.info(
                "MediaPipe Tasks initialized successfully (version=%s)",
                mp.__version__,
            )
        except ImportError:
            self.mediapipe_available = False
            logger.warning("MediaPipe is not installed; vision features are disabled")
        except FileNotFoundError:
            self.mediapipe_available = False
            logger.error(
                "MediaPipe hand-landmarker model is missing; configure "
                "MEDIAPIPE_HAND_LANDMARKER_MODEL_PATH"
            )
        except Exception as exc:
            self.mediapipe_available = False
            logger.exception("MediaPipe initialization error: %s", exc)

        # Gesture mappings
        self.gesture_to_emoji = {
            "wave": "👋",
            "thumbs_up": "👍",
            "thumbs_down": "👎",
            "peace": "✌️",
            "ok": "👌",
            "pointing_up": "☝️",
            "fist": "✊",
            "open_palm": "🖐️",
            "raised_hand": "🙋",
            "stop": "✋",
            "i_love_you": "🤟",  # ILY sign - pinky, index, and thumb extended
            "call_me": "🤙",  # Shaka/call me sign - thumb and pinky extended
            "rock_on": "🤘",  # Rock on sign - index and pinky extended
            "crossed_fingers": "🤞",  # Crossed fingers - index and middle crossed
            "pinch": "🤏",  # Pinching gesture - thumb and index close
            "three": "🖖",  # Vulcan salute or number three
            "pray": "🙏",  # Praying hands - palms together
            "clap": "👏"  # Clapping - two open palms
        }
    
    def process_frame(
        self,
        frame_data: str,
        tracking_session_id: Optional[str] = None,
        timestamp_ms: Optional[float] = None,
    ) -> Dict[str, Any]:
        """
        Process a single frame from webcam
        
        Args:
            frame_data: Base64 encoded image
        
        Returns:
            Dict with detected gestures and landmarks
        """
        if not self.mediapipe_available:
            return {
                "error": "Hand landmark detection is unavailable",
                "error_type": "vision_unavailable",
            }
        
        try:
            image = self._decode_image(frame_data)
        except (ValueError, cv2.error) as e:
            logger.warning("Rejected invalid vision frame: %s", e)
            if tracking_session_id:
                self.dynamic_gesture_tracker.reset_movement_history(tracking_session_id)
            return {
                "error": f"Invalid frame: {e}",
                "error_type": "invalid_frame",
            }

        try:
            results = self._detect_hands(image)
            landmarks_by_hand = results.hand_landmarks or []
            handedness_by_hand = results.handedness or []

            if len(landmarks_by_hand) != len(handedness_by_hand):
                logger.error("MediaPipe returned mismatched hand landmarks and handedness")
                return {
                    "error": "Hand landmark metadata was incomplete",
                    "error_type": "incomplete_detection",
                }

            if not landmarks_by_hand:
                if tracking_session_id and timestamp_ms is not None:
                    self.dynamic_gesture_tracker.update(
                        tracking_session_id,
                        timestamp_ms,
                        [],
                    )
                return {
                    "hands_detected": 0,
                    "gestures": [],
                    "emojis": [],
                    "confidence": 0.0
                }
            
            # Detect gestures from landmarks
            gestures = []
            emojis = []
            tracked_hands = []

            for hand_landmarks, handedness in zip(
                landmarks_by_hand,
                handedness_by_hand,
            ):
                if not handedness:
                    logger.error("MediaPipe returned missing handedness metadata")
                    return {
                        "error": "Hand landmark metadata was incomplete",
                        "error_type": "incomplete_detection",
                    }
                classification = handedness[0]
                hand_label = classification.category_name
                confidence = float(classification.score)

                # Recognize gesture
                gesture = self._recognize_gesture(hand_landmarks, hand_label)
                tracked_hands.append({
                    "hand": hand_label if confidence >= 0.55 else None,
                    "landmarks": hand_landmarks,
                    "static_gesture": gesture,
                })

                if gesture:
                    gestures.append({
                        "gesture": gesture,
                        "hand": hand_label,
                        "confidence": confidence
                    })
                    
                    # Map to emoji
                    emoji = self.gesture_to_emoji.get(gesture, "")
                    if emoji:
                        emojis.append(emoji)
            
            motion_diagnostics = {}
            if tracking_session_id and timestamp_ms is not None:
                motion_diagnostics = self.dynamic_gesture_tracker.update(
                    tracking_session_id,
                    timestamp_ms,
                    tracked_hands,
                )
                for detected_gesture in gestures:
                    motion = motion_diagnostics.get(detected_gesture["hand"])
                    if not motion:
                        continue
                    if motion["dynamic_gesture"] == "wave":
                        detected_gesture["gesture"] = "wave"
                    detected_gesture.update({
                        "movement_direction": motion["movement_direction"],
                        "movement_displacement": motion["movement_displacement"],
                        "movement_velocity": motion["movement_velocity"],
                        "wrist_movement_direction": motion["wrist_movement_direction"],
                        "wrist_movement_displacement": motion["wrist_movement_displacement"],
                        "wrist_movement_velocity": motion["wrist_movement_velocity"],
                        "dynamic_gesture_confidence": motion["dynamic_gesture_confidence"],
                    })
                emojis = [
                    self.gesture_to_emoji[gesture["gesture"]]
                    for gesture in gestures
                    if gesture["gesture"] in self.gesture_to_emoji
                ]
            else:
                # Without a camera-session key and timestamp, retain static-only behavior.
                for detected_gesture in gestures:
                    detected_gesture.update({
                        "movement_direction": "unavailable",
                        "movement_displacement": 0.0,
                        "movement_velocity": 0.0,
                        "wrist_movement_direction": "unavailable",
                        "wrist_movement_displacement": 0.0,
                        "wrist_movement_velocity": 0.0,
                        "dynamic_gesture_confidence": 0.0,
                    })

            return {
                "hands_detected": len(landmarks_by_hand),
                "gestures": gestures,
                "emojis": emojis,
                "confidence": sum(g["confidence"] for g in gestures) / len(gestures) if gestures else 0.0
            }
            
        except Exception as e:
            logger.exception("Error processing frame: %s", e)
            if tracking_session_id:
                self.dynamic_gesture_tracker.reset_movement_history(tracking_session_id)
            return {
                "error": "Frame processing failed",
                "error_type": "processing_error",
            }

    def _detect_hands(self, image: np.ndarray):
        image_rgb = cv2.cvtColor(image, cv2.COLOR_BGR2RGB)
        task_image = self.mp.Image(
            image_format=self.mp.ImageFormat.SRGB,
            data=image_rgb,
        )
        return self.hand_landmarker.detect(task_image)

    def extract_hand_landmarks(
        self,
        frame_data: str,
        timestamp_ms: Optional[float] = None,
    ) -> Dict[str, Any]:
        """Return MediaPipe observations without applying gesture-label heuristics."""
        if not self.mediapipe_available:
            return {
                "error": "Hand landmark detection is unavailable",
                "error_type": "vision_unavailable",
            }

        try:
            image = self._decode_image(frame_data)
        except (ValueError, cv2.error) as exc:
            logger.warning("Rejected invalid landmark collection frame: %s", exc)
            return {
                "error": f"Invalid frame: {exc}",
                "error_type": "invalid_frame",
            }

        try:
            results = self._detect_hands(image)
            landmarks_by_hand = results.hand_landmarks or []
            handedness_by_hand = results.handedness or []
            if len(landmarks_by_hand) != len(handedness_by_hand):
                logger.error("MediaPipe returned mismatched hand landmarks and handedness")
                return {
                    "error": "Hand landmark metadata was incomplete",
                    "error_type": "incomplete_detection",
                }

            captured_at = datetime.now(timezone.utc).isoformat()
            observations = []
            for hand_landmarks, handedness in zip(
                landmarks_by_hand, handedness_by_hand
            ):
                if (
                    not handedness
                    or len(hand_landmarks) != 21
                ):
                    logger.error("MediaPipe returned an incomplete hand observation")
                    return {
                        "error": "Hand landmark metadata was incomplete",
                        "error_type": "incomplete_detection",
                        "hands_detected": 0,
                        "observations": [],
                    }
                classification = handedness[0]
                observations.append({
                    "hand_side": classification.category_name,
                    "handedness_confidence": float(classification.score),
                    "timestamp": captured_at,
                    "timestamp_ms": timestamp_ms,
                    "landmarks": [
                        {"x": float(point.x), "y": float(point.y), "z": float(point.z)}
                        for point in hand_landmarks
                    ],
                })

            return {
                "hands_detected": len(observations),
                "observations": observations,
            }
        except Exception as exc:
            logger.exception("Error extracting hand landmarks: %s", exc)
            return {
                "error": "Landmark extraction failed",
                "error_type": "processing_error",
            }

    @staticmethod
    def _landmark_points(landmarks):
        return getattr(landmarks, "landmark", landmarks)

    def _decode_image(self, frame_data: str) -> np.ndarray:
        """Decode base64 image to numpy array"""
        if not isinstance(frame_data, str) or not frame_data.strip():
            raise ValueError("Frame data is empty")

        # Remove data URL prefix if present
        if "base64," in frame_data:
            frame_data = frame_data.split("base64,")[1]

        # Decode base64
        try:
            img_bytes = base64.b64decode(frame_data, validate=True)
        except (ValueError, binascii.Error) as exc:
            raise ValueError("Frame data is not valid base64") from exc

        if not img_bytes:
            raise ValueError("Frame image data is empty")

        # Convert to numpy array
        nparr = np.frombuffer(img_bytes, np.uint8)

        # Decode image
        try:
            image = cv2.imdecode(nparr, cv2.IMREAD_COLOR)
        except cv2.error as exc:
            raise ValueError("Frame data does not contain a valid image") from exc

        if (
            image is None or
            image.size == 0 or
            image.ndim != 3 or
            image.shape[0] <= 0 or
            image.shape[1] <= 0
        ):
            raise ValueError("Frame data does not contain a valid image")

        return image
    
    def _recognize_gesture(self, landmarks, hand_label: str) -> Optional[str]:
        """
        Recognize gesture from hand landmarks
        
        Args:
            landmarks: MediaPipe hand landmarks
            hand_label: "Left" or "Right"
        
        Returns:
            Gesture name or None
        """
        # Get landmark positions
        landmarks = self._landmark_points(landmarks)
        thumb_tip = landmarks[self.LANDMARK_INDEX["THUMB_TIP"]]
        index_tip = landmarks[self.LANDMARK_INDEX["INDEX_FINGER_TIP"]]
        middle_tip = landmarks[self.LANDMARK_INDEX["MIDDLE_FINGER_TIP"]]
        ring_tip = landmarks[self.LANDMARK_INDEX["RING_FINGER_TIP"]]
        pinky_tip = landmarks[self.LANDMARK_INDEX["PINKY_FINGER_TIP"]]

        wrist = landmarks[self.LANDMARK_INDEX["WRIST"]]

        thumb_ip = landmarks[self.LANDMARK_INDEX["THUMB_IP"]]
        index_mcp = landmarks[self.LANDMARK_INDEX["INDEX_FINGER_MCP"]]
        middle_mcp = landmarks[self.LANDMARK_INDEX["MIDDLE_FINGER_MCP"]]
        ring_mcp = landmarks[self.LANDMARK_INDEX["RING_FINGER_MCP"]]
        pinky_mcp = landmarks[self.LANDMARK_INDEX["PINKY_FINGER_MCP"]]

        # Calculate which fingers are extended
        fingers_up = self._count_fingers_up(landmarks)
        
        # Gesture recognition logic
        
        # Thumbs up: thumb up, other fingers down
        if fingers_up["thumb"] and not any([
            fingers_up["index"],
            fingers_up["middle"],
            fingers_up["ring"],
            fingers_up["pinky"]
        ]):
            return "thumbs_up"
        
        # Thumbs down: thumb down, other fingers curled
        if not fingers_up["thumb"] and thumb_tip.y > thumb_ip.y:
            if not any([fingers_up["index"], fingers_up["middle"], fingers_up["ring"], fingers_up["pinky"]]):
                return "thumbs_down"
        
        # Peace sign: index and middle up, others down
        if fingers_up["index"] and fingers_up["middle"]:
            if not fingers_up["ring"] and not fingers_up["pinky"]:
                return "peace"
        
        # OK sign: thumb and index forming circle
        thumb_index_dist = self._distance(thumb_tip, index_tip)
        if thumb_index_dist < 0.05:  # Close together
            if fingers_up["middle"] and fingers_up["ring"] and fingers_up["pinky"]:
                return "ok"
        
        # Pointing up: only index finger up
        if fingers_up["index"] and not any([
            fingers_up["middle"],
            fingers_up["ring"],
            fingers_up["pinky"]
        ]):
            return "pointing_up"
        
        # Fist: all fingers down
        if not any(fingers_up.values()):
            return "fist"
        
        # I Love You sign: thumb, index, and pinky up (middle and ring down)
        if fingers_up["thumb"] and fingers_up["index"] and fingers_up["pinky"]:
            if not fingers_up["middle"] and not fingers_up["ring"]:
                return "i_love_you"
        
        # Call me / Shaka: thumb and pinky up (others down)
        if fingers_up["thumb"] and fingers_up["pinky"]:
            if not any([fingers_up["index"], fingers_up["middle"], fingers_up["ring"]]):
                return "call_me"
        
        # Rock on: index and pinky up (thumb, middle, ring down)
        if fingers_up["index"] and fingers_up["pinky"]:
            if not fingers_up["thumb"] and not fingers_up["middle"] and not fingers_up["ring"]:
                return "rock_on"
        
        # Three fingers / Vulcan salute: index, middle, ring up
        if fingers_up["index"] and fingers_up["middle"] and fingers_up["ring"]:
            if not fingers_up["pinky"]:
                return "three"
        
        # Pinch: thumb and index close together, others down
        thumb_index_dist = self._distance(thumb_tip, index_tip)
        if thumb_index_dist < 0.03:  # Very close together
            if not any([fingers_up["middle"], fingers_up["ring"], fingers_up["pinky"]]):
                return "pinch"
        
        # Open palm / Stop: all fingers up
        if all([
            fingers_up["thumb"],
            fingers_up["index"],
            fingers_up["middle"],
            fingers_up["ring"],
            fingers_up["pinky"]
        ]):
            # Check if hand is raised (above wrist level)
            avg_finger_y = (index_tip.y + middle_tip.y + ring_tip.y + pinky_tip.y) / 4
            if avg_finger_y < wrist.y - 0.1:  # Fingers significantly above wrist
                return "raised_hand"
            else:
                return "open_palm"
        
        # An open-looking static pose is not a wave; motion tracking decides that.
        if all([fingers_up["index"], fingers_up["middle"], fingers_up["ring"], fingers_up["pinky"]]):
            return "open_palm"
        
        return None
    
    def _count_fingers_up(self, landmarks) -> Dict[str, bool]:
        """Count which fingers are extended"""
        landmarks = self._landmark_points(landmarks)

        # Get key landmarks
        thumb_tip = landmarks[self.LANDMARK_INDEX["THUMB_TIP"]]
        thumb_ip = landmarks[self.LANDMARK_INDEX["THUMB_IP"]]

        index_tip = landmarks[self.LANDMARK_INDEX["INDEX_FINGER_TIP"]]
        index_pip = landmarks[self.LANDMARK_INDEX["INDEX_FINGER_PIP"]]

        middle_tip = landmarks[self.LANDMARK_INDEX["MIDDLE_FINGER_TIP"]]
        middle_pip = landmarks[self.LANDMARK_INDEX["MIDDLE_FINGER_PIP"]]

        ring_tip = landmarks[self.LANDMARK_INDEX["RING_FINGER_TIP"]]
        ring_pip = landmarks[self.LANDMARK_INDEX["RING_FINGER_PIP"]]

        pinky_tip = landmarks[self.LANDMARK_INDEX["PINKY_FINGER_TIP"]]
        pinky_pip = landmarks[self.LANDMARK_INDEX["PINKY_FINGER_PIP"]]

        # Check if each finger is extended (tip above PIP joint)
        return {
            "thumb": thumb_tip.x < thumb_ip.x - 0.05 or thumb_tip.x > thumb_ip.x + 0.05,  # Horizontal check for thumb
            "index": index_tip.y < index_pip.y,
            "middle": middle_tip.y < middle_pip.y,
            "ring": ring_tip.y < ring_pip.y,
            "pinky": pinky_tip.y < pinky_pip.y
        }
    
    def _distance(self, point1, point2) -> float:
        """Calculate Euclidean distance between two landmarks"""
        return np.sqrt(
            (point1.x - point2.x) ** 2 +
            (point1.y - point2.y) ** 2 +
            (point1.z - point2.z) ** 2
        )
    
    def get_supported_gestures(self) -> List[Dict[str, str]]:
        """Get list of supported gestures"""
        return [
            {"gesture": gesture, "emoji": emoji}
            for gesture, emoji in self.gesture_to_emoji.items()
        ]
    
    def cleanup(self):
        """Clean up resources"""
        if self.hand_landmarker:
            self.hand_landmarker.close()
