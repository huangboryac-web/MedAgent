import json
import uuid 
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from redis import Redis

from logger import get_logger
from database.db import get_all_sessions, get_chat_by_session_id, init_chat_db, insert_chat_by_session_id
from models import ChatRequest
from constants import WEBSITE_HOST, APP_TITLE, TEST, REDIS_HOST, REDIS_PORT, REDIS_CHAT_CACHE, CACHE_TTL

logger = get_logger("API")

chat_cache = Redis(host=REDIS_HOST, port=REDIS_PORT, db=REDIS_CHAT_CACHE, decode_responses=True)

app = FastAPI(title=APP_TITLE)

app.add_middleware(
    CORSMiddleware,
    allow_origins=[WEBSITE_HOST],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

init_chat_db()

@app.get("/session")
async def create_session():
    session_id = str(uuid.uuid4())
    logger.info(f"Created new session: {session_id}")
    return {"session_id": session_id}

@app.get("/sessions")
async def get_sessions_endpoint():
    sessions = get_all_sessions()
    return sessions

@app.get("/history/{session_id}")
async def get_history(session_id: str):
    cache_key = f"history:{session_id}"

    cached_data = chat_cache.get(cache_key)
    if cached_data:
        logger.info(f"Cache Hit: {session_id}")
        return json.loads(cached_data)

    logger.info(f"Cache Miss (SQLite): {session_id}")
    rows = get_chat_by_session_id(session_id)
    data = [dict(row) for row in rows]
    chat_cache.setex(cache_key, CACHE_TTL, json.dumps(data))
    return data

@app.post("/chat") 
async def chat_endpoint(request: ChatRequest):
    chat_cache.delete(f"history:{request.session_id}")
    logger.debug(f"Invalidated cache for session: {request.session_id}")

    insert_chat_by_session_id(request.session_id, request.query, "user")
    logger.info(f"Received Query [{request.session_id}]: {request.query}")

    try:
        result = {
            "generation": "Result"
        }
        answer = result.get("generation", "Error.")
    except Exception as e:
        logger.error(f"Error processing chat request: {str(e)}", exc_info=True)
        answer = f"System Error: {str(e)}"

    insert_chat_by_session_id(request.session_id, answer, "assistant")
    
    return {"response": answer}


if __name__ == "__main__":
    import uvicorn
    uvicorn.run("main:app", port=8000, reload=TEST)