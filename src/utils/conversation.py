"""
会话管理器
管理对话历史、上下文窗口、会话摘要
"""

from datetime import datetime, timezone
from typing import Optional

from src.utils.logger import logger


class ConversationTurn:
    """对话轮次"""
    def __init__(self, role: str, content: str, metadata: Optional[dict] = None):
        self.role = role  # user / assistant / system
        self.content = content
        self.timestamp = datetime.now(timezone.utc)
        self.metadata = metadata or {}

    def to_dict(self) -> dict:
        return {
            "role": self.role,
            "content": self.content,
            "timestamp": self.timestamp.isoformat(),
            "metadata": self.metadata,
        }


class ConversationManager:
    """对话历史管理器"""

    MAX_TURNS = 20  # 最大保留轮次
    SUMMARY_TRIGGER = 10  # 超过此轮数触发摘要

    def __init__(self, session_id: str):
        self.session_id = session_id
        self.turns: list[ConversationTurn] = []
        self.summary: Optional[str] = None
        self.created_at = datetime.now(timezone.utc)

    def add_turn(self, role: str, content: str, metadata: Optional[dict] = None):
        """添加一轮对话"""
        turn = ConversationTurn(role=role, content=content, metadata=metadata)
        self.turns.append(turn)

        # 超限时自动裁剪
        if len(self.turns) > self.MAX_TURNS:
            removed = self.turns.pop(0)
            logger.debug(f"对话轮次超限，移除最早轮次: {removed.role} @ {removed.timestamp}")

    def get_context(self, max_turns: int = 10) -> list[dict]:
        """获取最近 N 轮对话上下文"""
        recent = self.turns[-max_turns:]
        return [t.to_dict() for t in recent]

    def get_history(self) -> list[dict]:
        """获取完整对话历史"""
        return [t.to_dict() for t in self.turns]

    def should_summarize(self) -> bool:
        """判断是否需要生成摘要"""
        return len(self.turns) >= self.SUMMARY_TRIGGER and self.summary is None

    async def generate_summary(self, llm_client=None) -> str:
        """生成对话摘要（需要 LLM 客户端）"""
        if not self.turns:
            return "无对话记录"

        if llm_client is None:
            # 简单规则摘要
            topics = set()
            for turn in self.turns:
                if turn.role == "user":
                    # 提取关键词
                    keywords = ["头疼", "发烧", "咳嗽", "胃疼", "过敏", "血压", "血糖"]
                    for kw in keywords:
                        if kw in turn.content:
                            topics.add(kw)

            summary_parts = [f"对话共 {len(self.turns)} 轮"]
            if topics:
                summary_parts.append(f"涉及健康话题: {', '.join(topics)}")
            self.summary = "；".join(summary_parts)
            return self.summary

        # 使用 LLM 生成摘要
        context = self.get_context(max_turns=10)
        messages = [
            {"role": "system", "content": "请将以下对话总结为一段话，重点提取用户的健康问题和关键信息。"},
            {"role": "user", "content": str(context)},
        ]
        response = await llm_client.ainvoke(messages)
        self.summary = response.content
        return self.summary

    @property
    def turn_count(self) -> int:
        return len(self.turns)

    @property
    def is_empty(self) -> bool:
        return len(self.turns) == 0


# 全局会话注册表（简化版，生产应使用 Redis）
_sessions: dict[str, ConversationManager] = {}


def get_or_create_session(session_id: str) -> ConversationManager:
    """获取或创建会话"""
    if session_id not in _sessions:
        _sessions[session_id] = ConversationManager(session_id)
        logger.info(f"创建新会话: {session_id}")
    return _sessions[session_id]


def remove_session(session_id: str):
    """移除会话"""
    if session_id in _sessions:
        del _sessions[session_id]
        logger.info(f"移除会话: {session_id}")
