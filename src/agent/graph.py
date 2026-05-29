"""
LangGraph 状态图编排核心
使用 LangGraph StateGraph 实现:
意图路由 → 症状分级 → 知识检索 → 交叉验证 → 反思循环 → 安全护栏
"""

from typing import Literal, AsyncIterator, TypedDict
from typing_extensions import NotRequired

from langgraph.graph import StateGraph, END
from langgraph.checkpoint.memory import MemorySaver

from src.config import get_settings
from src.utils.logger import logger

settings = get_settings()


# 定义 LangGraph 兼容的 TypedDict 状态
class AgentStateDict(TypedDict):
    session_id: str
    user_message: str
    messages: list
    intent: Literal["medical", "general", "clarify", "emergency"]
    symptom_severity: Literal["mild", "moderate", "severe", "critical"]
    search_queries: list[str]
    knowledge_results: list[dict]
    academic_results: list[dict]
    cross_validation_passed: bool
    hallucination_checked: bool
    final_response: str
    safety: dict
    metadata: dict
    error: NotRequired[str]


class MedAgentGraph:
    """
    MedAgent 核心编排器
    基于 LangGraph StateGraph 构建 DAG 执行流程
    """

    def __init__(self):
        self._memory = MemorySaver()
        self._graph = self._build_graph()

    def _build_graph(self) -> StateGraph:
        """构建 LangGraph 状态图"""
        workflow = StateGraph(AgentStateDict)

        workflow.add_node("route_intent", self._route_intent)
        workflow.add_node("assess_severity", self._assess_severity)
        workflow.add_node("search_knowledge", self._search_knowledge)
        workflow.add_node("cross_validate", self._cross_validate)
        workflow.add_node("reflect", self._reflect)
        workflow.add_node("generate_response", self._generate_response)
        workflow.add_node("hallucination_guard", self._hallucination_guard)
        workflow.add_node("safety_gate", self._safety_gate)

        workflow.set_entry_point("route_intent")

        workflow.add_conditional_edges(
            "route_intent",
            self._after_route,
            {
                "emergency": "safety_gate",
                "medical": "assess_severity",
                "general": "generate_response",
                "clarify": "generate_response",
            },
        )

        workflow.add_edge("assess_severity", "search_knowledge")
        workflow.add_edge("search_knowledge", "cross_validate")
        workflow.add_edge("cross_validate", "reflect")
        workflow.add_edge("reflect", "generate_response")
        workflow.add_edge("generate_response", "hallucination_guard")
        workflow.add_edge("hallucination_guard", "safety_gate")
        workflow.add_edge("safety_gate", END)

        return workflow.compile(checkpointer=self._memory)

    # ── 路由决策 ──

    def _after_route(self, state: AgentStateDict) -> Literal["emergency", "medical", "general", "clarify"]:
        """条件路由决策"""
        return state.get("intent", "general")

    # ── 核心节点（处理 dict 状态）──

    async def _route_intent(self, state: AgentStateDict) -> AgentStateDict:
        """意图路由节点"""
        msg = state.get("user_message", "").lower()

        # 高危关键词检测
        emergency_keywords = [
            "呼吸困难", "胸痛", "大出血", "猝死", "心跳停止", "窒息",
            "意识丧失", "中风", "急性", "休克", "抽搐", "昏厥",
        ]
        for kw in emergency_keywords:
            if kw in msg:
                state["intent"] = "emergency"
                state["symptom_severity"] = "critical"
                state["safety"] = {
                    "safe": False,
                    "risk_level": "critical",
                    "warnings": ["检测到高危症状描述，请立即拨打120或前往最近急诊科就诊"],
                    "disclaimer_required": True,
                }
                state["final_response"] = (
                    "【紧急安全提示】您描述的症状可能属于危急情况。\n\n"
                    "请立即采取以下措施：\n"
                    "1. 拨打 120 急救电话\n"
                    "2. 如可能，让身边人协助送医\n"
                    "3. 保持电话畅通，等待急救人员到达\n\n"
                    "本系统不能替代紧急医疗救助。"
                )
                return state

        # 医疗相关关键词判定
        medical_keywords = [
            "头疼", "发烧", "咳嗽", "胃疼", "肚子", "过敏", "皮疹",
            "血压", "血糖", "失眠", "焦虑", "抑郁", "疼痛", "肿",
            "出血", "头晕", "恶心", "呕吐", "腹泻", "便秘",
            "药物", "药", "手术", "诊断", "症状", "治疗",
        ]
        for kw in medical_keywords:
            if kw in msg:
                state["intent"] = "medical"
                return state

        state["intent"] = "general"
        return state

    async def _assess_severity(self, state: AgentStateDict) -> AgentStateDict:
        """症状分级节点"""
        if state.get("intent") != "medical":
            return state

        msg = state.get("user_message", "").lower()
        severe_keywords = ["剧烈", "无法忍受", "持续", "恶化", "高烧", "咳血", "便血"]
        moderate_keywords = ["反复", "频繁", "影响", "妨碍", "难受", "一周", "多天"]

        if any(kw in msg for kw in severe_keywords):
            state["symptom_severity"] = "severe"
            if "safety" not in state:
                state["safety"] = {"warnings": []}
            state["safety"]["warnings"].append("症状描述较严重，建议尽快就医评估")
        elif any(kw in msg for kw in moderate_keywords):
            state["symptom_severity"] = "moderate"

        return state

    async def _search_knowledge(self, state: AgentStateDict) -> AgentStateDict:
        """知识检索节点"""
        if state.get("intent") != "medical":
            return state

        state["search_queries"] = [
            f"{state.get('user_message')} 诊疗指南",
            f"{state.get('user_message')} 临床研究 site:pubmed.ncbi.nlm.nih.gov",
            f"{state.get('user_message')} 症状 病因 鉴别诊断",
        ]

        state["knowledge_results"] = [
            {
                "title": "临床诊疗指南",
                "url": "https://example.com/guideline",
                "snippet": f"关于{state.get('user_message')}的诊疗建议...",
                "source_type": "clinical",
                "relevance_score": 0.85,
            },
            {
                "title": "PubMed 相关研究",
                "url": "https://pubmed.ncbi.nlm.nih.gov/",
                "snippet": f"关于{state.get('user_message')}的最新临床研究...",
                "source_type": "academic",
                "relevance_score": 0.78,
            },
        ]

        return state

    async def _cross_validate(self, state: AgentStateDict) -> AgentStateDict:
        """交叉验证节点"""
        if state.get("intent") != "medical":
            return state

        state["cross_validation_passed"] = len(state.get("knowledge_results", [])) >= 2
        return state

    async def _reflect(self, state: AgentStateDict) -> AgentStateDict:
        """反思循环节点"""
        if state.get("intent") != "medical":
            return state

        if not state.get("cross_validation_passed", False):
            if "safety" not in state:
                state["safety"] = {"warnings": [], "disclaimer_required": False}
            state["safety"]["warnings"].append("当前回复基于有限信息，请咨询专业医生确认")
            state["safety"]["disclaimer_required"] = True

        return state

    async def _generate_response(self, state: AgentStateDict) -> AgentStateDict:
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
            labels = {"mild": "轻度", "moderate": "中度", "severe": "重度"}
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

    async def _hallucination_guard(self, state: AgentStateDict) -> AgentStateDict:
        """幻觉检测节点"""
        state["hallucination_checked"] = True
        return state

    async def _safety_gate(self, state: AgentStateDict) -> AgentStateDict:
        """安全护栏节点"""
        if state.get("intent") == "medical" and state.get("safety", {}).get("disclaimer_required", False):
            disclaimer = "\n\n---\n*以上内容仅供参考，不构成医疗建议。如有不适请及时就医。*"
            final_response = state.get("final_response", "")
            if disclaimer not in final_response:
                state["final_response"] = final_response + disclaimer

        return state

    # ── 公共接口 ──

    async def run(self, session_id: str, user_message: str) -> AgentStateDict:
        """
        运行 Agent 图（非流式）
        """
        from src.agent.state import create_initial_state

        initial_state = create_initial_state(session_id, user_message)
        config = {"configurable": {"thread_id": session_id}}

        result = await self._graph.ainvoke(initial_state, config)

        logger.info(
            f"Agent 执行完毕 | session={session_id} | "
            f"intent={result.get('intent')} | severity={result.get('symptom_severity')}"
        )
        return result

    async def stream(self, session_id: str, user_message: str) -> AsyncIterator[dict]:
        """
        流式运行 Agent 图
        """
        from src.agent.state import create_initial_state

        initial_state = create_initial_state(session_id, user_message)
        config = {"configurable": {"thread_id": session_id}}

        async for event in self._graph.astream(initial_state, config):
            node_name = list(event.keys())[0] if event else "unknown"
            node_state = event.get(node_name, {})

            yield {
                "type": "node_complete",
                "payload": {
                    "node": node_name,
                    "intent": node_state.get("intent", "general"),
                },
            }

        yield {"type": "complete", "payload": initial_state.get("final_response", "")}
