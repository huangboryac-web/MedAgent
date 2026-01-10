import uvicorn
from contextlib import asynccontextmanager
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from logger import get_logger
from config import get_settings
from database.db import init_chat_db
from constants import REDIS_HOST, REDIS_PORT, APP_TITLE, WEBSITE_HOST
from routers import session, history, chat
from agents.workflow import init_workflow

logger = get_logger("API")
settings = get_settings()

@asynccontextmanager
async def lifespan(app: FastAPI):
    logger.info("🚀 Starting Medical Agent API...")
    init_chat_db()
    
    async with init_workflow() as saver:
        logger.info("✅ Redis Checkpointer Connected & Graph Compiled")
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