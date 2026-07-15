from typing import Dict, Any
import logging

try:
    from services.llm_client import GeminiClient
except ImportError:
    from backend.services.llm_client import GeminiClient


logger = logging.getLogger(__name__)

class NonVerbalAgent:
    def __init__(self):
        self.client = GeminiClient()
        self.model = self.client.model
        
        # Symbol/gesture token mappings
        self.token_map = {
            "👋": "greeting",
            "🙋": "raise hand / need attention",
            "❓": "question",
            "✋": "stop / wait",
            "👍": "yes / agree",
            "👎": "no / disagree",
            "🚽": "bathroom need",
            "🍎": "hungry / food",
            "💧": "thirsty / water",
            "😊": "happy",
            "😢": "sad",
            "😰": "anxious / worried",
            "🤔": "thinking / confused",
            "😴": "tired / sleepy",
            "🤒": "sick / not feeling well",
            "📚": "study / learn / book",
            "🎨": "art / creative activity",
            "⚽": "play / sports / game",
            "🏠": "home / want to go home",
            "👨‍👩‍👧": "family / parents",
            "🙏": "please / request politely",
            "❤️": "love / like",
            "🎉": "celebrate / excited",
            "😡": "angry / frustrated"
        }
    
    async def interpret(self, input_text: str) -> Dict[str, Any]:
        # Check for known tokens
        tokens_found = []
        for token, meaning in self.token_map.items():
            if token in input_text:
                tokens_found.append({"token": token, "meaning": meaning})
        
        if self.model:
            try:
                prompt = f"""Interpret the following non-verbal communication input. It may contain symbols, gesture tokens, or simple text.

Input: {input_text}

Known tokens detected: {tokens_found if tokens_found else "None"}

Provide:
1. Semantic meaning (what the user is trying to communicate)
2. Emotional tone
3. Urgency level (low/medium/high)

Be concise and clear."""

                response = self.model.generate_content(prompt)
                result_text = response.text
                
                # Preserve original input in semantic meaning for emoji matching
                semantic_with_input = f"{input_text} - {result_text}"
                
                return {
                    "original_input": input_text,
                    "tokens_detected": tokens_found,
                    "semantic_meaning": semantic_with_input,
                    "interpretation_method": "ai_enhanced"
                }
            except Exception as e:
                logger.exception("NonVerbalAgent Gemini call failed: %s", e)
                return self._fallback_interpretation(input_text, tokens_found)
        else:
            return self._fallback_interpretation(input_text, tokens_found)
    
    def _fallback_interpretation(self, input_text: str, tokens_found: list) -> Dict[str, Any]:
        # Preserve the original input as semantic meaning so speech agent can match emojis
        if tokens_found:
            meanings = [t["meaning"] for t in tokens_found]
            # Include both the original input AND the interpretation
            semantic = f"{input_text} ({', '.join(meanings)})"
        else:
            # For text input, just pass it through
            semantic = input_text
        
        return {
            "original_input": input_text,
            "tokens_detected": tokens_found,
            "semantic_meaning": semantic,
            "interpretation_method": "rule_based"
        }
