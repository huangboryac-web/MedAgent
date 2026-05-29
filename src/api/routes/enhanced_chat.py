"""
Phase 3: 增强型 API 路由
集成用户认证和外部 Skill
"""

import asyncio
import json
from datetime import datetime, timezone
from typing import Optional

from fastapi import APIRouter, Depends, HTTPException, Query, Request, status
from pydantic import BaseModel, Field
from sse_starlette.sse import EventSourceResponse

from src.agent.state import create_initial_state
from src.agent.enhanced_graph import compiled_base_graph, compiled_enhanced_graph
from src.knowledge.enhanced_retriever import EnhancedKnowledgeRetriever
from src.skills.integration import skill_integration
from src.utils.auth import auth_service, rate_limiter, verify_api_key
from src.utils.conversation import get_or_create_session
from src.utils.logger import logger
from src.utils.safety import safety_guardrail

router = APIRouter(prefix="/api/v2", tags=["Enhanced API v2"])


class ChatRequest(BaseModel):
    """聊天请求"""
    message: str = Field(..., description="用户消息")
    session_id: Optional[str] = Field(None, description="会话 ID")
    user_context: Optional[dict] = Field(None, description="用户上下文信息")
    enable_skills: bool = Field(True, description="是否启用外部 Skill")
    enable_enhanced_search: bool = Field(True, description="是否启用增强检索")


class ChatResponse(BaseModel):
    """聊天响应"""
    session_id: str
    response: str
    intent: str
    risk_level: str
    requires_disclaimer: bool
    knowledge_sources: int
    timestamp: str


class HealthRecordRequest(BaseModel):
    """健康记录请求"""
    user_id: str
    temperature: Optional[float] = None
    heart_rate: Optional[int] = None
    blood_pressure_sys: Optional[int] = None
    blood_pressure_dia: Optional[int] = None
    blood_sugar: Optional[float] = None
    weight: Optional[float] = None
    symptoms: Optional[str] = None


class DrugCheckRequest(BaseModel):
    """药物检查请求"""
    drugs: list[str] = Field(..., description="药物列表")
    conditions: list[str] = Field(default_factory=list, description="已有疾病")


@router.get("/health")
async def health_check():
    """健康检查"""
    return {
        "status": "healthy",
        "version": "2.0.0",
        "timestamp": datetime.now(timezone.utc).isoformat(),
    }


@router.post("/chat/send", response_model=ChatResponse)
async def chat_send(
    chat_request: ChatRequest,
    request: Request,
    user_info: tuple = Depends(verify_api_key),
):
    """
    发送聊天消息（增强版）
    """
    user_id, auth_info = user_info

    # 速率限制检查
    client_ip = request.client.host if request.client else "unknown"
    if not rate_limiter.is_allowed(client_ip):
        raise HTTPException(
            status_code=status.HTTP_429_TOO_MANY_REQUESTS,
            detail="请求过于频繁，请稍后重试",
        )

    # 安全检查
    risk = safety_guardrail.assess_message(chat_request.message)
    if risk.blocked:
        return ChatResponse(
            session_id=chat_request.session_id or "blocked",
            response=risk.warnings[0],
            intent="emergency",
            risk_level=risk.risk_level,
            requires_disclaimer=True,
            knowledge_sources=0,
            timestamp=datetime.now(timezone.utc).isoformat(),
        )

    # 会话管理
    session = get_or_create_session(
        chat_request.session_id or f"session_{user_id}_{int(datetime.now(timezone.utc).timestamp())}"
    )
    session.add_turn("user", chat_request.message)

    # 选择执行图
    if chat_request.enable_skills and chat_request.enable_enhanced_search:
        exec_graph = compiled_enhanced_graph
    else:
        exec_graph = compiled_base_graph

    # 执行 Agent
    initial_state = create_initial_state(
        session_id=chat_request.session_id or f"session_{user_id}_{int(datetime.now(timezone.utc).timestamp())}",
        user_message=chat_request.message,
    )

    try:
        result = await exec_graph.ainvoke(initial_state)
    except Exception as e:
        logger.error(f"Agent 执行失败: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"处理请求失败: {str(e)}",
        )

    # 记录对话
    response_text = result.get("response", "")
    session.add_turn("assistant", response_text)

    # 安全检查回复
    response_risk = safety_guardrail.assess_response(
        response=response_text,
        intent=result.get("intent", "general"),
        knowledge_sources=result.get("knowledge_sources", []),
    )

    # 自动触发会话摘要
    if session.should_summarize():
        asyncio.create_task(session.generate_summary())

    return ChatResponse(
        session_id=session.session_id,
        response=response_text,
        intent=result.get("intent", "general"),
        risk_level=result.get("risk_level", response_risk.risk_level),
        requires_disclaimer=risk.disclaimer_required or response_risk.disclaimer_required,
        knowledge_sources=len(result.get("knowledge_sources", [])),
        timestamp=datetime.now(timezone.utc).isoformat(),
    )


