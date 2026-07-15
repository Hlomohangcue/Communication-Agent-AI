from typing import Dict, Any, Optional
import logging

try:
    from services.llm_client import GeminiClient
except ImportError:
    from backend.services.llm_client import GeminiClient


logger = logging.getLogger(__name__)

class IntentAgent:
    def __init__(self):
        self.client = GeminiClient()
        self.model = self.client.model
    
    async def detect_intent(self, semantic_meaning: str, context: Optional[Dict] = None) -> Dict[str, Any]:
        prompt = f"""Analyze the following communication and determine the user's intent.
        
Input: {semantic_meaning}
"""
        if context:
            prompt += f"\nPrevious context: {context.get('summary', '')}"
        
        prompt += """
Classify the intent into one of these categories:
- request_help
- ask_question
- express_need
- share_feeling
- greet
- respond
- other

Provide confidence score (0.0 to 1.0) and a brief explanation.

Respond in this format:
Intent: [category]
Confidence: [score]
Explanation: [brief explanation]
"""
        
        if self.model:
            try:
                response = self.model.generate_content(prompt)
                result_text = response.text
                
                # Parse response
                intent = "other"
                confidence = 0.5
                explanation = ""
                
                for line in result_text.split('\n'):
                    if line.startswith("Intent:"):
                        intent = line.split(":", 1)[1].strip()
                    elif line.startswith("Confidence:"):
                        try:
                            confidence = float(line.split(":", 1)[1].strip())
                        except ValueError:
                            confidence = 0.7
                    elif line.startswith("Explanation:"):
                        explanation = line.split(":", 1)[1].strip()
                
                return {
                    "intent": intent,
                    "confidence": confidence,
                    "explanation": explanation,
                    "raw_response": result_text
                }
            except Exception as e:
                logger.exception("IntentAgent Gemini call failed: %s", e)
                return self._fallback_intent(semantic_meaning)
        else:
            return self._fallback_intent(semantic_meaning)
    
    def _fallback_intent(self, text: str) -> Dict[str, Any]:
        text_lower = text.lower()
        
        # Check for specific patterns
        if any(word in text_lower for word in ["help", "need", "assist", "🙋"]):
            return {"intent": "request_help", "confidence": 0.85, "explanation": "Help request detected"}
        elif any(word in text_lower for word in ["what", "why", "how", "when", "where", "?", "❓"]):
            return {"intent": "ask_question", "confidence": 0.8, "explanation": "Question detected"}
        elif any(word in text_lower for word in ["hello", "hi", "hey", "greet", "👋"]):
            return {"intent": "greet", "confidence": 0.9, "explanation": "Greeting detected"}
        elif any(word in text_lower for word in ["yes", "agree", "okay", "sure", "👍"]):
            return {"intent": "respond", "confidence": 0.85, "explanation": "Agreement detected"}
        elif any(word in text_lower for word in ["no", "disagree", "not", "👎"]):
            return {"intent": "respond", "confidence": 0.85, "explanation": "Disagreement detected"}
        elif any(word in text_lower for word in ["stop", "wait", "hold", "✋"]):
            return {"intent": "request_help", "confidence": 0.8, "explanation": "Stop/wait request detected"}
        elif any(word in text_lower for word in ["bathroom", "restroom", "🚽"]):
            return {"intent": "express_need", "confidence": 0.95, "explanation": "Bathroom need detected"}
        elif any(word in text_lower for word in ["hungry", "food", "eat", "🍎"]):
            return {"intent": "express_need", "confidence": 0.95, "explanation": "Food need detected"}
        elif any(word in text_lower for word in ["thirsty", "water", "drink", "💧"]):
            return {"intent": "express_need", "confidence": 0.95, "explanation": "Water need detected"}
        else:
            return {"intent": "express_need", "confidence": 0.6, "explanation": "Default classification"}
