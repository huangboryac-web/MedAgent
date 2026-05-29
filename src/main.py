"""
MedAgent 核心入口 - FastAPI 应用
"""

from contextlib import asynccontextmanager

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from src.api.routes.chat import router as chat_router
from src.config import get_settings
from src.utils.logger import logger

settings = get_settings()


@asynccontextmanager
async def lifespan(app: FastAPI):
    """应用生命周期管理"""
    logger.info(f"MedAgent 启动中... 环境: {settings.app_env}")
    yield
    logger.info("MedAgent 关闭中...")


app = FastAPI(
    title="MedAgent API Edition",
    description="专业个人 AI 医生 Agent - 基于 LangGraph 智能体编排",
    version="0.1.0",
    lifespan=lifespan,
)

# CORS 中间件
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"] if settings.app_env == "development" else [],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# 注册路由
app.include_router(chat_router)


@app.get("/health")
async def health_check():
    """健康检查接口"""
    return {"status": "ok", "env": settings.app_env}
