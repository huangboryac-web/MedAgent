"""
MedAgent 全局配置管理
基于 pydantic-settings 从环境变量和 .env 文件加载
"""

from functools import lru_cache
from pathlib import Path
from typing import Literal

from pydantic_settings import BaseSettings, SettingsConfigDict

PROJECT_ROOT = Path(__file__).resolve().parent.parent


class Settings(BaseSettings):
    """应用配置类，自动从 .env 和环境变量加载"""

    model_config = SettingsConfigDict(
        env_file=PROJECT_ROOT / "config" / ".env",
        env_file_encoding="utf-8",
        extra="ignore",
    )

    # ── LLM ──
    openai_api_key: str = ""
    anthropic_api_key: str = ""
    default_llm_provider: Literal["openai", "anthropic"] = "openai"
    default_llm_model: str = "gpt-4o"

    # ── 搜索 ──
    tavily_api_key: str = ""

    # ── 向量数据库 ──
    vector_db_provider: Literal["pinecone", "weaviate"] = "pinecone"
    pinecone_api_key: str = ""
    pinecone_environment: str = "us-east-1"
    pinecone_index_name: str = "medagent"
    weaviate_url: str = "http://localhost:8080"

    # ── Redis ──
    redis_url: str = "redis://localhost:6379/0"

    # ── 服务 ──
    app_env: Literal["development", "production", "test"] = "development"
    app_host: str = "0.0.0.0"
    app_port: int = 8080
    log_level: Literal["DEBUG", "INFO", "WARNING", "ERROR"] = "INFO"


@lru_cache()
def get_settings() -> Settings:
    """获取全局配置单例"""
    return Settings()
