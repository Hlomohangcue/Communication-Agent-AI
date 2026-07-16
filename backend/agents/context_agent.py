from typing import Dict, Any, Optional
from datetime import datetime

class ContextAgent:
    def __init__(self, db):
        self.db = db
        self.session_contexts = {}

    @staticmethod
    def _context_key(session_id: str, user_id: str) -> str:
        return f"{user_id}:{session_id}"
    
    def get_context(self, session_id: str, user_id: str) -> Optional[Dict[str, Any]]:
        key = self._context_key(session_id, user_id)
        if key in self.session_contexts:
            return self.session_contexts[key]
        
        # Load from database
        messages = self.db.get_messages(session_id, user_id, limit=5)
        if messages:
            return {
                "recent_messages": messages,
                "summary": self._summarize_messages(messages)
            }
        return None
    
    def update_context(self, session_id: str, user_id: str, interaction: Dict[str, Any]):
        key = self._context_key(session_id, user_id)
        if key not in self.session_contexts:
            self.session_contexts[key] = {
                "interactions": [],
                "patterns": {},
                "created_at": datetime.utcnow().isoformat()
            }
        
        context = self.session_contexts[key]
        context["interactions"].append({
            "timestamp": datetime.utcnow().isoformat(),
            "input": interaction.get("input"),
            "intent": interaction.get("intent", {}).get("intent"),
            "output": interaction.get("output", {}).get("text")
        })
        
        # Keep only last 10 interactions in memory
        if len(context["interactions"]) > 10:
            context["interactions"] = context["interactions"][-10:]
        
        # Track intent patterns
        intent = interaction.get("intent", {}).get("intent")
        if intent:
            context["patterns"][intent] = context["patterns"].get(intent, 0) + 1
    
    def _summarize_messages(self, messages: list) -> str:
        if not messages:
            return ""
        
        intents = [m.get("intent", "unknown") for m in messages]
        most_common = max(set(intents), key=intents.count) if intents else "unknown"
        
        return f"Recent conversation with {len(messages)} messages. Common intent: {most_common}"
