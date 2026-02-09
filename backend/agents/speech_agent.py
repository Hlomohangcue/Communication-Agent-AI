import os
from typing import Dict, Any
import google.generativeai as genai
import sys
sys.path.append(os.path.dirname(os.path.dirname(__file__)))
from config import GEMINI_API_KEY

class SpeechAgent:
    def __init__(self):
        api_key = GEMINI_API_KEY
        print(f"=== SpeechAgent Initialization ===")
        print(f"API Key present: {'YES' if api_key else 'NO'}")
        print(f"API Key length: {len(api_key) if api_key else 0}")
        
        if api_key:
            try:
                genai.configure(api_key=api_key)
                # Try different model names based on API version
                try:
                    self.model = genai.GenerativeModel('gemini-1.5-flash-latest')
                except:
                    try:
                        self.model = genai.GenerativeModel('models/gemini-1.5-flash-latest')
                    except:
                        self.model = genai.GenerativeModel('models/gemini-pro')
                print("✓ Gemini model initialized successfully for speech generation")
            except Exception as e:
                print(f"✗ Error initializing Gemini: {e}")
                self.model = None
        else:
            print("✗ No API key found, using fallback template responses")
            self.model = None
    
    async def generate_output(self, intent: str, semantic_meaning: str, confidence: float) -> Dict[str, Any]:
        if self.model:
            try:
                prompt = f"""You are a supportive teacher/caregiver responding to a non-verbal student's communication.

Student's intent: {intent}
Student's message: {semantic_meaning}
Confidence: {confidence}

Generate a warm, helpful response that:
1. Acknowledges what the student communicated
2. Provides a direct answer if they asked a question
3. Offers support or assistance if needed
4. Is concise (1-3 sentences)
5. Is appropriate for a classroom setting

If the student asked a specific question (like "what is 1+1"), answer it directly and clearly.

Provide only the response text, nothing else."""

                response = self.model.generate_content(prompt)
                output_text = response.text.strip()
                
                # Clean up any markdown or extra formatting
                output_text = output_text.replace('**', '').replace('*', '')
                
                return {
                    "text": output_text,
                    "format": "speech",
                    "generation_method": "ai"
                }
            except Exception as e:
                print(f"Gemini API error: {e}")
                return self._fallback_output(intent, semantic_meaning)
        else:
            return self._fallback_output(intent, semantic_meaning)
    
    def _fallback_output(self, intent: str, semantic_meaning: str) -> Dict[str, Any]:
        # More specific and varied templates based on intent and meaning
        templates = {
            "request_help": [
                "I'm here to help you. What do you need?",
                "Of course, I'll help you with that.",
                "Let me assist you right away."
            ],
            "ask_question": [
                "That's a great question! Let me help you find the answer.",
                "I'm glad you asked. Let's explore that together.",
                "Good question! Let me explain that to you."
            ],
            "express_need": [
                "I understand. Let me help you with that.",
                "I hear you. Let's take care of that.",
                "Thank you for letting me know. I'll help you."
            ],
            "greet": [
                "Hello! It's wonderful to see you!",
                "Hi there! How are you doing today?",
                "Good to see you! How can I help you?"
            ],
            "respond": [
                "Thank you for sharing that with me.",
                "I appreciate you telling me that.",
                "I understand what you're saying."
            ]
        }
        
        # Convert to lowercase for easier matching
        meaning_lower = semantic_meaning.lower()
        
        # Check for specific patterns in semantic meaning
        if "👋" in semantic_meaning or "greeting" in meaning_lower:
            text = "Hello! It's great to see you today!"
        elif "🙋" in semantic_meaning or "raise hand" in meaning_lower or "need attention" in meaning_lower:
            text = "I see you need help. What can I do for you?"
        elif "❓" in semantic_meaning or "question" in meaning_lower:
            text = "I'm listening. What would you like to know?"
        elif "✋" in semantic_meaning or "stop" in meaning_lower or "wait" in meaning_lower:
            text = "Okay, I'll wait. Take your time."
        elif "👍" in semantic_meaning or ("yes" in meaning_lower and "agree" in meaning_lower):
            text = "Great! I'm glad we're on the same page."
        elif "👎" in semantic_meaning or ("no" in meaning_lower and "disagree" in meaning_lower):
            text = "I understand. Let's try a different approach."
        elif "🚽" in semantic_meaning or "bathroom" in meaning_lower:
            text = "Of course, you may go to the bathroom."
        elif "🍎" in semantic_meaning or "hungry" in meaning_lower or "food" in meaning_lower:
            text = "I understand you're hungry. Let's get you something to eat."
        elif "💧" in semantic_meaning or "thirsty" in meaning_lower or "water" in meaning_lower:
            text = "Let me get you some water right away."
        elif "😊" in semantic_meaning or "happy" in meaning_lower:
            text = "I'm so glad you're feeling happy!"
        elif "😢" in semantic_meaning or "sad" in meaning_lower:
            text = "I'm sorry you're feeling sad. I'm here for you."
        elif "😰" in semantic_meaning or "anxious" in meaning_lower or "worried" in meaning_lower:
            text = "It's okay to feel worried. Let's talk about it."
        elif "🤔" in semantic_meaning or "thinking" in meaning_lower or "confused" in meaning_lower:
            text = "Take your time to think. I'm here if you need help."
        elif "😴" in semantic_meaning or "tired" in meaning_lower or "sleepy" in meaning_lower:
            text = "You look tired. Would you like to take a break?"
        elif "🤒" in semantic_meaning or "sick" in meaning_lower or "not feeling well" in meaning_lower:
            text = "I'm sorry you're not feeling well. Let me help you."
        elif "📚" in semantic_meaning or "study" in meaning_lower or "learn" in meaning_lower or "book" in meaning_lower:
            text = "Great! Let's study together. What would you like to learn?"
        elif "🎨" in semantic_meaning or "art" in meaning_lower or "creative" in meaning_lower:
            text = "Art time! That sounds fun. What would you like to create?"
        elif "⚽" in semantic_meaning or "play" in meaning_lower or "sports" in meaning_lower or "game" in meaning_lower:
            text = "Time to play! What game would you like to play?"
        elif "🏠" in semantic_meaning or "home" in meaning_lower:
            text = "I understand you want to go home. It won't be long now."
        elif "👨‍👩‍👧" in semantic_meaning or "family" in meaning_lower or "parents" in meaning_lower:
            text = "You're thinking about your family. They'll be here soon."
        elif "🙏" in semantic_meaning or "please" in meaning_lower:
            text = "Of course! I appreciate you asking so nicely."
        elif "❤️" in semantic_meaning or "love" in meaning_lower or "like" in meaning_lower:
            text = "That's wonderful! I'm glad you feel that way."
        elif "🎉" in semantic_meaning or "celebrate" in meaning_lower or "excited" in meaning_lower:
            text = "How exciting! Let's celebrate together!"
        elif "😡" in semantic_meaning or "angry" in meaning_lower or "frustrated" in meaning_lower:
            text = "I can see you're upset. Let's talk about what's bothering you."
        else:
            # Use varied responses from templates
            import random
            responses = templates.get(intent, ["I understand. How can I help you?"])
            text = random.choice(responses)
        
        return {
            "text": text,
            "format": "speech",
            "generation_method": "template"
        }
