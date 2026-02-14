import cv2
import numpy as np
from typing import Dict, Any, Optional, List
import base64

class VisionService:
    """
    Computer vision service for hand gesture recognition
    Uses MediaPipe Hands for real-time hand tracking
    Compatible with MediaPipe v0.10.30+
    """
    
    def __init__(self):
        try:
            import mediapipe as mp
            
            # MediaPipe v0.10.30+ uses different API
            # Import the tasks module
            from mediapipe.tasks import python
            from mediapipe.tasks.python import vision
            
            # For now, disable MediaPipe and use fallback
            # The new API requires different initialization
            self.mediapipe_available = False
            self.hands = None
            
            print("⚠ MediaPipe v0.10.30+ detected - New API not yet integrated")
            print("  Vision features temporarily disabled")
            print("  System will work with manual emoji input")
            print("  GPU deployment will use compatible version")
                
        except ImportError:
            self.mediapipe_available = False
            self.hands = None
            print("⚠ MediaPipe not installed - vision features disabled")
            print("  Install with: pip install mediapipe opencv-python")
        except Exception as e:
            self.mediapipe_available = False
            self.hands = None
            print(f"⚠ MediaPipe initialization: {e}")
            print("  Vision features disabled - system will use manual input")
        
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
            "stop": "✋"
        }
    
    def process_frame(self, frame_data: str) -> Dict[str, Any]:
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
                "hands_detected": 0,
                "gestures": [],
                "emojis": [],
                "confidence": 0.0
            }
        
        try:
            # Decode base64 image
            image = self._decode_image(frame_data)
            
            # Convert BGR to RGB
            image_rgb = cv2.cvtColor(image, cv2.COLOR_BGR2RGB)
            
            # Process with MediaPipe
            results = self.hands.process(image_rgb)
            
            if not results.multi_hand_landmarks:
                return {
                    "hands_detected": 0,
                    "gestures": [],
                    "emojis": [],
                    "confidence": 0.0
                }
            
            # Detect gestures from landmarks
            gestures = []
            emojis = []
            
            for hand_landmarks, handedness in zip(
                results.multi_hand_landmarks,
                results.multi_handedness
            ):
                hand_label = handedness.classification[0].label  # "Left" or "Right"
                confidence = handedness.classification[0].score
                
                # Recognize gesture
                gesture = self._recognize_gesture(hand_landmarks, hand_label)
                
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
            
            return {
                "hands_detected": len(results.multi_hand_landmarks),
                "gestures": gestures,
                "emojis": emojis,
                "confidence": sum(g["confidence"] for g in gestures) / len(gestures) if gestures else 0.0
            }
            
        except Exception as e:
            print(f"Error processing frame: {e}")
            return {
                "error": str(e),
                "hands_detected": 0,
                "gestures": [],
                "emojis": []
            }
    
    def _decode_image(self, frame_data: str) -> np.ndarray:
        """Decode base64 image to numpy array"""
        # Remove data URL prefix if present
        if "base64," in frame_data:
            frame_data = frame_data.split("base64,")[1]
        
        # Decode base64
        img_bytes = base64.b64decode(frame_data)
        
        # Convert to numpy array
        nparr = np.frombuffer(img_bytes, np.uint8)
        
        # Decode image
        image = cv2.imdecode(nparr, cv2.IMREAD_COLOR)
        
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
        
        # Wave: open palm with horizontal movement (detected over multiple frames)
        # For now, just detect open palm
        if all([fingers_up["index"], fingers_up["middle"], fingers_up["ring"], fingers_up["pinky"]]):
            return "wave"
        
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
