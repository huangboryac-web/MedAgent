"""
FastAPI 应用测试
"""

import pytest
from fastapi.testclient import TestClient

from src.main import app


class TestFastAPIApp:
    """FastAPI 应用基础测试"""

    @pytest.fixture
    def client(self):
        """测试客户端 fixture"""
        return TestClient(app)

    def test_health_endpoint(self, client):
        """测试健康检查接口"""
        response = client.get("/health")
        assert response.status_code == 200
        data = response.json()
        assert data["status"] == "ok"
        assert "env" in data

    def test_chat_endpoint_validation(self, client):
        """测试聊天接口参数校验"""
        # 空消息应返回 422
        response = client.post("/api/v1/chat/send", json={"message": ""})
        assert response.status_code == 422

        # 正常消息应返回 200
        response = client.post("/api/v1/chat/send", json={"message": "头痛"})
        assert response.status_code == 200
        data = response.json()
        assert "session_id" in data
        assert "response" in data
        assert "safety_warnings" in data

    def test_chat_stream_endpoint(self, client):
        """测试流式聊天接口"""
        response = client.post("/api/v1/chat/stream", json={"message": "测试"})
        assert response.status_code == 200
        assert response.headers["content-type"] == "text/event-stream; charset=utf-8"
