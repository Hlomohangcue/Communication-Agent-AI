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
