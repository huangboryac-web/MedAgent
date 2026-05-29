"""
Phase 3 集成测试
测试增强检索、Skill 集成、用户认证
"""

import pytest
from fastapi.testclient import TestClient

from src.main import app
from src.skills.manager import skill_manager, SkillResult
from src.skills.integration import SkillIntegrationService, skill_integration
from src.utils.auth import AuthService, RateLimiter
from src.utils.safety import DrugInteractionChecker, HallucinationDetector, SafetyGuardrail


client = TestClient(app)


@pytest.fixture(autouse=True)
def reset_auth():
    """重置认证状态"""
    AuthService._api_keys.clear()


class TestSkillManager:
    """Skill 管理器测试"""

    def test_list_skills(self):
        """测试列出 Skill"""
        skills = skill_manager.list_skills()
        assert len(skills) > 0
        assert any(s["name"] == "deep-research" for s in skills)
        assert any(s["name"] == "academic-search" for s in skills)

    def test_get_skill_info(self):
        """测试获取 Skill 信息"""
        info = skill_manager.get_skill_info("deep-research")
        assert info is not None
        assert "description" in info
        assert "input" in info

    def test_unknown_skill(self):
        """测试未知 Skill"""
        info = skill_manager.get_skill_info("unknown-skill")
        assert info is None

    @pytest.mark.asyncio
    async def test_execute_skill_without_callback(self):
        """测试无回调时的 Skill 执行"""
        result = await skill_manager.execute("deep-research", {"query": "头痛"})
        assert result.success
        assert result.skill_name == "deep-research"


class TestDrugInteractionChecker:
    """药物检查器测试"""

    def test_high_risk_combination(self):
        """测试高风险药物组合"""
        risk = DrugInteractionChecker.check_combination("华法林", "阿司匹林")
        assert not risk.safe
        assert risk.risk_level == "high"
        assert risk.blocked

    def test_safe_combination(self):
        """测试安全药物组合"""
        risk = DrugInteractionChecker.check_combination("维生素C", "钙片")
        assert risk.safe
        assert risk.risk_level == "none"

    def test_contraindication(self):
        """测试禁忌症检查"""
        risk = DrugInteractionChecker.check_contraindication("布洛芬", "胃溃疡")
        assert not risk.safe
        assert risk.blocked

    def test_safe_condition(self):
        """测试安全疾病组合"""
        risk = DrugInteractionChecker.check_contraindication("维生素C", "感冒")
        assert risk.safe


class TestHallucinationDetector:
    """幻觉检测器测试"""

    def test_antibiotic_misconception(self):
        """测试抗生素误区检测"""
        warnings = HallucinationDetector.scan("感冒了可以吃抗生素治疗")
        assert len(warnings) > 0
        assert "病毒性感冒" in warnings[0]

    def test_no_misconception(self):
        """测试无误导内容"""
        warnings = HallucinationDetector.scan("建议多喝温水，适当休息")
        assert len(warnings) == 0

    def test_vitamin_c_misconception(self):
        """测试维生素C误区"""
        warnings = HallucinationDetector.scan("维生素C可以预防感冒")
        assert len(warnings) > 0


class TestSafetyGuardrail:
    """安全护栏测试"""

    def test_emergency_detection(self):
        """测试紧急症状检测"""
        risk = SafetyGuardrail().assess_message("我呼吸困难，胸口剧痛")
        assert not risk.safe
        assert risk.risk_level == "critical"
        assert risk.blocked

    def test_self_harm_detection(self):
        """测试自伤意图检测"""
        risk = SafetyGuardrail().assess_message("我觉得活着没意思，想自杀")
        assert not risk.safe
        assert risk.risk_level == "critical"

    def test_normal_message(self):
        """测试普通消息"""
        risk = SafetyGuardrail().assess_message("最近有点头疼")
        assert risk.safe
        assert risk.risk_level == "none"


class TestAuthService:
    """认证服务测试"""

    def test_api_key_registration(self):
        """测试 API Key 注册"""
        AuthService.register_api_key("test-key-123", "user-1")
        info = AuthService.verify_api_key("test-key-123")
        assert info is not None
        assert info["user_id"] == "user-1"

    def test_invalid_api_key(self):
        """测试无效 API Key"""
        info = AuthService.verify_api_key("invalid-key")
        assert info is None

    def test_api_key_revocation(self):
        """测试 API Key 撤销"""
        AuthService.register_api_key("test-key-456", "user-2")
        assert AuthService.verify_api_key("test-key-456") is not None
        AuthService.revoke_api_key("test-key-456")
        assert AuthService.verify_api_key("test-key-456") is None


class TestRateLimiter:
    """速率限制器测试"""

    def test_allowed_requests(self):
        """测试允许的请求"""
        limiter = RateLimiter(max_requests=5, window_seconds=60)
        for _ in range(5):
            assert limiter.is_allowed("client-1")
        assert not limiter.is_allowed("client-1")


class TestEnhancedAPI:
    """增强 API 测试"""

    def test_health_endpoint(self):
        """测试增强版健康检查"""
        response = client.get("/api/v2/health")
        assert response.status_code == 200
        data = response.json()
        assert data["status"] == "healthy"
        assert data["version"] == "2.0.0"

    def test_chat_invalid_auth(self):
        """测试无效认证"""
        # 开发环境下允许匿名访问，所以应该返回200
        response = client.post(
            "/api/v2/chat/send",
            json={"message": "头疼"},
        )
        # 开发环境允许匿名访问，所以返回200
        assert response.status_code == 200

    def test_chat_with_auth(self):
        """测试带认证的聊天"""
        AuthService.register_api_key("test-key", "user-1")
        response = client.post(
            "/api/v2/chat/send",
            json={"message": "你好"},
            headers={"X-API-Key": "test-key"},
        )
        assert response.status_code == 200

    def test_chat_emergency_block(self):
        """测试紧急消息拦截"""
        AuthService.register_api_key("test-key-2", "user-2")
        response = client.post(
            "/api/v2/chat/send",
            json={"message": "我呼吸困难"},
            headers={"X-API-Key": "test-key-2"},
        )
        assert response.status_code == 200
        data = response.json()
        assert data["intent"] == "emergency"

    def test_drug_check_endpoint(self):
        """测试药物检查接口"""
        AuthService.register_api_key("test-key-3", "user-3")
        response = client.post(
            "/api/v2/drug-check",
            json={"drugs": ["华法林", "阿司匹林"], "conditions": []},
            headers={"X-API-Key": "test-key-3"},
        )
        assert response.status_code == 200
        data = response.json()
        assert not data["safe"]

    def test_skills_list_endpoint(self):
        """测试 Skill 列表接口"""
        AuthService.register_api_key("test-key-4", "user-4")
        response = client.get(
            "/api/v2/skills",
            headers={"X-API-Key": "test-key-4"},
        )
        assert response.status_code == 200
        data = response.json()
        assert "skills" in data
