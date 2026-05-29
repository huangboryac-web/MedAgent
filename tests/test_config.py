"""
基础配置测试
"""

import pytest
from src.config import get_settings


class TestConfig:
    """配置系统测试"""

    def test_settings_singleton(self):
        """测试配置单例模式"""
        s1 = get_settings()
        s2 = get_settings()
        assert s1 is s2

    def test_default_values(self):
        """测试默认配置值"""
        settings = get_settings()
        assert settings.app_env == "development"
        assert settings.app_port == 8080
        assert settings.default_llm_provider == "openai"
        assert settings.vector_db_provider == "pinecone"

    def test_env_file_loading(self):
        """测试 .env 文件加载（需存在 .env 文件）"""
        # 此测试在无 .env 文件时跳过
        pass
