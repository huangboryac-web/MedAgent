"""
Skill 管理器
管理和调度外部 Skill（deep-research、multi-search-engine、academic-search、summarize 等）
"""

from typing import Optional

from src.config import get_settings
from src.utils.logger import logger

settings = get_settings()


class SkillResult:
    """Skill 执行结果"""
    def __init__(self, skill_name: str, success: bool, data: Optional[dict] = None, error: Optional[str] = None):
        self.skill_name = skill_name
        self.success = success
        self.data = data or {}
        self.error = error


class SkillManager:
    """
    Skill 调度器
    负责管理和调用外部 Skill
    """

    # 可用 Skill 清单
    AVAILABLE_SKILLS = {
        "deep-research": {
            "description": "深度调研 - 多角度系统性研究",
            "input": {"query": "str", "depth": "int"},
            "output": {"report": "str", "sources": "list"},
        },
        "multi-search-engine": {
            "description": "多引擎搜索 - 同时查询多个搜索引擎",
            "input": {"query": "str", "engines": "list"},
            "output": {"results": "list"},
        },
        "academic-search": {
            "description": "学术搜索 - PubMed/Semantic Scholar 检索",
            "input": {"query": "str", "max_results": "int"},
            "output": {"papers": "list"},
        },
        "summarize": {
            "description": "摘要归档 - 对会话内容进行摘要生成",
            "input": {"text": "str"},
            "output": {"summary": "str"},
        },
        "web-access": {
            "description": "网页访问 - 搜索和抓取网页内容",
            "input": {"query": "str"},
            "output": {"content": "str", "urls": "list"},
        },
    }

    def __init__(self):
        self._skill_registry = self.AVAILABLE_SKILLS.copy()

    def list_skills(self) -> list[dict]:
        """列出所有可用 Skill"""
        return [
            {"name": name, "description": info["description"]}
            for name, info in self._skill_registry.items()
        ]

    def get_skill_info(self, skill_name: str) -> Optional[dict]:
        """获取 Skill 详细信息"""
        return self._skill_registry.get(skill_name)

    async def execute(
        self,
        skill_name: str,
        params: dict,
        use_skill_fn=None,
    ) -> SkillResult:
        """
        执行指定 Skill
        use_skill_fn: 可选的 use_skill 回调函数，用于调用外部 Skill
        """
        if skill_name not in self._skill_registry:
            return SkillResult(skill_name, False, error=f"未知 Skill: {skill_name}")

        logger.info(f"执行 Skill: {skill_name}, params={params}")

        try:
            if skill_name == "deep-research":
                return await self._run_deep_research(params, use_skill_fn)
            elif skill_name == "multi-search-engine":
                return await self._run_multi_search(params, use_skill_fn)
            elif skill_name == "academic-search":
                return await self._run_academic_search(params, use_skill_fn)
            elif skill_name == "summarize":
                return await self._run_summarize(params, use_skill_fn)
            elif skill_name == "web-access":
                return await self._run_web_access(params, use_skill_fn)
            else:
                return SkillResult(skill_name, False, error=f"Skill 未实现: {skill_name}")

        except Exception as e:
            logger.error(f"Skill 执行失败: {skill_name}, error={e}")
            return SkillResult(skill_name, False, error=str(e))

    async def _run_deep_research(self, params: dict, use_skill_fn=None) -> SkillResult:
        """执行深度调研 Skill"""
        if use_skill_fn:
            task = f"对以下医学问题进行深度调研: {params.get('query')}"
            result = await use_skill_fn(skill_name="deep-research", task=task)
            return SkillResult("deep-research", True, data={"report": str(result)})
        return SkillResult("deep-research", True, data={"report": f"深度调研: {params.get('query')}"})

    async def _run_multi_search(self, params: dict, use_skill_fn=None) -> SkillResult:
        """执行多引擎搜索 Skill"""
        if use_skill_fn:
            task = f"多引擎搜索以下医学问题: {params.get('query')}"
            result = await use_skill_fn(skill_name="multi-search-engine", task=task)
            return SkillResult("multi-search-engine", True, data={"results": str(result)})
        return SkillResult("multi-search-engine", True, data={"results": f"搜索结果: {params.get('query')}"})

    async def _run_academic_search(self, params: dict, use_skill_fn=None) -> SkillResult:
        """执行学术搜索 Skill"""
        if use_skill_fn:
            task = f"搜索以下医学术语的学术论文: {params.get('query')}, 最多{params.get('max_results', 5)}篇"
            result = await use_skill_fn(skill_name="academic-search", task=task)
            return SkillResult("academic-search", True, data={"papers": str(result)})
        return SkillResult("academic-search", True, data={"papers": f"学术检索: {params.get('query')}"})

    async def _run_summarize(self, params: dict, use_skill_fn=None) -> SkillResult:
        """执行摘要归档 Skill"""
        text = params.get("text", "")
        if not text:
            return SkillResult("summarize", False, error="缺少文本内容")

        if use_skill_fn:
            task = f"请总结以下会话内容: {text[:500]}"
            result = await use_skill_fn(skill_name="summarize", task=task)
            return SkillResult("summarize", True, data={"summary": str(result)})

        # 简单规则摘要
        summary = f"会话摘要：共 {len(text)} 字符，涉及医疗健康咨询"
        return SkillResult("summarize", True, data={"summary": summary})

    async def _run_web_access(self, params: dict, use_skill_fn=None) -> SkillResult:
        """执行网页访问 Skill"""
        if use_skill_fn:
            task = f"搜索并获取关于以下内容的网页信息: {params.get('query')}"
            result = await use_skill_fn(skill_name="web-access", task=task)
            return SkillResult("web-access", True, data={"content": str(result)})
        return SkillResult("web-access", True, data={"content": f"网页访问: {params.get('query')}"})


# 全局单例
skill_manager = SkillManager()
