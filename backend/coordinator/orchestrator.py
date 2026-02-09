import uuid
from datetime import datetime
from typing import Dict, Any, Optional

from agents.intent_agent import IntentAgent
from agents.nonverbal_agent import NonVerbalAgent
from agents.speech_agent import SpeechAgent
from agents.context_agent import ContextAgent

class Coordinator:
    def __init__(self, db):
        self.db = db
        self.intent_agent = IntentAgent()
        self.nonverbal_agent = NonVerbalAgent()
        self.speech_agent = SpeechAgent()
        self.context_agent = ContextAgent(db)
        self.confidence_threshold = 0.7
    
    async def process_communication(
        self, 
        input_text: str, 
        user_type: str = "nonverbal",
        session_id: Optional[str] = None
    ) -> Dict[str, Any]:
        if not session_id:
            session_id = str(uuid.uuid4())
            self.db.create_session(session_id)
        
        workflow = []
        
        # Step 1: Non-verbal interpretation
        self._log_agent_action(session_id, "nonverbal_agent", "started", {"input": input_text})
        interpretation = await self.nonverbal_agent.interpret(input_text)
        workflow.append({"agent": "nonverbal_agent", "result": interpretation})
        self._log_agent_action(session_id, "nonverbal_agent", "completed", interpretation)
        
        # Step 2: Intent detection
        self._log_agent_action(session_id, "intent_agent", "started", {"interpreted": interpretation})
        intent_result = await self.intent_agent.detect_intent(interpretation["semantic_meaning"])
        workflow.append({"agent": "intent_agent", "result": intent_result})
        self._log_agent_action(session_id, "intent_agent", "completed", intent_result)
        
        # Step 3: Check confidence and retry if needed
        if intent_result["confidence"] < self.confidence_threshold:
            self._log_agent_action(session_id, "coordinator", "retry", {
                "reason": "low_confidence",
                "confidence": intent_result["confidence"]
            })
            # Retry with context
            context = self.context_agent.get_context(session_id)
            intent_result = await self.intent_agent.detect_intent(
                interpretation["semantic_meaning"],
                context=context
            )
            workflow.append({"agent": "intent_agent_retry", "result": intent_result})
        
        # Step 4: Generate speech/text output
        self._log_agent_action(session_id, "speech_agent", "started", {"intent": intent_result})
        output = await self.speech_agent.generate_output(
            intent=intent_result["intent"],
            semantic_meaning=interpretation["semantic_meaning"],
            confidence=intent_result["confidence"]
        )
        workflow.append({"agent": "speech_agent", "result": output})
        self._log_agent_action(session_id, "speech_agent", "completed", output)
        
        # Step 5: Update context
        self.context_agent.update_context(session_id, {
            "input": input_text,
            "interpretation": interpretation,
            "intent": intent_result,
            "output": output
        })
        
        # Store message
        self.db.store_message(session_id, input_text, output["text"], intent_result["intent"])
        
        return {
            "session_id": session_id,
            "input": input_text,
            "output": output["text"],
            "intent": intent_result["intent"],
            "confidence": intent_result["confidence"],
            "workflow": workflow,
            "timestamp": datetime.utcnow().isoformat()
        }
    
    def _log_agent_action(self, session_id: str, agent_name: str, action: str, data: Dict[str, Any]):
        self.db.log_agent_action(session_id, agent_name, action, data)
