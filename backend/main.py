import uvicorn
from contextlib import asynccontextmanager
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from redis import Redis

from logger import get_logger
from config import get_settings
from database.db import init_chat_db
from constants import REDIS_HOST, REDIS_PORT, APP_TITLE, WEBSITE_HOST
from routers import session, history, chat

logger = get_logger("API")
settings = get_settings()

@asynccontextmanager
async def lifespan(app: FastAPI):
    logger.info("🚀 Starting Medical Agent API...")
    init_chat_db()
    
    try:
        r = Redis(host=REDIS_HOST, port=REDIS_PORT)
        r.ping()
        logger.info(f"✅ Redis Connected: {REDIS_HOST}")
        r.close()
    except Exception as e:
        logger.warning(f"⚠️ Redis Connection Failed: {e}. Session caching may be degraded.")
    
    yield
    
    logger.info("🛑 Shutting down...")

app = FastAPI(title=APP_TITLE, lifespan=lifespan)


app.add_middleware(
    CORSMiddleware,
    allow_origins=[WEBSITE_HOST],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

app.include_router(session.router)
app.include_router(history.router)
app.include_router(chat.router)

if __name__ == "__main__":
    uvicorn.run("main:app", port=8000, reload=settings.test, log_level="info")