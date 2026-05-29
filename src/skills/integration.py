"""
Phase 3: 外部 Skill 集成与 API 增强
实现 deep-research、multi-search-engine、academic-search 等 Skill 的实际调用
"""

import asyncio
from typing import Optional

from src.skills.manager import skill_manager, SkillResult
from src.utils.logger import logger


class SkillIntegrationService:
    """Skill 集成服务"""

    def __init__(self):
        self._use_skill_callback = None

    def register_callback(self, callback):
        """注册 use_skill 回调函数"""
        self._use_skill_callback = callback
        logger.info("Skill 回调函数已注册")

    async def execute_skill(
        self,
        skill_name: str,
        params: dict,
        timeout: int = 30,
    ) -> SkillResult:
        """
        执行 Skill 并处理超时
        """
        if not self._use_skill_callback:
            return SkillResult(
                skill_name,
                False,
                error="Skill 回调函数未注册，无法执行外部 Skill",
            )

        try:
            # 执行 Skill
            result = await asyncio.wait_for(
                skill_manager.execute(skill_name, params, self._use_skill_callback),
                timeout=timeout,
            )
            return result
        except asyncio.TimeoutError:
            logger.error(f"Skill 执行超时: {skill_name}, timeout={timeout}s")
            return SkillResult(
                skill_name,
                False,
                error=f"Skill 执行超时（{timeout}s）",
            )
        except Exception as e:
            logger.error(f"Skill 执行异常: {skill_name}, error={e}")
            return SkillResult(
                skill_name,
                False,
                error=f"Skill 执行失败: {str(e)}",
            )

    async def deep_research(
        self,
        query: str,
        depth: int = 2,
    ) -> SkillResult:
        """
        深度调研 Skill
        """
        params = {
            "query": query,
            "depth": depth,
        }
        return await self.execute_skill("deep-research", params)

    async def multi_search(
        self,
        query: str,
        engines: Optional[list] = None,
    ) -> SkillResult:
        """
        多引擎搜索 Skill
        """
        params = {
            "query": query,
            "engines": engines or ["google", "bing", "baidu", "duckduckgo"],
        }
        return await self.execute_skill("multi-search-engine", params)

    async def academic_search(
        self,
        query: str,
        max_results: int = 5,
    ) -> SkillResult:
        """
        学术搜索 Skill
        """
        params = {
            "query": query,
            "max_results": max_results,
        }
        return await self.execute_skill("academic-search", params)

    async def summarize_text(
        self,
        text: str,
    ) -> SkillResult:
        """
        摘要归档 Skill
        """
        params = {
            "text": text,
        }
        return await self.execute_skill("summarize", params)

    async def web_access(
        self,
        query: str,
    ) -> SkillResult:
        """
        网页访问 Skill
        """
        params = {
            "query": query,
        }
        return await self.execute_skill("web-access", params)


# 全局单例
skill_integration = SkillIntegrationService()
