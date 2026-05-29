"""
聊天 API 路由
提供 SSE 流式对话接口
"""

import asyncio
import uuid
from typing import Optional

from fastapi import APIRouter, HTTPException
from pydantic import BaseModel, Field
from sse_starlette.sse import EventSourceResponse

from src.agent.graph import MedAgentGraph
from src.agent.state import AgentState
from src.utils.logger import logger

router = APIRouter(prefix="/api/v1/chat", tags=["chat"])


# ── 请求/响应模型 ──

class ChatRequest(BaseModel):
    message: str = Field(..., min_length=1, max_length=5000, description="用户输入文本")
    session_id: Optional[str] = Field(default=None, description="会话 ID，不传则新建")


class ChatMessage(BaseModel):
    role: str
    content: str


class ChatResponse(BaseModel):
    session_id: str
    response: str
    safety_warnings: list[str] = Field(default_factory=list)


# ── 路由 ──

@router.post("/send", response_model=ChatResponse)
async def send_message(req: ChatRequest) -> ChatResponse:
    """非流式对话接口"""
    session_id = req.session_id or str(uuid.uuid4())

    try:
        graph = MedAgentGraph()
        result = await graph.run(session_id=session_id, user_message=req.message)
        return ChatResponse(
            session_id=session_id,
            response=result.get("final_response", ""),
            safety_warnings=result.get("safety", {}).get("warnings", []),
        )
    except Exception as e:
        logger.error(f"对话处理失败: {e}")
        raise HTTPException(status_code=500, detail="服务器内部错误")


@router.post("/stream")
async def stream_chat(req: ChatRequest):
    """SSE 流式对话接口"""
    session_id = req.session_id or str(uuid.uuid4())

    async def event_generator():
        try:
            graph = MedAgentGraph()
            async for event in graph.stream(session_id=session_id, user_message=req.message):
                yield {"event": event.get("type", "message"), "data": event.get("payload", "")}
        except Exception as e:
            logger.error(f"流式对话异常: {e}")
            yield {"event": "error", "data": "服务器内部错误"}

    return EventSourceResponse(event_generator())
