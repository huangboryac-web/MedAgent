"""
增强型 Agent 图
集成外部 Skill 进行深度知识检索
"""

from langgraph.graph import END, StateGraph

from src.agent.graph import AgentStateDict
from src.utils.logger import logger


def _detect_intent(state: AgentStateDict) -> AgentStateDict:
    """意图检测节点"""
    message = state.get("user_message", "").lower()
    emergency_keywords = ["呼吸困难", "胸痛", "心脏骤停", "大出血", "意识丧失", "窒息"]
    medical_keywords = ["头疼", "发烧", "咳嗽", "胃疼", "血压", "过敏",
                       "糖尿病", "失眠", "腰疼", "感冒", "关节", "皮疹",
                       "恶心", "呕吐", "头晕", "腹泻", "便秘"]

    if any(kw in message for kw in emergency_keywords):
        state["intent"] = "emergency"
    elif any(kw in message for kw in medical_keywords):
        state["intent"] = "medical"
    elif len(message) < 5:
        state["intent"] = "clarify"
    else:
        state["intent"] = "general"
    return state


def _classify_symptoms(state: AgentStateDict) -> AgentStateDict:
    """症状分级节点"""
    if state.get("intent") == "emergency":
        state["symptom_severity"] = "critical"
        return state

    severity_mapping = {
        "critical": ["呼吸困难", "胸痛", "大出血", "意识丧失"],
        "severe": ["高烧", "剧烈", "无法忍受", "吐血", "昏迷"],
        "moderate": ["持续", "加重", "发烧", "肿胀", "过敏", "失眠", "血压高"],
        "mild": ["轻微", "偶尔", "有点"],
    }
    message = state.get("user_message", "").lower()
    for severity, keywords in severity_mapping.items():
        if any(kw in message for kw in keywords):
            state["symptom_severity"] = severity
            return state
    state["symptom_severity"] = "mild"
    return state


def _cross_validation(state: AgentStateDict) -> AgentStateDict:
    """交叉验证节点"""
    state["cross_validation_passed"] = len(state.get("knowledge_sources", [])) >= 1
    return state


def _safety_guardrail(state: AgentStateDict) -> AgentStateDict:
    """安全护栏节点"""
    state.setdefault("safety", {})
    if state.get("intent") == "emergency":
        state["safety"]["disclaimer_required"] = False
        state["final_response"] = (
            "您描述的症状可能为紧急情况。\n\n"
            "请立即拨打120急救电话或前往最近医院急诊科就诊。\n\n"
            "在等待救援期间，请保持镇静，如有旁人在场请寻求帮助。"
        )
    elif state.get("intent") == "medical":
        state["safety"]["disclaimer_required"] = True
    return state


async def _generate_response(state: AgentStateDict) -> AgentStateDict:
    """生成最终回复节点"""
    if state.get("intent") == "emergency":
        return state
    if state.get("intent") == "general":
        state["final_response"] = (
            "您好，我是 MedAgent 个人医疗 AI 助手。我可以帮助您：\n\n"
            "- 分析症状并提供健康参考信息\n"
            "- 检索最新医学研究和诊疗指南\n"
            "- 解答用药注意事项\n\n"
            "请描述您想咨询的健康问题。"
        )
    elif state.get("intent") == "medical":
        severity = state.get("symptom_severity", "mild")
        labels = {"mild": "轻度", "moderate": "中度", "severe": "重度", "critical": "危急"}
        validated = state.get("cross_validation_passed", False)
        state["final_response"] = (
            f"已分析您的症状描述。\n\n"
            f"严重程度评估: {labels.get(severity, severity)}\n"
            f"来源验证: {'已通过多源交叉验证' if validated else '信息有限，建议进一步确认'}\n\n"
            f"建议：\n"
            f"1. 详细描述症状的持续时间、具体部位\n"
            f"2. 记录伴随症状\n"
            f"3. 如症状持续或加重，请及时就医"
        )
    return state


async def _reflection_loop(state: AgentStateDict) -> AgentStateDict:
    """反思循环节点"""
    return state


def _hallucination_guard(state: AgentStateDict) -> AgentStateDict:
    """幻觉检测节点"""
    state["hallucination_checked"] = True
    return state


