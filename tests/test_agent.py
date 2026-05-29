"""
Agent 图编排测试
"""

import pytest
from src.agent.graph import MedAgentGraph
from src.agent.state import AgentState


class TestAgentGraph:
    """Agent 图编排测试"""

    @pytest.fixture
    def graph(self):
        return MedAgentGraph()

    @pytest.mark.asyncio
    async def test_emergency_intent_detection(self, graph):
        """测试紧急意图检测"""
        result = await graph.run(
            session_id="test-emergency",
            user_message="我呼吸困难，胸口剧痛"
        )
        assert result["intent"] == "emergency"
        assert result["symptom_severity"] == "critical"
        assert result["final_response"].startswith("【紧急安全提示】")
        assert not result["safety"]["safe"]

    @pytest.mark.asyncio
    async def test_medical_intent_detection(self, graph):
        """测试医疗意图检测"""
        result = await graph.run(
            session_id="test-medical",
            user_message="我有点头疼，持续两天了"
        )
        assert result["intent"] == "medical"
        assert result["symptom_severity"] in ["mild", "moderate", "severe"]

    @pytest.mark.asyncio
    async def test_general_intent_detection(self, graph):
        """测试通用意图检测"""
        result = await graph.run(
            session_id="test-general",
            user_message="你好，介绍一下你的功能"
        )
        assert result["intent"] == "general"
        assert "我可以帮助您" in result["final_response"]

    @pytest.mark.asyncio
    async def test_safety_disclaimer(self, graph):
        """测试安全免责声明"""
        result = await graph.run(
            session_id="test-safety",
            user_message="我发烧39度，咳嗽带血"
        )
        if result["intent"] == "medical" and result["safety"]["disclaimer_required"]:
            assert "以上内容仅供参考" in result["final_response"]
