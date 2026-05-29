"""
LangGraph 状态定义
定义 Agent 图中流转的 State 结构和字段
"""

from typing import Annotated, Any, Literal, Optional, Sequence

from langgraph.graph.message import add_messages
from pydantic import BaseModel, Field


class MessageMetadata(BaseModel):
    """消息元数据"""
    token_count: Optional[int] = None
    latency_ms: Optional[float] = None


class SafetyCheck(BaseModel):
    """安全校验结果"""
    safe: bool = True
    risk_level: Literal["none", "low", "medium", "high", "critical"] = "none"
    warnings: list[str] = Field(default_factory=list)
    disclaimer_required: bool = False


class KnowledgeSource(BaseModel):
    """知识检索来源"""
    title: str = ""
    url: str = ""
    snippet: str = ""
    source_type: Literal["academic", "clinical", "web", "reference"] = "web"
    relevance_score: float = 0.0


class AgentState(BaseModel):
    """
    Agent 图的核心状态
    在 LangGraph 节点间流转，通过 TypedDict 兼容 LangGraph API
    """

    # ── 对话 ──
    session_id: str = ""
    user_message: str = ""
    messages: Annotated[list, add_messages] = Field(default_factory=list)

    # ── 意图路由 ──
    intent: Literal["medical", "general", "clarify", "emergency"] = "general"
    symptom_severity: Literal["mild", "moderate", "severe", "critical"] = "mild"

    # ── 知识检索 ──
    search_queries: list[str] = Field(default_factory=list)
    knowledge_results: list[KnowledgeSource] = Field(default_factory=list)
    academic_results: list[KnowledgeSource] = Field(default_factory=list)

    # ── 反思 & 验证 ──
    cross_validation_passed: bool = False
    hallucination_checked: bool = False
    final_response: str = ""

    # ── 安全 ──
    safety: SafetyCheck = Field(default_factory=SafetyCheck)

    # ── 元数据 ──
    metadata: dict[str, Any] = Field(default_factory=dict)
    error: Optional[str] = None


def create_initial_state(session_id: str, user_message: str) -> AgentState:
    """创建初始 Agent 状态"""
    return AgentState(
        session_id=session_id,
        user_message=user_message,
        messages=[],
    )
