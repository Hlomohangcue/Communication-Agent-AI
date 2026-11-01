import cv2
import numpy as np
from typing import Dict, Any, Optional, List
import base64
import binascii
import logging
from datetime import datetime, timezone

from .dynamic_gesture_tracker import DynamicGestureTracker


logger = logging.getLogger(__name__)

class VisionService:
    """
    Computer vision service for hand gesture recognition
    Uses MediaPipe Hands for real-time hand tracking
    Uses MediaPipe's legacy Solutions Hands API.
    """
    
    def __init__(self):
        self.dynamic_gesture_tracker = DynamicGestureTracker()
        try:
            import mediapipe as mp
            
            # Use MediaPipe's legacy Solutions Hands API.
            self.mp_hands = mp.solutions.hands
            self.mp_drawing = mp.solutions.drawing_utils
            
            # Initialize hands detector
            self.hands = self.mp_hands.Hands(
                static_image_mode=False,
                max_num_hands=2,
                min_detection_confidence=0.5,
                min_tracking_confidence=0.5
            )
            
            self.mediapipe_available = True
            logger.info("MediaPipe initialized successfully (version=%s)", mp.__version__)
                
        except ImportError:
            self.mediapipe_available = False
            self.hands = None
            self.mp_hands = None
            self.mp_drawing = None
            logger.warning("MediaPipe not installed; vision features are disabled")
        except Exception as e:
            self.mediapipe_available = False
            self.hands = None
            self.mp_hands = None
            self.mp_drawing = None
            logger.exception("MediaPipe initialization error: %s", e)
        
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
                "error": "MediaPipe not installed",
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
            # Convert BGR to RGB
            image_rgb = cv2.cvtColor(image, cv2.COLOR_BGR2RGB)
            
            # Process with MediaPipe
            results = self.hands.process(image_rgb)
            
            if not results.multi_hand_landmarks:
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
                results.multi_hand_landmarks,
                results.multi_handedness
            ):
                hand_label = handedness.classification[0].label  # "Left" or "Right"
                confidence = handedness.classification[0].score
                
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
                "hands_detected": len(results.multi_hand_landmarks),
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

    def extract_hand_landmarks(
        self,
        frame_data: str,
        timestamp_ms: Optional[float] = None,
    ) -> Dict[str, Any]:
        """Return MediaPipe observations without applying gesture-label heuristics."""
        if not self.mediapipe_available:
            return {
                "error": "MediaPipe not installed",
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
            results = self.hands.process(cv2.cvtColor(image, cv2.COLOR_BGR2RGB))
            landmarks_by_hand = results.multi_hand_landmarks or []
            handedness_by_hand = results.multi_handedness or []
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
                    not handedness.classification
                    or len(hand_landmarks.landmark) != 21
                ):
                    logger.error("MediaPipe returned an incomplete hand observation")
                    return {
                        "error": "Hand landmark metadata was incomplete",
                        "error_type": "incomplete_detection",
                        "hands_detected": 0,
                        "observations": [],
                    }
                classification = handedness.classification[0]
                observations.append({
                    "hand_side": classification.label,
                    "handedness_confidence": float(classification.score),
                    "timestamp": captured_at,
                    "timestamp_ms": timestamp_ms,
                    "landmarks": [
                        {"x": float(point.x), "y": float(point.y), "z": float(point.z)}
                        for point in hand_landmarks.landmark
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
        thumb_tip = landmarks.landmark[self.mp_hands.HandLandmark.THUMB_TIP]
        index_tip = landmarks.landmark[self.mp_hands.HandLandmark.INDEX_FINGER_TIP]
        middle_tip = landmarks.landmark[self.mp_hands.HandLandmark.MIDDLE_FINGER_TIP]
        ring_tip = landmarks.landmark[self.mp_hands.HandLandmark.RING_FINGER_TIP]
        pinky_tip = landmarks.landmark[self.mp_hands.HandLandmark.PINKY_TIP]
        
        wrist = landmarks.landmark[self.mp_hands.HandLandmark.WRIST]
        
        thumb_ip = landmarks.landmark[self.mp_hands.HandLandmark.THUMB_IP]
        index_mcp = landmarks.landmark[self.mp_hands.HandLandmark.INDEX_FINGER_MCP]
        middle_mcp = landmarks.landmark[self.mp_hands.HandLandmark.MIDDLE_FINGER_MCP]
        ring_mcp = landmarks.landmark[self.mp_hands.HandLandmark.RING_FINGER_MCP]
        pinky_mcp = landmarks.landmark[self.mp_hands.HandLandmark.PINKY_MCP]
        
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
        # Get key landmarks
        thumb_tip = landmarks.landmark[self.mp_hands.HandLandmark.THUMB_TIP]
        thumb_ip = landmarks.landmark[self.mp_hands.HandLandmark.THUMB_IP]
        
        index_tip = landmarks.landmark[self.mp_hands.HandLandmark.INDEX_FINGER_TIP]
        index_pip = landmarks.landmark[self.mp_hands.HandLandmark.INDEX_FINGER_PIP]
        
        middle_tip = landmarks.landmark[self.mp_hands.HandLandmark.MIDDLE_FINGER_TIP]
        middle_pip = landmarks.landmark[self.mp_hands.HandLandmark.MIDDLE_FINGER_PIP]
        
        ring_tip = landmarks.landmark[self.mp_hands.HandLandmark.RING_FINGER_TIP]
        ring_pip = landmarks.landmark[self.mp_hands.HandLandmark.RING_FINGER_PIP]
        
        pinky_tip = landmarks.landmark[self.mp_hands.HandLandmark.PINKY_TIP]
        pinky_pip = landmarks.landmark[self.mp_hands.HandLandmark.PINKY_PIP]
        
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
        if self.hands:
            self.hands.close()
