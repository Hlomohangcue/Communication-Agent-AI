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

app = FastAPI(title="Communication Bridge AI")

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

db = Database()
coordinator = Coordinator(db)
simulation = ClassroomSimulation(coordinator, db)

class CommunicateRequest(BaseModel):
    input_text: str
    user_type: str = "nonverbal"
    session_id: Optional[str] = None

class SimulationStepRequest(BaseModel):
    session_id: str
    input_text: str

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

if __name__ == "__main__":
    uvicorn.run(app, host="0.0.0.0", port=8000)
