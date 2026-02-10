from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from fastapi.staticfiles import StaticFiles
from pydantic import BaseModel
from typing import Optional, Dict, Any
import uvicorn
from datetime import datetime

from coordinator.orchestrator import Coordinator
from simulation.classroom_sim import ClassroomSimulation
from database.db import Database
from agents.gesture_agent import GestureAgent

app = FastAPI(title="Communication Bridge AI")

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

db = Database()
db.init_gesture_tables()  # Initialize gesture tables
coordinator = Coordinator(db)
simulation = ClassroomSimulation(coordinator, db)
gesture_agent = GestureAgent()

class CommunicateRequest(BaseModel):
    input_text: str
    user_type: str = "nonverbal"
    session_id: Optional[str] = None

class SimulationStepRequest(BaseModel):
    session_id: str
    input_text: str

class TextToGestureRequest(BaseModel):
    text: str
    session_id: Optional[str] = None

class AddPhraseRequest(BaseModel):
    text: str
    category: str
    gesture_sequence: Optional[str] = None

@app.get("/")
async def root():
    return {"status": "Communication Bridge AI is running", "version": "1.0.0"}

@app.post("/simulate/start")
async def start_simulation():
    session_id = simulation.start_session()
    return {
        "session_id": session_id,
        "status": "started",
        "message": "Classroom simulation initialized"
    }

@app.post("/simulate/step")
async def simulation_step(request: SimulationStepRequest):
    result = await simulation.process_step(request.session_id, request.input_text)
    return result

@app.post("/communicate")
async def communicate(request: CommunicateRequest):
    result = await coordinator.process_communication(
        input_text=request.input_text,
        user_type=request.user_type,
        session_id=request.session_id
    )
    return result

@app.get("/logs")
async def get_logs(session_id: Optional[str] = None, limit: int = 50):
    logs = db.get_agent_logs(session_id, limit)
    return {"logs": logs}

@app.get("/session/{session_id}")
async def get_session(session_id: str):
    session = db.get_session(session_id)
    if not session:
        raise HTTPException(status_code=404, detail="Session not found")
    messages = db.get_messages(session_id)
    return {"session": session, "messages": messages}

@app.get("/sessions")
async def list_sessions(limit: int = 20):
    sessions = db.get_recent_sessions(limit)
    return {"sessions": sessions}

# Gesture Translation Endpoints

@app.post("/translate/text-to-gesture")
async def translate_text_to_gesture(request: TextToGestureRequest):
    """Convert text to gesture sequence for non-verbal users"""
    try:
        result = gesture_agent.text_to_gestures(request.text)
        
        # Store in database if session provided
        if request.session_id:
            db.store_gesture_sequence(
                session_id=request.session_id,
                source_text=request.text,
                gesture_sequence=result["gesture_sequence"],
                method=result["method"]
            )
        
        return {
            "success": True,
            **result
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@app.get("/gestures")
async def get_gestures():
    """Get all available gestures"""
    return {
        "gestures": gesture_agent.get_gesture_library(),
        "by_category": gesture_agent.get_gestures_by_category()
    }

@app.get("/phrases")
async def get_phrases(category: Optional[str] = None):
    """Get common phrases, optionally filtered by category"""
    # Get from database
    db_phrases = db.get_phrases(category)
    
    # Also include built-in phrases
    common_phrases = gesture_agent.get_common_phrases()
    
    return {
        "common_phrases": common_phrases,
        "custom_phrases": db_phrases,
        "categories": ["greetings", "questions", "needs", "responses", "classroom"]
    }

@app.post("/phrases/custom")
async def add_custom_phrase(request: AddPhraseRequest):
    """Add a custom phrase to the library"""
    try:
        db.add_phrase(
            text=request.text,
            category=request.category,
            gesture_sequence=request.gesture_sequence,
            is_custom=True
        )
        return {"success": True, "message": "Phrase added successfully"}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@app.get("/gesture-history/{session_id}")
async def get_gesture_history(session_id: str, limit: int = 50):
    """Get gesture translation history for a session"""
    history = db.get_gesture_sequences(session_id, limit)
    return {"history": history}

if __name__ == "__main__":
    uvicorn.run(app, host="0.0.0.0", port=8000)