@router.post("/chat/stream")
async def chat_stream(
    chat_request: ChatRequest,
    request: Request,
    user_info: tuple = Depends(verify_api_key),
):
    """
    流式聊天接口（增强版，SSE）
    """
    user_id, auth_info = user_info

    # 安全检查
    risk = safety_guardrail.assess_message(chat_request.message)
    if risk.blocked:
        async def blocked_generator():
            yield {"data": json.dumps({"type": "safety_alert", "content": risk.warnings[0], "risk_level": risk.risk_level})}
        return EventSourceResponse(blocked_generator())

    async def event_generator():
        try:
            # 发送开始事件
            yield {
                "data": json.dumps({
                    "type": "start",
                    "session_id": chat_request.session_id or f"stream_{user_id}_{int(datetime.now(timezone.utc).timestamp())}",
                })
            }

            # 意图分析
            intent_result = graph.detect_intent({"user_message": chat_request.message})
            yield {
                "data": json.dumps({
                    "type": "intent",
                    "intent": intent_result.get("intent", "unknown"),
                })
            }

            # 执行 Agent
            exec_graph = compiled_enhanced_graph if chat_request.enable_skills else graph.graph
            initial_state = graph.create_initial_state(
                user_message=chat_request.message,
                user_context=chat_request.user_context,
            )

            result = await exec_graph.ainvoke(initial_state)

            response_text = result.get("response", "")

            # 流式发送回复
            chunk_size = 50
            for i in range(0, len(response_text), chunk_size):
                chunk = response_text[i:i + chunk_size]
                yield {
                    "data": json.dumps({
                        "type": "chunk",
                        "content": chunk,
                    })
                }
                await asyncio.sleep(0.01)  # 模拟流式延迟

            # 发送完成事件
            yield {
                "data": json.dumps({
                    "type": "done",
                    "intent": result.get("intent", "general"),
                    "risk_level": result.get("risk_level", "none"),
                    "knowledge_sources": len(result.get("knowledge_sources", [])),
                }),
                "event": "done",
            }

        except Exception as e:
            logger.error(f"流式处理失败: {e}")
            yield {
                "data": json.dumps({
                    "type": "error",
                    "content": f"处理失败: {str(e)}",
                })
            }

    return EventSourceResponse(event_generator())


@router.post("/drug-check")
async def check_drug_interactions(
    drug_request: DrugCheckRequest,
    user_info: tuple = Depends(verify_api_key),
):
    """
    药物相互作用检查
    """
    from src.utils.safety import DrugInteractionChecker

    results = []

    # 检查两两组合
    for i in range(len(drug_request.drugs)):
        for j in range(i + 1, len(drug_request.drugs)):
            risk = DrugInteractionChecker.check_combination(
                drug_request.drugs[i],
                drug_request.drugs[j],
            )
            if not risk.safe:
                results.append({
                    "drug_a": drug_request.drugs[i],
                    "drug_b": drug_request.drugs[j],
                    "risk_level": risk.risk_level,
                    "warnings": risk.warnings,
                })

    # 检查禁忌症
    for drug in drug_request.drugs:
        for condition in drug_request.conditions:
            risk = DrugInteractionChecker.check_contraindication(drug, condition)
            if not risk.safe:
                results.append({
                    "drug": drug,
                    "condition": condition,
                    "risk_level": risk.risk_level,
                    "warnings": risk.warnings,
                })

    return {
        "safe": len(results) == 0,
        "total_drugs": len(drug_request.drugs),
        "total_conditions": len(drug_request.conditions),
        "interactions": results,
        "timestamp": datetime.now(timezone.utc).isoformat(),
    }


@router.post("/health-record")
async def save_health_record(
    record: HealthRecordRequest,
    user_info: tuple = Depends(verify_api_key),
):
    """
    保存健康记录
    """
    from src.knowledge.health_record import VitalSigns, SymptomRecord, get_health_record

    user_id, auth_info = user_info
    health_record = get_health_record(record.user_id or user_id)

    # 保存生命体征
    if any([record.temperature, record.heart_rate, record.blood_pressure_sys,
            record.blood_sugar, record.weight]):
        vitals = VitalSigns(
            temperature=record.temperature,
            heart_rate=record.heart_rate,
            blood_pressure_sys=record.blood_pressure_sys,
            blood_pressure_dia=record.blood_pressure_dia,
            blood_sugar=record.blood_sugar,
            weight=record.weight,
        )
        health_record.add_vital_signs(vitals)

    # 保存症状
    if record.symptoms:
        symptom = SymptomRecord(
            description=record.symptoms,
        )
        health_record.add_symptom(symptom)

    return {
        "status": "ok",
        "user_id": health_record.user_id,
        "summary": health_record.get_summary(),
        "timestamp": datetime.now(timezone.utc).isoformat(),
    }


@router.get("/health-record/{user_id}")
async def get_health_record(
    user_id: str,
    user_info: tuple = Depends(verify_api_key),
):
    """
    获取健康记录
    """
    from src.knowledge.health_record import get_health_record

    record = get_health_record(user_id)
    return {
        "user_id": record.user_id,
        "summary": record.get_summary(),
        "recent_vitals": record.get_recent_vitals(),
        "recent_symptoms": record.get_recent_symptoms(),
        "current_medications": record.get_current_medications(),
        "allergies": record.allergies,
        "chronic_conditions": record.chronic_conditions,
    }


@router.get("/skills")
async def list_skills(
    user_info: tuple = Depends(verify_api_key),
):
    """
    列出可用 Skill
    """
    from src.skills.manager import skill_manager
    return {
        "skills": skill_manager.list_skills(),
    }
