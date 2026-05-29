"""
LLM 工厂
统一管理 OpenAI / Anthropic 等 LLM 客户端
"""

from typing import Optional

from langchain_openai import ChatOpenAI
from langchain_anthropic import ChatAnthropic

from src.config import get_settings
from src.utils.logger import logger

settings = get_settings()


class LLMFactory:
    """LLM 客户端工厂"""

    _instances: dict[str, object] = {}

    @classmethod
    def get_openai(
        cls,
        model: Optional[str] = None,
        temperature: float = 0.3,
        max_tokens: int = 2048,
    ) -> ChatOpenAI:
        """获取 OpenAI 客户端"""
        model_name = model or settings.default_llm_model
        cache_key = f"openai:{model_name}"

        if cache_key not in cls._instances:
            cls._instances[cache_key] = ChatOpenAI(
                api_key=settings.openai_api_key,
                model=model_name,
                temperature=temperature,
                max_tokens=max_tokens,
            )
            logger.info(f"OpenAI 客户端初始化: model={model_name}")

        return cls._instances[cache_key]

    @classmethod
    def get_anthropic(
        cls,
        model: str = "claude-3-5-sonnet-20241022",
        temperature: float = 0.3,
        max_tokens: int = 2048,
    ) -> ChatAnthropic:
        """获取 Anthropic 客户端"""
        cache_key = f"anthropic:{model}"

        if cache_key not in cls._instances:
            cls._instances[cache_key] = ChatAnthropic(
                api_key=settings.anthropic_api_key,
                model=model,
                temperature=temperature,
                max_tokens=max_tokens,
            )
            logger.info(f"Anthropic 客户端初始化: model={model}")

        return cls._instances[cache_key]

    @classmethod
    def get_default(cls):
        """获取默认 LLM 客户端"""
        if settings.default_llm_provider == "anthropic":
            return cls.get_anthropic()
        return cls.get_openai()

    @classmethod
    def get_client(cls, provider: str = "openai", model: str = "gpt-4o"):
        """
        便捷方法：获取 LLM 客户端
        用于其他模块的快速集成
        """
        if provider == "anthropic":
            return cls.get_anthropic(model=model)
        return cls.get_openai(model=model)


# 全局单例，方便其他模块直接引用
llm_factory = LLMFactory()
