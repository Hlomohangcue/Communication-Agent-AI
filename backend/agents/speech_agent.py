from typing import Dict, Any, Optional
import logging

try:
    from services.llm_client import GeminiClient
except ImportError:
    from backend.services.llm_client import GeminiClient


logger = logging.getLogger(__name__)


class SpeechAgent:
    def __init__(self):
        self.client = GeminiClient()
        self.model = self.client.model
        logger.info("SpeechAgent initialized (gemini_available=%s)", bool(self.model))

    async def generate_output(
        self,
        intent: str,
        semantic_meaning: str,
        confidence: float,
        context: Optional[Dict[str, Any]] = None,
    ) -> Dict[str, Any]:
        if self.model:
            try:
                prompt = f"""You are a supportive teacher/caregiver responding to a non-verbal student's communication.

Student's intent: {intent}
Student's message: {semantic_meaning}
Confidence: {confidence}
Previous conversation: {context.get('summary', '') if context else 'None'}

Generate a warm, helpful response that:
1. Acknowledges what the student communicated
2. Provides a direct answer if they asked a question
3. Offers support or assistance if needed
4. Is concise (1-3 sentences)
5. Is appropriate for a classroom setting
6. Avoids harmful or unsafe instructions
7. If information is uncertain, state uncertainty briefly and ask a clarifying follow-up
8. Keep the reply relevant to the recent conversation context if available

Provide only the response text, nothing else."""

                response = self.model.generate_content(prompt)
                output_text = response.text.strip()
                output_text = output_text.replace('**', '').replace('*', '')

                return {
                    "text": output_text,
                    "format": "speech",
                    "generation_method": "ai",
                }
            except Exception as e:
                logger.exception("SpeechAgent Gemini call failed: %s", e)
                return self._fallback_output(intent, semantic_meaning, context=context)
        return self._fallback_output(intent, semantic_meaning, context=context)

    def _fallback_output(
        self,
        intent: str,
        semantic_meaning: str,
        context: Optional[Dict[str, Any]] = None,
    ) -> Dict[str, Any]:
        meaning_lower = semantic_meaning.lower()
        recent_messages = context.get("recent_messages", []) if context else []

        last_user_message = ""
        if recent_messages:
            last_user_message = (recent_messages[-1].get("input_text") or "").strip()

        if "thank you" in meaning_lower or "thanks" in meaning_lower or "🙏" in semantic_meaning:
            text = "You're very welcome! I'm happy to help you."
        elif "water" in meaning_lower or "thirsty" in meaning_lower or "💧" in semantic_meaning:
            text = "You need some water. I'll help you get it."
        elif "hungry" in meaning_lower or "food" in meaning_lower or "🍎" in semantic_meaning:
            text = "You seem hungry. Let's get something to eat."
        elif "hello" in meaning_lower or "hi" in meaning_lower or "👋" in semantic_meaning:
            text = "Hello! It's great to see you today!"
        elif "good morning" in meaning_lower:
            text = "Good morning! I hope you're ready for a great day!"
        elif "goodbye" in meaning_lower or "bye" in meaning_lower:
            text = "Goodbye! Have a wonderful rest of your day!"
        elif "help" in meaning_lower or "need" in meaning_lower or "🙋" in semantic_meaning:
            text = "I'm here to help you. What do you need?"
        elif "question" in meaning_lower or "?" in meaning_lower or "❓" in semantic_meaning:
            text = "I can help with that. What would you like to know?"
        elif "happy" in meaning_lower or "😊" in semantic_meaning:
            text = "I'm glad you're feeling happy today!"
        elif "not feeling well" in meaning_lower or "sick" in meaning_lower or "hurt" in meaning_lower:
            text = "I'm sorry you're not feeling well. Let's get you some support."
        elif last_user_message and (last_user_message.lower() in meaning_lower or meaning_lower in last_user_message.lower()):
            text = f"You mentioned {last_user_message}. I'll keep helping with that."
        else:
            templates = {
                "request_help": [
                    "I'm here to help you. What do you need?",
                    "Of course, I'll help you with that.",
                    "Let me assist you right away.",
                ],
                "ask_question": [
                    "That's a great question! Let me help you find the answer.",
                    "I'm glad you asked. Let's explore that together.",
                    "Good question! Let me explain that to you.",
                ],
                "express_need": [
                    "I understand. Let me help you with that.",
                    "I hear you. Let's take care of that.",
                    "Thank you for letting me know. I'll help you.",
                ],
                "greet": [
                    "Hello! It's wonderful to see you!",
                    "Hi there! How are you doing today?",
                    "Good to see you! How can I help you?",
                ],
                "respond": [
                    "Thank you for sharing that with me.",
                    "I appreciate you telling me that.",
                    "I understand what you're saying.",
                ],
            }
            default_templates = templates.get(intent.lower(), templates["respond"])
            text = default_templates[0]

        return {
            "text": text,
            "format": "speech",
            "generation_method": "fallback",
        }
