from pydantic import BaseModel
from typing import Optional, Dict, Any
from datetime import datetime

class Session(BaseModel):
    id: str
    created_at: datetime
    metadata: Optional[Dict[str, Any]] = {}
    status: str = "active"

class Message(BaseModel):
    id: Optional[int] = None
    session_id: str
    input_text: str
    output_text: str
    intent: str
    created_at: datetime

class AgentLog(BaseModel):
    id: Optional[int] = None
    session_id: str
    agent_name: str
    action: str
    data: Dict[str, Any]
    created_at: datetime

class Gesture(BaseModel):
    id: Optional[int] = None
    emoji: str
    name: str
    category: str
    asl_equivalent: Optional[str] = None
    description: Optional[str] = None
    usage_count: int = 0

class Phrase(BaseModel):
    id: Optional[int] = None
    text: str
    category: str
    gesture_sequence: Optional[str] = None
    is_custom: bool = False
    usage_count: int = 0

class GestureSequence(BaseModel):
    id: Optional[int] = None
    session_id: str
    source_text: str
    gesture_sequence: str
    method: str  # 'phrase_match', 'keyword_match', 'ai_translation'
    created_at: datetime
