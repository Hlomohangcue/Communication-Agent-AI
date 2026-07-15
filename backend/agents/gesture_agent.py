"""
Gesture Translation Agent
Translates text/speech to gesture sequences for non-verbal users
"""

import logging

try:
    from services.llm_client import GeminiClient
except ImportError:
    from backend.services.llm_client import GeminiClient


logger = logging.getLogger(__name__)

class GestureAgent:
    def __init__(self):
        """Initialize the Gesture Translation Agent"""
        self.client = GeminiClient()
        self.model = self.client.model
        
        # Gesture library with ASL meanings
        self.gesture_library = {
            # Basic Communication
            "hello": "👋",
            "goodbye": "👋",
            "hi": "👋",
            "bye": "👋",
            "yes": "👍",
            "no": "👎",
            "ok": "👌",
            "good": "👍",
            "bad": "👎",
            "stop": "✋",
            "wait": "✋",
            "please": "🙏",
            "thank you": "🙏",
            "thanks": "🙏",
            "love": "🤟",
            
            # Questions
            "what": "❓",
            "why": "❔",
            "how": "🤷",
            "when": "🕐",
            "where": "📍",
            "who": "👤",
            "question": "❓",
            
            # Needs
            "bathroom": "🚻",
            "restroom": "🚻",
            "water": "💧",
            "drink": "💧",
            "thirsty": "💧",
            "food": "🍎",
            "hungry": "🍎",
            "eat": "🍎",
            "book": "📚",
            "read": "📖",
            "write": "✏️",
            "help": "🆘",
            
            # Emotions
            "happy": "😊",
            "sad": "😢",
            "angry": "😠",
            "mad": "😠",
            "scared": "😰",
            "worried": "😰",
            "tired": "😴",
            "sick": "🤒",
            "fine": "👌",
            
            # Classroom
            "raise hand": "✋",
            "hand": "✋",
            "math": "🧮",
            "science": "🔬",
            "art": "🎨",
            "music": "🎵",
            "break": "⏸️",
            "rest": "⏸️",
            "finished": "✅",
            "done": "✅",
            "ready": "✅",
            
            # Pronouns
            "i": "👤",
            "me": "👤",
            "you": "👉",
            "we": "👥",
            "us": "👥",
            
            # Actions
            "go": "🚶",
            "come": "🚶",
            "sit": "💺",
            "stand": "🧍",
            "look": "👀",
            "listen": "👂",
            "speak": "🗣️",
            "talk": "🗣️",
            "understand": "🧠",
            "know": "🧠",
            "think": "🧠",
            
            # Time
            "now": "⏰",
            "later": "⏰",
            "today": "📅",
            "tomorrow": "📅",
            "morning": "☀️",
            "afternoon": "🌤️",
            "night": "🌙",
            
            # Negation
            "not": "❌",
            "don't": "❌",
            "can't": "❌",
            "won't": "❌",
        }
        
        # Common phrase mappings
        self.phrase_mappings = {
            "good morning": "👋 ☀️",
            "good afternoon": "👋 🌤️",
            "good night": "👋 🌙",
            "how are you": "❓ 😊",
            "i'm fine": "👤 👍",
            "thank you": "🙏",
            "you're welcome": "👍 😊",
            "i don't understand": "👤 ❌ 🧠",
            "can you help me": "❓ 🆘 👤",
            "i need help": "👤 🆘",
            "i have a question": "👤 ❓",
            "can i go to the bathroom": "❓ 👤 🚻",
            "i'm hungry": "👤 🍎",
            "i'm thirsty": "👤 💧",
            "i'm tired": "👤 😴",
            "i'm ready": "👤 ✅",
            "i'm finished": "👤 ✅",
            "please repeat": "🙏 🔄",
            "i agree": "👤 👍",
            "i disagree": "👤 👎",
        }
    
    def text_to_gestures(self, text: str) -> dict:
        """
        Convert text to gesture sequence
        
        Args:
            text: Input text from verbal user
            
        Returns:
            dict with gesture_sequence, text, and explanation
        """
        text_lower = text.lower().strip()
        
        # Check for exact phrase match first
        if text_lower in self.phrase_mappings:
            gesture_sequence = self.phrase_mappings[text_lower]
            return {
                "gesture_sequence": gesture_sequence,
                "original_text": text,
                "method": "phrase_match",
                "gestures": gesture_sequence.split(),
                "explanation": f"Common phrase: '{text}'"
            }
        
        # Try keyword-based mapping
        gestures = []
        words = text_lower.split()
        matched_words = []
        
        for word in words:
            # Remove punctuation
            clean_word = word.strip('.,!?;:')
            
            if clean_word in self.gesture_library:
                gestures.append(self.gesture_library[clean_word])
                matched_words.append(clean_word)
        
        if gestures:
            gesture_sequence = " ".join(gestures)
            return {
                "gesture_sequence": gesture_sequence,
                "original_text": text,
                "method": "keyword_match",
                "gestures": gestures,
                "matched_words": matched_words,
                "explanation": f"Matched keywords: {', '.join(matched_words)}"
            }
        
        # Use AI for complex sentences
        try:
            if not self.model:
                raise RuntimeError("Gemini model unavailable")
            ai_result = self._ai_translate(text)
            return ai_result
        except Exception as e:
            logger.exception("Gesture AI translation error: %s", e)
            # Fallback to basic representation
            return {
                "gesture_sequence": "💬 ❓",
                "original_text": text,
                "method": "fallback",
                "gestures": ["💬", "❓"],
                "explanation": "Complex message - showing generic communication icon"
            }
    
    def _ai_translate(self, text: str) -> dict:
        """Use Gemini AI to translate complex text to gestures"""
        
        # Create a prompt with available gestures
        gesture_list = "\n".join([f"- {word}: {emoji}" for word, emoji in list(self.gesture_library.items())[:50]])
        
        prompt = f"""You are a gesture translation assistant. Convert the following text into a sequence of emojis/gestures that represent the meaning.

Available gestures:
{gesture_list}

Text to translate: "{text}"

Rules:
1. Use only emojis from the available gestures list above
2. Keep the sequence short (3-6 gestures maximum)
3. Focus on key concepts
4. Maintain the core meaning
5. Return ONLY the emoji sequence separated by spaces, nothing else

Example:
Input: "Can you help me with my homework?"
Output: ❓ 🆘 📚

Now translate: "{text}"
"""
        
        try:
            response = self.model.generate_content(prompt)
            gesture_sequence = response.text.strip()
            
            # Clean up the response
            gesture_sequence = gesture_sequence.replace('\n', ' ').strip()
            allowed = set(self.gesture_library.values())
            validated_gestures = [token for token in gesture_sequence.split() if token in allowed]

            if not validated_gestures:
                validated_gestures = ["💬", "❓"]
                method = "ai_translation_fallback_filtered"
            else:
                method = "ai_translation"
            
            return {
                "gesture_sequence": " ".join(validated_gestures),
                "original_text": text,
                "method": method,
                "gestures": validated_gestures,
                "explanation": "AI-generated gesture sequence with allowlist validation"
            }
        except Exception as e:
            raise Exception(f"AI translation failed: {str(e)}")
    
    def get_gesture_library(self) -> dict:
        """Return the complete gesture library"""
        return self.gesture_library
    
    def get_common_phrases(self) -> dict:
        """Return common phrase mappings"""
        return self.phrase_mappings
    
    def get_gestures_by_category(self) -> dict:
        """Return gestures organized by category"""
        return {
            "basic": {
                "hello": "👋", "goodbye": "👋", "yes": "👍", "no": "👎",
                "ok": "👌", "please": "🙏", "thank you": "🙏", "love": "🤟"
            },
            "questions": {
                "what": "❓", "why": "❔", "how": "🤷", "when": "🕐",
                "where": "📍", "who": "👤"
            },
            "needs": {
                "bathroom": "🚻", "water": "💧", "food": "🍎", "help": "🆘",
                "book": "📚", "read": "📖", "write": "✏️"
            },
            "emotions": {
                "happy": "😊", "sad": "😢", "angry": "😠", "scared": "😰",
                "tired": "😴", "sick": "🤒"
            },
            "classroom": {
                "raise hand": "✋", "math": "🧮", "science": "🔬", "art": "🎨",
                "music": "🎵", "break": "⏸️", "finished": "✅"
            }
        }
