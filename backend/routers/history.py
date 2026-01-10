from fastapi import APIRouter

from database.db import get_chat_by_session_id

router = APIRouter()

@router.get("/history/{session_id}")
async def get_history_route(session_id: str):
    rows = get_chat_by_session_id(session_id)
    return [dict(row) for row in rows]