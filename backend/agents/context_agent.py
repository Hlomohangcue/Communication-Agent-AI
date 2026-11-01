from typing import Dict, Any, Optional, List
from datetime import datetime


class ContextAgent:
    def __init__(self, db):
        self.db = db
        self.session_contexts = {}

    @staticmethod
    def _context_key(session_id: str, user_id: str) -> str:
        return f"{user_id}:{session_id}"

    def get_context(self, session_id: str, user_id: str, limit: int = 6) -> Optional[Dict[str, Any]]:
        key = self._context_key(session_id, user_id)
        messages = self.db.get_messages(session_id, user_id, limit=limit)
        if not messages:
            return None

        ordered_messages = list(reversed(messages))
        context = {
            "recent_messages": ordered_messages,
            "summary": self._summarize_messages(ordered_messages),
            "limit": limit,
            "session_id": session_id,
            "user_id": user_id,
        }
        self.session_contexts[key] = context
        return context

    def update_context(self, session_id: str, user_id: str, interaction: Dict[str, Any]):
        key = self._context_key(session_id, user_id)
        if key not in self.session_contexts:
            self.session_contexts[key] = {
                "interactions": [],
                "patterns": {},
                "created_at": datetime.utcnow().isoformat(),
                "limit": 6,
            }

        context = self.session_contexts[key]
        context["interactions"].append({
            "timestamp": datetime.utcnow().isoformat(),
            "input": interaction.get("input"),
            "intent": interaction.get("intent", {}).get("intent"),
            "output": interaction.get("output", {}).get("text"),
        })

        if len(context["interactions"]) > 10:
            context["interactions"] = context["interactions"][-10:]

        intent = interaction.get("intent", {}).get("intent")
        if intent:
            context["patterns"][intent] = context["patterns"].get(intent, 0) + 1

    def _summarize_messages(self, messages: List[Dict[str, Any]]) -> str:
        if not messages:
            return ""

        pairs = []
        for message in messages:
            input_text = (message.get("input_text") or "").strip()
            output_text = (message.get("output_text") or "").strip()
            if input_text and output_text:
                pairs.append(f"User: {input_text}. Assistant: {output_text}.")

        intents = [m.get("intent", "unknown") for m in messages]
        most_common = max(set(intents), key=intents.count) if intents else "unknown"
        summary = " ".join(pairs[-4:]) if pairs else "No prior messages."
        return f"Recent conversation context: {summary} Common intent: {most_common}."
