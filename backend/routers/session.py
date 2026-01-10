import uuid
from fastapi import APIRouter

from logger import get_logger
from database.db import get_all_sessions, delete_chat_by_session_id

router = APIRouter()
logger = get_logger("Router:Session")

@router.get("/session")
async def create_session():
    sid = str(uuid.uuid4())
    logger.info(f"New Session Created: {sid}")
    return {"session_id": sid}

@router.get("/sessions")
async def get_sessions_route():
    return get_all_sessions()

@router.delete("/session/{session_id}")
async def delete_session_route(session_id: str):
    delete_chat_by_session_id(session_id)
    return {"status": "success", "message": f"Session {session_id} deleted"}