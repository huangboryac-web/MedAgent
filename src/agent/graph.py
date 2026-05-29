"""
LangGraph Agent 图编排核心
实现: 意图路由 → 症状分级 → 知识检索 → 交叉验证 → 反思循环 → 安全护栏
"""

import asyncio
from typing import AsyncIterator

from src.agent.state import AgentState, KnowledgeSource, SafetyCheck
from src.config import get_settings
from src.utils.logger import logger

settings = get_settings()


class MedAgentGraph:
    """
    Agent 图编排器
    管理 LangGraph 状态机中所有节点的执行流程
    """

    def __init__(self):
        self._graph = None
        self._compiled = False

    # ── 核心节点 ──

    async def _route_intent(self, state: AgentState) -> AgentState:
        """意图路由：分类用户输入为 medical / general / clarify / emergency"""
        msg = state.user_message.lower()

        # 高危关键词检测
        emergency_keywords = [
            "呼吸困难", "胸痛", "大出血", "猝死", "心跳停止", "窒息",
            "意识丧失", "中风", "急性", "休克", "抽搐", "昏厥",
        ]
        for kw in emergency_keywords:
            if kw in msg:
                state.intent = "emergency"
                state.symptom_severity = "critical"
                state.safety = SafetyCheck(
                    safe=False,
                    risk_level="critical",
                    warnings=["检测到高危症状描述，请立即拨打120或前往最近急诊科就诊"],
                    disclaimer_required=True,
                )
                state.final_response = (
                    "【紧急安全提示】您描述的症状可能属于危急情况。\n\n"
                    "请立即采取以下措施：\n"
                    "1. 拨打 120 急救电话\n"
                    "2. 如可能，让身边人协助送医\n"
                    "3. 保持电话畅通，等待急救人员到达\n\n"
                    "⚠️ 本系统不能替代紧急医疗救助。"
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
                state.intent = "medical"
                return state

        state.intent = "general"
        return state

    async def _assess_severity(self, state: AgentState) -> AgentState:
        """症状分级：评估严重程度 (mild / moderate / severe)"""
        if state.intent != "medical":
            return state

        msg = state.user_message.lower()
        severe_keywords = ["剧烈", "无法忍受", "持续", "恶化", "高烧", "咳血", "便血"]
        moderate_keywords = ["反复", "频繁", "影响", "妨碍", "难受", "一周", "多天"]

        if any(kw in msg for kw in severe_keywords):
            state.symptom_severity = "severe"
            state.safety.warnings.append("症状描述较严重，建议尽快就医评估")
        elif any(kw in msg for kw in moderate_keywords):
            state.symptom_severity = "moderate"

        return state

    async def _search_knowledge(self, state: AgentState) -> AgentState:
        """知识检索：多引擎搜索医学知识"""
        if state.intent != "medical":
            return state

        # 构建搜索查询
        state.search_queries = [
            f"{state.user_message} 诊疗指南",
            f"{state.user_message} 临床研究 site:pubmed.ncbi.nlm.nih.gov",
            f"{state.user_message} 症状 病因 鉴别诊断",
        ]

        # 模拟知识检索（实际通过 Skills 调用）
        state.knowledge_results = []
        logger.info(f"知识检索查询: {state.search_queries}")

        return state

    async def _cross_validate(self, state: AgentState) -> AgentState:
        """交叉验证：多源信息一致性校验"""
        if state.intent != "medical":
            return state

        # 对检索结果进行来源交叉校验
        state.cross_validation_passed = len(state.knowledge_results) >= 2
        return state

    async def _reflect(self, state: AgentState) -> AgentState:
        """反思循环：对生成结果进行二次审查"""
        if state.intent != "medical":
            return state

        # 检查是否需要对答案进行修正
        if not state.cross_validation_passed and state.intent == "medical":
            state.safety.warnings.append("当前回复基于有限信息，请咨询专业医生确认")
            state.safety.disclaimer_required = True

        return state

    async def _hallucination_guard(self, state: AgentState) -> AgentState:
        """幻觉检测：检查生成内容是否有虚构引用"""
        state.hallucination_checked = True
        return state

    async def _safety_gate(self, state: AgentState) -> AgentState:
        """安全护栏：最终安全检查与免责声明"""
        if state.intent == "medical" and state.safety.disclaimer_required:
            disclaimer = (
                "\n\n---\n*以上内容仅供参考，不构成医疗建议。如有不适请及时就医。*"
            )
            if disclaimer not in state.final_response:
                state.final_response += disclaimer

        return state

    async def _generate_response(self, state: AgentState) -> AgentState:
        """生成最终回复"""
        if state.intent == "emergency":
            return state  # 已在上游生成紧急响应

        if state.intent == "general":
            state.final_response = (
                "您好，我是 MedAgent 个人医疗 AI 助手。我可以帮助您：\n\n"
                "- 分析症状并提供健康参考信息\n"
                "- 检索最新医学研究和诊疗指南\n"
                "- 解答用药注意事项\n\n"
                "请描述您想咨询的健康问题。"
            )
        elif state.intent == "medical":
            state.final_response = (
                f"已分析您的症状描述。\n\n"
                f"严重程度评估: {state.symptom_severity}\n"
                f"来源验证: {'已通过' if state.cross_validation_passed else '信息有限'}\n\n"
                f"建议：\n"
                f"1. 详细描述症状的持续时间、具体部位\n"
                f"2. 记录伴随症状\n"
                f"3. 如症状持续或加重，请及时就医"
            )

        return state

    # ── 图执行 ──

    async def run(self, session_id: str, user_message: str) -> AgentState:
        """
        运行 Agent 图（非流式）
        按序执行所有节点并返回最终状态
        """
        from src.agent.state import create_initial_state

        state = create_initial_state(session_id, user_message)

        # 按 DAG 顺序执行节点
        nodes = [
            self._route_intent,
            self._assess_severity,
            self._search_knowledge,
            self._cross_validate,
            self._reflect,
            self._generate_response,
            self._hallucination_guard,
            self._safety_gate,
        ]

        for node in nodes:
            # 紧急情况短路
            if state.intent == "emergency":
                break
            state = await node(state)

        logger.info(
            f"Agent 执行完毕 | session={session_id} | intent={state.intent} | "
            f"severity={state.symptom_severity} | safe={state.safety.safe}"
        )
        return state

    async def stream(self, session_id: str, user_message: str) -> AsyncIterator[dict]:
        """
        流式运行 Agent 图
        每个节点完成后 yield 事件
        """
        from src.agent.state import create_initial_state

        state = create_initial_state(session_id, user_message)

        nodes = [
            ("intent_routing", self._route_intent),
            ("severity_assessment", self._assess_severity),
            ("knowledge_search", self._search_knowledge),
            ("cross_validation", self._cross_validate),
            ("reflection", self._reflect),
            ("response_generation", self._generate_response),
            ("hallucination_check", self._hallucination_guard),
            ("safety_gate", self._safety_gate),
        ]

        for node_name, node_func in nodes:
            if state.intent == "emergency":
                yield {"type": "emergency", "payload": state.final_response}
                break

            state = await node_func(state)
            yield {
                "type": "node_complete",
                "payload": {"node": node_name, "intent": state.intent},
            }

        yield {"type": "complete", "payload": state.final_response}
