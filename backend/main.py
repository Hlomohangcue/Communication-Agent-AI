from fastapi import FastAPI, HTTPException, Depends, Header
from fastapi.middleware.cors import CORSMiddleware
from fastapi.staticfiles import StaticFiles
from pydantic import BaseModel
from typing import Optional, Dict, Any
import uvicorn
from datetime import datetime
import uuid

from coordinator.orchestrator import Coordinator
from simulation.classroom_sim import ClassroomSimulation
from database.db import Database
from agents.gesture_agent import GestureAgent
from auth.auth_handler import AuthHandler
from services.vision_service import VisionService

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
auth_handler = AuthHandler()
vision_service = VisionService()  # Initialize vision service

# Authentication dependency
async def get_current_user(authorization: Optional[str] = Header(None)):
    if not authorization:
        raise HTTPException(status_code=401, detail="Not authenticated")
    
    try:
        scheme, token = authorization.split()
        if scheme.lower() != 'bearer':
            raise HTTPException(status_code=401, detail="Invalid authentication scheme")
        
        payload = auth_handler.decode_token(token)
        if not payload:
            raise HTTPException(status_code=401, detail="Invalid or expired token")
        
        user_id = payload.get("sub")
        user = db.get_user_by_id(user_id)
        
        if not user or not user.get("is_active"):
            raise HTTPException(status_code=401, detail="User not found or inactive")
        
        return user
    except ValueError:
        raise HTTPException(status_code=401, detail="Invalid authorization header")

class SignupRequest(BaseModel):
    name: str
    email: str
    password: str

class LoginRequest(BaseModel):
    email: str
    password: str

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

class SaveMessageRequest(BaseModel):
    session_id: str
    input_text: str
    output_text: str
    intent: str = "manual_save"
    confidence: float = 1.0

class ProcessFrameRequest(BaseModel):
    frame: str  # Base64 encoded image
    session_id: Optional[str] = None

@app.get("/")
async def root():
    return {"status": "Communication Bridge AI is running", "version": "1.0.0"}

# Authentication Endpoints

@app.post("/auth/signup")
async def signup(request: SignupRequest):
    """Create a new user account"""
    # Check if user already exists
    existing_user = db.get_user_by_email(request.email)
    if existing_user:
        raise HTTPException(status_code=400, detail="Email already registered")
    
    # Hash password
    password_hash = auth_handler.hash_password(request.password)
    
    # Create user
    user_id = str(uuid.uuid4())
    db.create_user(user_id, request.email, request.name, password_hash)
    
    return {
        "message": "User created successfully",
        "user": {
            "id": user_id,
            "email": request.email,
            "name": request.name,
            "credits": 100
        }
    }

@app.post("/auth/login")
async def login(request: LoginRequest):
    """Login and get access token"""
    # Get user
    user = db.get_user_by_email(request.email)
    if not user:
        raise HTTPException(status_code=401, detail="Invalid email or password")
    
    # Verify password
    if not auth_handler.verify_password(request.password, user["password_hash"]):
        raise HTTPException(status_code=401, detail="Invalid email or password")
    
    # Update last login
    db.update_last_login(user["id"])
    
    # Create access token
    token = auth_handler.create_access_token({"sub": user["id"]})
    
    return {
        "token": token,
        "user": {
            "id": user["id"],
            "email": user["email"],
            "name": user["name"],
            "plan": user["plan"],
            "credits": user["credits"]
        }
    }

@app.get("/auth/verify")
async def verify_token(current_user: dict = Depends(get_current_user)):
    """Verify if token is valid"""
    return {
        "valid": True,
        "user": current_user
    }

@app.get("/auth/me")
async def get_current_user_info(current_user: dict = Depends(get_current_user)):
    """Get current user information"""
    return current_user

@app.get("/auth/credits")
async def get_credits(current_user: dict = Depends(get_current_user)):
    """Get user's remaining credits"""
    credits = db.get_user_credits(current_user["id"])
    return {
        "credits": credits,
        "plan": current_user["plan"]
    }

@app.post("/simulate/start")
async def start_simulation(current_user: dict = Depends(get_current_user)):
    session_id = simulation.start_session()
    return {
        "session_id": session_id,
        "status": "started",
        "message": "Classroom simulation initialized",
        "user_credits": db.get_user_credits(current_user["id"])
    }

@app.post("/simulate/step")
async def simulation_step(request: SimulationStepRequest, current_user: dict = Depends(get_current_user)):
    # Check if user has credits (unless they're on pro plan)
    if current_user["plan"] == "free":
        credits = db.get_user_credits(current_user["id"])
        if credits < 1:
            raise HTTPException(
                status_code=402,
                detail="Insufficient credits. Please upgrade to Pro plan for unlimited messages."
            )
        
        # Use 1 credit
        if not db.use_credits(current_user["id"], 1, request.session_id, "message"):
            raise HTTPException(status_code=402, detail="Failed to deduct credits")
    
    result = await simulation.process_step(request.session_id, request.input_text)
    
    # Add remaining credits to response
    remaining_credits = db.get_user_credits(current_user["id"])
    result["user_credits"] = remaining_credits
    
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

@app.post("/save_message")
async def save_message(request: SaveMessageRequest):
    """Save a message directly to the database (for verbal-to-nonverbal mode)"""
    try:
        db.store_message(
            session_id=request.session_id,
            input_text=request.input_text,
            output_text=request.output_text,
            intent=request.intent,
            confidence=request.confidence
        )
        return {"success": True, "message": "Message saved successfully"}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

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

# Computer Vision Endpoints

@app.post("/vision/process-frame")
async def process_frame(request: ProcessFrameRequest):
    """Process a webcam frame and detect gestures"""
    result = vision_service.process_frame(request.frame)
    
    # If gestures detected and session provided, store them
    if request.session_id and result.get("emojis"):
        emoji_text = " ".join(result["emojis"])
        # You can store this in database if needed
    
    return result

@app.get("/vision/gestures")
async def get_supported_gestures():
    """Get list of supported gestures"""
    return {
        "gestures": vision_service.get_supported_gestures()
    }

@app.post("/vision/gesture-to-text")
async def gesture_to_text(request: ProcessFrameRequest, current_user: dict = Depends(get_current_user)):
    """
    Process frame, detect gesture, and generate AI response
    Complete flow: Webcam → Gesture → Emoji → AI Response
    """
    # Process frame
    vision_result = vision_service.process_frame(request.frame)
    
    if not vision_result.get("emojis"):
        return {
            "success": False,
            "message": "No gestures detected",
            "vision_result": vision_result
        }
    
    # Convert emojis to text
    emoji_input = " ".join(vision_result["emojis"])
    
    # Process through communication pipeline
    comm_result = await coordinator.process_communication(
        input_text=emoji_input,
        user_type="nonverbal",
        session_id=request.session_id
    )
    
    return {
        "success": True,
        "vision_result": vision_result,
        "communication_result": comm_result,
        "detected_gestures": vision_result["gestures"],
        "emojis": vision_result["emojis"],
        "ai_response": comm_result.get("output", {}).get("text", "")
    }

if __name__ == "__main__":
    uvicorn.run(app, host="0.0.0.0", port=8000)
