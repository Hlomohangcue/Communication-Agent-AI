"""
Gesture Meaning Service
Maps detected hand gestures to their semantic meanings and generates appropriate responses
"""

class GestureMeaningService:
    """Service to interpret gesture meanings and generate contextual responses"""
    
    def __init__(self):
        # Map gestures to their primary meanings
        self.gesture_meanings = {
            "wave": {
                "primary": "greeting",
                "meanings": ["hello", "hi", "goodbye", "bye"],
                "context": "greeting or farewell"
            },
            "thumbs_up": {
                "primary": "agreement",
                "meanings": ["yes", "good", "agree", "okay", "correct"],
                "context": "positive affirmation"
            },
            "thumbs_down": {
                "primary": "disagreement",
                "meanings": ["no", "bad", "disagree", "wrong", "not good"],
                "context": "negative response"
            },
            "peace": {
                "primary": "peace",
                "meanings": ["peace", "victory", "two", "second"],
                "context": "peace sign or number two"
            },
            "ok": {
                "primary": "confirmation",
                "meanings": ["okay", "perfect", "fine", "good", "alright"],
                "context": "confirmation or approval"
            },
            "pointing_up": {
                "primary": "attention",
                "meanings": ["wait", "attention", "one", "first", "listen"],
                "context": "requesting attention or indicating number one"
            },
            "fist": {
                "primary": "power",
                "meanings": ["stop", "power", "strength", "solidarity", "zero"],
                "context": "stop gesture or showing strength"
            },
            "open_palm": {
                "primary": "stop",
                "meanings": ["stop", "wait", "five", "hand"],
                "context": "stop or wait gesture"
            },
            "raised_hand": {
                "primary": "question",
                "meanings": ["question", "raise hand", "ask", "help", "attention"],
                "context": "asking a question or requesting help"
            },
            "stop": {
                "primary": "halt",
                "meanings": ["stop", "halt", "wait", "pause"],
                "context": "stop or pause action"
            }
        }
        
        # Contextual response templates
        self.response_templates = {
            "greeting": [
                "Hello! How can I help you today?",
                "Hi there! What would you like to communicate?",
                "Greetings! I'm here to assist you.",
                "Hello! Nice to see you!"
            ],
            "farewell": [
                "Goodbye! Have a great day!",
                "See you later! Take care!",
                "Bye! Come back anytime!",
                "Farewell! Stay safe!"
            ],
            "agreement": [
                "Great! I understand you agree.",
                "Wonderful! That's a yes from you.",
                "Perfect! You're saying yes.",
                "Excellent! You approve."
            ],
            "disagreement": [
                "I understand you disagree.",
                "Okay, that's a no from you.",
                "Got it, you don't agree.",
                "Understood, you're saying no."
            ],
            "confirmation": [
                "Perfect! Everything is okay.",
                "Great! You're confirming this is fine.",
                "Wonderful! You're saying it's all good.",
                "Excellent! You approve."
            ],
            "attention": [
                "Yes, I'm listening. What would you like to say?",
                "You have my attention. Please continue.",
                "I'm here. What do you need?",
                "Yes? How can I help you?"
            ],
            "question": [
                "Yes, I see you have a question. What would you like to know?",
                "You're raising your hand. What's your question?",
                "I'm here to help. What do you need?",
                "Yes? What would you like to ask?"
            ],
            "stop": [
                "Okay, I'll stop. Let me know when you're ready to continue.",
                "Understood, pausing now.",
                "Alright, I'll wait for your signal.",
                "Stopping as requested."
            ],
            "power": [
                "I see your gesture. What would you like to communicate?",
                "Understood. How can I assist you?",
                "Got it. What do you need?",
                "I'm listening. Please continue."
            ],
            "peace": [
                "Peace to you too!",
                "I understand. Is there anything else?",
                "Got it. What would you like to communicate?",
                "Understood. How can I help?"
            ]
        }
    
    def interpret_gesture(self, gesture_name: str, context: str = "general") -> Dict[str, Any]:
        """
        Interpret a gesture and return its meaning
        
        Args:
            gesture_name: Name of the detected gesture
            context: Context of the conversation (general, classroom, etc.)
            
        Returns:
            Dict with interpretation and suggested response
        """
        if gesture_name not in self.gesture_meanings:
            return {
                "gesture": gesture_name,
                "understood": False,
                "meaning": "unknown",
                "interpretation": f"I detected a {gesture_name} gesture but I'm not sure what you mean.",
                "suggested_response": "Could you please clarify what you're trying to communicate?"
            }
        
        gesture_info = self.gesture_meanings[gesture_name]
        primary_meaning = gesture_info["primary"]
        
        # Get appropriate response based on context
        response_category = self._get_response_category(gesture_name, context)
        responses = self.response_templates.get(response_category, self.response_templates["power"])
        
        import random
        suggested_response = random.choice(responses)
        
        return {
            "gesture": gesture_name,
            "understood": True,
            "meaning": primary_meaning,
            "possible_meanings": gesture_info["meanings"],
            "context_description": gesture_info["context"],
            "interpretation": f"You're showing a {gesture_name} gesture, which typically means: {', '.join(gesture_info['meanings'][:3])}",
            "suggested_response": suggested_response
        }
    
    def _get_response_category(self, gesture_name: str, context: str) -> str:
        """Determine the appropriate response category based on gesture and context"""
        
        # Map gestures to response categories
        gesture_to_category = {
            "wave": "greeting",  # Could be greeting or farewell based on context
            "thumbs_up": "agreement",
            "thumbs_down": "disagreement",
            "ok": "confirmation",
            "pointing_up": "attention",
            "raised_hand": "question",
            "stop": "stop",
            "open_palm": "stop",
            "fist": "power",
            "peace": "peace"
        }
        
        return gesture_to_category.get(gesture_name, "power")
    
    def generate_response(self, gestures: List[str], context: str = "general") -> Dict[str, Any]:
        """
        Generate a comprehensive response for multiple gestures
        
        Args:
            gestures: List of detected gesture names
            context: Conversation context
            
        Returns:
            Dict with combined interpretation and response
        """
        if not gestures:
            return {
                "understood": False,
                "message": "No gestures detected. Please try again.",
                "response": "I didn't detect any gestures. Could you please try again?"
            }
        
        # Interpret each gesture
        interpretations = [self.interpret_gesture(g, context) for g in gestures]
        
        # Combine meanings
        all_meanings = []
        for interp in interpretations:
            if interp["understood"]:
                all_meanings.extend(interp["possible_meanings"][:2])
        
        # Generate combined response
        if len(gestures) == 1:
            primary_interp = interpretations[0]
            return {
                "understood": primary_interp["understood"],
                "gestures": gestures,
                "message": primary_interp["interpretation"],
                "response": primary_interp["suggested_response"],
                "meanings": primary_interp.get("possible_meanings", [])
            }
        else:
            # Multiple gestures - combine meanings
            combined_message = f"I detected {len(gestures)} gestures: {', '.join(gestures)}. "
            combined_message += f"This could mean: {', '.join(all_meanings[:5])}."
            
            return {
                "understood": True,
                "gestures": gestures,
                "message": combined_message,
                "response": "I see you're communicating multiple things. Could you clarify what you need?",
                "meanings": all_meanings
            }
    
    def get_gesture_info(self, gesture_name: str) -> Dict[str, Any]:
        """Get detailed information about a specific gesture"""
        return self.gesture_meanings.get(gesture_name, {
            "primary": "unknown",
            "meanings": [],
            "context": "unknown gesture"
        })
