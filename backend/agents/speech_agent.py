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
        
        # Comprehensive gesture-to-response mapping
        # Greetings (using 👋 wave emoji)
        if "👋" in semantic_meaning and "☀️" in semantic_meaning:
            text = "Good morning! I hope you're ready for a great day!"
        elif "👋" in semantic_meaning and "🌤️" in semantic_meaning:
            text = "Good afternoon! How has your day been so far?"
        elif "👋" in semantic_meaning and "🌙" in semantic_meaning:
            text = "Good night! Sleep well and see you tomorrow!"
        elif "👋" in semantic_meaning and "✌️" in semantic_meaning:
            text = "Goodbye! Have a wonderful rest of your day!"
        # Check for standalone "hi" or "hello" - use word boundaries to avoid matching "thirsty"
        elif "👋" in semantic_meaning or " hello" in meaning_lower or "hello " in meaning_lower or meaning_lower == "hello" or " hi " in meaning_lower or meaning_lower == "hi" or meaning_lower.startswith("hi ") or meaning_lower.endswith(" hi"):
            text = "Hello! It's great to see you today!"
        
        # Raise hand (using 🙋 emoji) - for getting attention/asking questions
        elif "🙋" in semantic_meaning or "raise hand" in meaning_lower:
            text = "I see you need help. What can I do for you?"
        
        # Text-based greetings (when user types instead of using emojis)
        elif "good morning" in meaning_lower:
            text = "Good morning! I hope you're ready for a great day!"
        elif "good afternoon" in meaning_lower:
            text = "Good afternoon! How has your day been so far?"
        elif "good evening" in meaning_lower:
            text = "Good evening! How has your day been?"
        elif "good night" in meaning_lower:
            text = "Good night! Sleep well and see you tomorrow!"
        elif "goodbye" in meaning_lower or "bye" in meaning_lower:
            text = "Goodbye! Have a wonderful rest of your day!"
        
        # Polite expressions
        elif "🙏" in semantic_meaning and "❤️" in semantic_meaning:
            text = "You're very welcome! I'm happy to help you."
        elif "🙏" in semantic_meaning or "please" in meaning_lower:
            text = "Of course! I appreciate you asking so nicely."
        elif "👍" in semantic_meaning and "⭐" in semantic_meaning:
            text = "Thank you! You're doing an excellent job too!"
        elif "👍" in semantic_meaning or "yes" in meaning_lower:
            text = "Great! I'm glad we're on the same page."
        elif "👎" in semantic_meaning or "no" in meaning_lower:
            text = "I understand. Let's try a different approach."
        elif "👏" in semantic_meaning:
            text = "Thank you! I appreciate your enthusiasm!"
        
        # Classroom actions
        elif "🪑" in semantic_meaning and "⬇️" in semantic_meaning:
            text = "Okay, I'll sit down now. Thank you for letting me know."
        elif "🧍" in semantic_meaning and "⬆️" in semantic_meaning:
            text = "Standing up now. What would you like me to do?"
        elif "🤫" in semantic_meaning or "quiet" in meaning_lower:
            text = "I understand. I'll be quiet now."
        elif "👂" in semantic_meaning or "listen" in meaning_lower:
            text = "I'm listening carefully. Please go ahead."
        elif "👀" in semantic_meaning and "⚠️" in semantic_meaning:
            text = "You have my full attention. I'm focused now."
        elif "👀" in semantic_meaning or "look" in meaning_lower:
            text = "I'm looking. What would you like to show me?"
        elif "📖" in semantic_meaning and "➡️" in semantic_meaning:
            text = "Opening my book now. What page should I turn to?"
        elif "📖" in semantic_meaning or "read" in meaning_lower:
            text = "I'll start reading. Thank you for the reminder."
        elif "✍️" in semantic_meaning or "write" in meaning_lower:
            text = "I'll write that down. What should I write?"
        elif "📚" in semantic_meaning or "books" in meaning_lower:
            text = "I have my books ready. What should we study?"
        elif "✏️" in semantic_meaning or "pencil" in meaning_lower:
            text = "I have my pencil. I'm ready to work."
        elif "📄" in semantic_meaning or "paper" in meaning_lower:
            text = "I have paper ready. What should I do with it?"
        
        # Questions and help
        elif "🙋" in semantic_meaning or "raise hand" in meaning_lower:
            text = "I see you need help. What can I do for you?"
        elif "❓" in semantic_meaning and "❓" in semantic_meaning:
            text = "You have questions? I'm here to answer them all!"
        elif "❓" in semantic_meaning or "question" in meaning_lower:
            text = "I'm listening. What would you like to know?"
        elif "🆘" in semantic_meaning or "help" in meaning_lower:
            text = "I'm here to help! What do you need assistance with?"
        elif "💡" in semantic_meaning or "understand" in meaning_lower:
            text = "Great! I'm glad you understand. Well done!"
        elif "🔄" in semantic_meaning or "repeat" in meaning_lower or "again" in meaning_lower:
            text = "Of course! Let me explain that again for you."
        
        # Time and activities
        elif "⏰" in semantic_meaning and "☕" in semantic_meaning:
            text = "Yes, it's break time! Enjoy your rest."
        elif "🍽️" in semantic_meaning and "⏰" in semantic_meaning:
            text = "It's lunch time! Let's go eat."
        elif "⏰" in semantic_meaning or "time" in meaning_lower:
            text = "You're right, let's check the time."
        elif "☕" in semantic_meaning or "break" in meaning_lower:
            text = "Good idea! Let's take a short break."
        elif "📅" in semantic_meaning and "➡️" in semantic_meaning:
            text = "Yes, we'll continue this tomorrow. See you then!"
        elif "▶️" in semantic_meaning or "begin" in meaning_lower or "start" in meaning_lower:
            text = "Great! Let's begin. I'm ready to start."
        elif "⏹️" in semantic_meaning or "stop" in meaning_lower:
            text = "Okay, I'll stop now. Thank you for letting me know."
        elif "✅" in semantic_meaning or "done" in meaning_lower or "finish" in meaning_lower:
            text = "Excellent! You finished! Great work!"
        
        # Feedback and emotions
        elif "⭐" in semantic_meaning and "⭐" in semantic_meaning and "⭐" in semantic_meaning:
            text = "Wow! Excellent work! You're doing amazing!"
        elif "😊" in semantic_meaning or "happy" in meaning_lower:
            text = "I'm so glad you're feeling happy! That makes me happy too!"
        elif "😢" in semantic_meaning or "sad" in meaning_lower:
            text = "I'm sorry you're feeling sad. I'm here for you. Want to talk about it?"
        elif "😔" in semantic_meaning or "sorry" in meaning_lower:
            text = "It's okay. I understand. Thank you for telling me."
        elif "😰" in semantic_meaning or "worried" in meaning_lower:
            text = "It's okay to feel worried. Let's talk about what's bothering you."
        elif "🤔" in semantic_meaning or "thinking" in meaning_lower:
            text = "Take your time to think. I'm here if you need help."
        elif "😡" in semantic_meaning or "angry" in meaning_lower:
            text = "I can see you're upset. Let's talk about what's bothering you and find a solution."
        
        # Classroom management
        elif "👥" in semantic_meaning and "👥" in semantic_meaning:
            text = "Yes, let's work in groups. Find your partners!"
        elif "👥" in semantic_meaning or "class" in meaning_lower or "partner" in meaning_lower:
            text = "Good idea! Let's work together as a class."
        elif "➡️" in semantic_meaning and "➡️" in semantic_meaning and "➡️" in semantic_meaning:
            text = "Time to line up! Please form a line."
        elif "🧹" in semantic_meaning or "clean up" in meaning_lower:
            text = "Good thinking! Let's clean up our space."
        elif "📝" in semantic_meaning and "🏠" in semantic_meaning:
            text = "Yes, don't forget your homework! Complete it at home."
        elif "🔄" in semantic_meaning and "📚" in semantic_meaning:
            text = "Great idea! Let's review what we learned."
        
        # Basic needs
        elif "🚽" in semantic_meaning or "bathroom" in meaning_lower:
            text = "Of course, you may go to the bathroom. Come back when you're ready."
        elif "🍎" in semantic_meaning or "hungry" in meaning_lower:
            text = "I understand you're hungry. Let's get you something to eat soon."
        elif "💧" in semantic_meaning or "thirsty" in meaning_lower:
            text = "Let me get you some water right away. Stay hydrated!"
        elif "😴" in semantic_meaning or "tired" in meaning_lower:
            text = "You look tired. Would you like to take a short rest?"
        elif "🤒" in semantic_meaning or "sick" in meaning_lower:
            text = "I'm sorry you're not feeling well. Let me help you get some care."
        
        # Activities
        elif "📚" in semantic_meaning or "study" in meaning_lower:
            text = "Great! Let's study together. What subject would you like to focus on?"
        elif "🎨" in semantic_meaning or "art" in meaning_lower:
            text = "Art time! That sounds fun. What would you like to create?"
        elif "⚽" in semantic_meaning or "play" in meaning_lower:
            text = "Time to play! What game would you like to play?"
        elif "🏠" in semantic_meaning or "home" in meaning_lower:
            text = "I understand you want to go home. It won't be long now."
        elif "👨‍👩‍👧" in semantic_meaning or "family" in meaning_lower:
            text = "You're thinking about your family. They'll be here to pick you up soon."
        elif "❤️" in semantic_meaning or "love" in meaning_lower:
            text = "That's wonderful! I'm glad you feel that way. I care about you too!"
        elif "🎉" in semantic_meaning or "celebrate" in meaning_lower:
            text = "How exciting! Let's celebrate together! You deserve it!"
        
        # Pronouns and actions
        elif "👉" in semantic_meaning and "👥" in semantic_meaning:
            text = "You and your group? Yes, you can work together!"
        elif "👉" in semantic_meaning or "you" in meaning_lower:
            text = "Yes, I'm talking to you. What can I help you with?"
        elif "👈" in semantic_meaning or "me" in meaning_lower:
            text = "Yes, I hear you. Tell me what you need."
        elif "🤲" in semantic_meaning or "have" in meaning_lower or "need" in meaning_lower:
            text = "What do you need? I'm here to help you get it."
        elif "💪" in semantic_meaning or "can" in meaning_lower:
            text = "Yes, you can do it! I believe in you!"
        elif "➡️" in semantic_meaning or "go" in meaning_lower:
            text = "Yes, you may go. Come back when you're ready."
        elif "⬅️" in semantic_meaning or "come" in meaning_lower:
            text = "Yes, please come here. I'd like to talk with you."
        elif "👁️" in semantic_meaning or "show" in meaning_lower:
            text = "Yes, please show me! I'd love to see what you have."
        elif "💬" in semantic_meaning or "tell" in meaning_lower or "answer" in meaning_lower:
            text = "I'm listening. Please tell me what you're thinking."
        
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
