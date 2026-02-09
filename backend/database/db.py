import sqlite3
import json
from datetime import datetime
from typing import Dict, Any, Optional, List
import os

class Database:
    def __init__(self, db_path: str = "communication_bridge.db"):
        self.db_path = db_path
        self.init_db()
    
    def init_db(self):
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        
        # Sessions table
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS sessions (
                id TEXT PRIMARY KEY,
                created_at TEXT NOT NULL,
                metadata TEXT,
                status TEXT DEFAULT 'active'
            )
        """)
        
        # Messages table
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS messages (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                session_id TEXT NOT NULL,
                input_text TEXT NOT NULL,
                output_text TEXT NOT NULL,
                intent TEXT,
                created_at TEXT NOT NULL,
                FOREIGN KEY (session_id) REFERENCES sessions(id)
            )
        """)
        
        # Agent logs table
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS agent_logs (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                session_id TEXT NOT NULL,
                agent_name TEXT NOT NULL,
                action TEXT NOT NULL,
                data TEXT,
                created_at TEXT NOT NULL,
                FOREIGN KEY (session_id) REFERENCES sessions(id)
            )
        """)
        
        conn.commit()
        conn.close()
    
    def create_session(self, session_id: str, metadata: Optional[Dict] = None):
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        cursor.execute(
            "INSERT INTO sessions (id, created_at, metadata) VALUES (?, ?, ?)",
            (session_id, datetime.utcnow().isoformat(), json.dumps(metadata or {}))
        )
        conn.commit()
        conn.close()
    
    def get_session(self, session_id: str) -> Optional[Dict]:
        conn = sqlite3.connect(self.db_path)
        conn.row_factory = sqlite3.Row
        cursor = conn.cursor()
        cursor.execute("SELECT * FROM sessions WHERE id = ?", (session_id,))
        row = cursor.fetchone()
        conn.close()
        
        if row:
            return {
                "id": row["id"],
                "created_at": row["created_at"],
                "metadata": json.loads(row["metadata"]),
                "status": row["status"]
            }
        return None
    
    def get_recent_sessions(self, limit: int = 20) -> List[Dict]:
        conn = sqlite3.connect(self.db_path)
        conn.row_factory = sqlite3.Row
        cursor = conn.cursor()
        cursor.execute(
            "SELECT * FROM sessions ORDER BY created_at DESC LIMIT ?",
            (limit,)
        )
        rows = cursor.fetchall()
        conn.close()
        
        return [
            {
                "id": row["id"],
                "created_at": row["created_at"],
                "metadata": json.loads(row["metadata"]),
                "status": row["status"]
            }
            for row in rows
        ]
    
    def store_message(self, session_id: str, input_text: str, output_text: str, intent: str):
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        cursor.execute(
            "INSERT INTO messages (session_id, input_text, output_text, intent, created_at) VALUES (?, ?, ?, ?, ?)",
            (session_id, input_text, output_text, intent, datetime.utcnow().isoformat())
        )
        conn.commit()
        conn.close()
    
    def get_messages(self, session_id: str, limit: int = 50) -> List[Dict]:
        conn = sqlite3.connect(self.db_path)
        conn.row_factory = sqlite3.Row
        cursor = conn.cursor()
        cursor.execute(
            "SELECT * FROM messages WHERE session_id = ? ORDER BY created_at DESC LIMIT ?",
            (session_id, limit)
        )
        rows = cursor.fetchall()
        conn.close()
        
        return [
            {
                "id": row["id"],
                "session_id": row["session_id"],
                "input_text": row["input_text"],
                "output_text": row["output_text"],
                "intent": row["intent"],
                "created_at": row["created_at"]
            }
            for row in rows
        ]
    
    def log_agent_action(self, session_id: str, agent_name: str, action: str, data: Dict[str, Any]):
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        cursor.execute(
            "INSERT INTO agent_logs (session_id, agent_name, action, data, created_at) VALUES (?, ?, ?, ?, ?)",
            (session_id, agent_name, action, json.dumps(data), datetime.utcnow().isoformat())
        )
        conn.commit()
        conn.close()
    
    def get_agent_logs(self, session_id: Optional[str] = None, limit: int = 50) -> List[Dict]:
        conn = sqlite3.connect(self.db_path)
        conn.row_factory = sqlite3.Row
        cursor = conn.cursor()
        
        if session_id:
            cursor.execute(
                "SELECT * FROM agent_logs WHERE session_id = ? ORDER BY created_at DESC LIMIT ?",
                (session_id, limit)
            )
        else:
            cursor.execute(
                "SELECT * FROM agent_logs ORDER BY created_at DESC LIMIT ?",
                (limit,)
            )
        
        rows = cursor.fetchall()
        conn.close()
        
        return [
            {
                "id": row["id"],
                "session_id": row["session_id"],
                "agent_name": row["agent_name"],
                "action": row["action"],
                "data": json.loads(row["data"]),
                "created_at": row["created_at"]
            }
            for row in rows
        ]
