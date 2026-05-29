"""
增强型知识检索服务
集成外部 Skill 进行深度信息检索
"""

from typing import Optional

from src.knowledge.retriever import KnowledgeRetriever
from src.skills.integration import skill_integration
from src.utils.logger import logger


class EnhancedKnowledgeRetriever(KnowledgeRetriever):
    """增强型知识检索器，集成外部 Skill"""

    async def retrieve_enhanced(
        self,
        query: str,
        intent: str = "medical",
        use_external_skills: bool = True,
    ) -> dict:
        """
        增强检索：结合向量库和外部 Skill
        """
        # 1. 基础向量检索
        base_results = await self.retrieve(query, top_k=3)

        if not use_external_skills:
            return base_results

        # 2. 根据意图选择外部 Skill
        external_results = []
        if intent == "medical":
            # 医疗意图：深度调研 + 学术搜索
            tasks = [
                self._run_deep_research(query),
                self._run_academic_search(query),
            ]
            results = await asyncio.gather(*tasks, return_exceptions=True)
            for result in results:
                if isinstance(result, Exception):
                    logger.error(f"Skill 执行异常: {result}")
                    continue
                if result.success:
                    external_results.append(result.data)
        elif intent == "general":
            # 通用意图：多引擎搜索
            result = await self._run_multi_search(query)
            if result.success:
                external_results.append(result.data)
        else:
            # 其他意图：网页访问
            result = await self._run_web_access(query)
            if result.success:
                external_results.append(result.data)

        # 3. 合并结果
        combined = {
            "query": query,
            "intent": intent,
            "vector_results": base_results.get("results", []),
            "external_skill_results": external_results,
            "total_sources": len(base_results.get("results", [])) + len(external_results),
        }

        return combined

    async def _run_deep_research(self, query: str):
        """执行深度调研"""
        return await skill_integration.deep_research(query)

    async def _run_multi_search(self, query: str):
        """执行多引擎搜索"""
        return await skill_integration.multi_search(query)

    async def _run_academic_search(self, query: str):
        """执行学术搜索"""
        return await skill_integration.academic_search(query)

    async def _run_web_access(self, query: str):
        """执行网页访问"""
        return await skill_integration.web_access(query)


# 全局单例
enhanced_retriever = EnhancedKnowledgeRetriever()
