import uuid
from datetime import datetime
from typing import Dict, Any

class ClassroomSimulation:
    def __init__(self, coordinator, db):
        self.coordinator = coordinator
        self.db = db
        self.active_sessions = {}
    
    def start_session(self) -> str:
        session_id = str(uuid.uuid4())
        self.db.create_session(session_id, metadata={
            "type": "classroom_simulation",
            "entities": ["nonverbal_student", "verbal_teacher", "ai_system"]
        })
        
        self.active_sessions[session_id] = {
            "started_at": datetime.utcnow().isoformat(),
            "step_count": 0,
            "entities": {
                "student": {"name": "Student", "type": "nonverbal"},
                "teacher": {"name": "Teacher", "type": "verbal"},
                "ai": {"name": "Communication Bridge AI", "type": "system"}
            }
        }
        
        return session_id
    
    async def process_step(self, session_id: str, student_input: str) -> Dict[str, Any]:
        if session_id not in self.active_sessions:
            raise ValueError("Session not found or not started")
        
        session = self.active_sessions[session_id]
        session["step_count"] += 1
        
        # Simulate the communication flow
        steps = []
        
        # Step 1: Student sends input
        steps.append({
            "step": 1,
            "actor": "student",
            "action": "sends_input",
            "data": student_input,
            "timestamp": datetime.utcnow().isoformat()
        })
        
        # Step 2-6: AI system processes (coordinator handles this)
        steps.append({
            "step": 2,
            "actor": "ai_system",
            "action": "processing",
            "data": "Coordinator triggered, agents working...",
            "timestamp": datetime.utcnow().isoformat()
        })
        
        result = await self.coordinator.process_communication(
            input_text=student_input,
            user_type="nonverbal",
            session_id=session_id
        )
        
        # Step 7: Teacher receives output
        steps.append({
            "step": 3,
            "actor": "teacher",
            "action": "receives_message",
            "data": result["output"],
            "timestamp": datetime.utcnow().isoformat()
        })
        
        # Step 8: Log interaction
        steps.append({
            "step": 4,
            "actor": "ai_system",
            "action": "logged",
            "data": f"Interaction logged with intent: {result['intent']}",
            "timestamp": datetime.utcnow().isoformat()
        })
        
        return {
            "session_id": session_id,
            "step_number": session["step_count"],
            "simulation_steps": steps,
            "communication_result": result,
            "status": "completed"
        }