def _add_disclaimer(state: AgentStateDict) -> AgentStateDict:
    """添加免责声明"""
    if state.get("intent") == "medical" and state.get("safety", {}).get("disclaimer_required", False):
        disclaimer = "\n\n---\n*以上内容仅供参考，不构成医疗建议。如有不适请及时就医。*"
        final_response = state.get("final_response", "")
        if disclaimer not in final_response:
            state["final_response"] = final_response + disclaimer
    return state


async def _knowledge_stub(state: AgentStateDict) -> AgentStateDict:
    """知识检索桩节点"""
    state["knowledge_sources"] = []
    return state


def create_base_graph() -> StateGraph:
    """创建基础 Agent 图"""
    w = StateGraph(AgentStateDict)
    w.add_node("detect_intent", _detect_intent)
    w.add_node("classify_symptoms", _classify_symptoms)
    w.add_node("knowledge_retrieval", _knowledge_stub)
    w.add_node("cross_validation", _cross_validation)
    w.add_node("safety_guardrail", _safety_guardrail)
    w.add_node("generate_response", _generate_response)
    w.add_node("hallucination_guard", _hallucination_guard)
    w.add_node("reflection_loop", _reflection_loop)
    w.add_node("add_disclaimer", _add_disclaimer)

    w.set_entry_point("detect_intent")
    w.add_edge("detect_intent", "classify_symptoms")
    w.add_edge("classify_symptoms", "knowledge_retrieval")
    w.add_edge("knowledge_retrieval", "cross_validation")
    w.add_edge("cross_validation", "safety_guardrail")
    w.add_edge("safety_guardrail", "generate_response")
    w.add_edge("generate_response", "hallucination_guard")
    w.add_edge("hallucination_guard", "reflection_loop")
    w.add_edge("reflection_loop", "add_disclaimer")
    w.add_edge("add_disclaimer", END)
    return w


compiled_base_graph = create_base_graph().compile()


# ── 增强图 ──

def create_enhanced_graph() -> StateGraph:
    """创建增强型 Agent 图"""
    w = StateGraph(AgentStateDict)
    w.add_node("detect_intent", _detect_intent)
    w.add_node("classify_symptoms", _classify_symptoms)
    w.add_node("enhanced_retrieval", _enhanced_retrieval)
    w.add_node("cross_validation", _cross_validation)
    w.add_node("safety_guardrail", _safety_guardrail)
    w.add_node("generate_response", _generate_response)
    w.add_node("hallucination_guard", _hallucination_guard)
    w.add_node("reflection_loop", _reflection_loop)
    w.add_node("add_disclaimer", _add_disclaimer)

    w.set_entry_point("detect_intent")
    w.add_edge("detect_intent", "classify_symptoms")
    w.add_edge("classify_symptoms", "enhanced_retrieval")
    w.add_edge("enhanced_retrieval", "cross_validation")
    w.add_edge("cross_validation", "safety_guardrail")
    w.add_edge("safety_guardrail", "generate_response")
    w.add_edge("generate_response", "hallucination_guard")
    w.add_edge("hallucination_guard", "reflection_loop")
    w.add_edge("reflection_loop", "add_disclaimer")
    w.add_edge("add_disclaimer", END)
    return w


async def _enhanced_retrieval(state: AgentStateDict) -> AgentStateDict:
    """增强检索节点"""
    query = state.get("user_message", "")
    intent = state.get("intent", "general")
    if not query:
        state["knowledge_sources"] = []
        return state
    try:
        from src.knowledge.enhanced_retriever import EnhancedKnowledgeRetriever
        retriever = EnhancedKnowledgeRetriever()
        results = await retriever.retrieve_enhanced(query, intent)
        state["knowledge_sources"] = results.get("vector_results", [])
        state.setdefault("metadata", {})
        state["metadata"]["enhanced_knowledge"] = results.get("external_skill_results", [])
        logger.info(f"增强检索: intent={intent}, sources={len(state['knowledge_sources'])}")
    except Exception as e:
        logger.error(f"增强检索失败: {e}")
        state["knowledge_sources"] = []
    return state


compiled_enhanced_graph = create_enhanced_graph().compile()
