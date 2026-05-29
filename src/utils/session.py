"""
Redis 会话持久化
管理 Agent 会话状态的存储与恢复
"""

import json
from typing import Optional

import redis.asyncio as aioredis

from src.config import get_settings
from src.utils.logger import logger

settings = get_settings()


class SessionStore:
    """会话存储管理器"""

    def __init__(self):
        self._redis: Optional[aioredis.Redis] = None
        self._prefix = "medagent:session:"
        self._ttl = 3600  # 会话过期时间 1 小时

    async def connect(self):
        """连接 Redis"""
        try:
            self._redis = await aioredis.from_url(
                settings.redis_url,
                encoding="utf-8",
                decode_responses=True,
            )
            await self._redis.ping()
            logger.info("Redis 会话存储连接成功")
        except Exception as e:
            logger.warning(f"Redis 连接失败，使用内存存储: {e}")
            self._redis = None

    async def disconnect(self):
        """断开 Redis 连接"""
        if self._redis:
            await self._redis.close()
            logger.info("Redis 会话存储已断开")

    async def save(self, session_id: str, data: dict) -> bool:
        """保存会话数据"""
        key = f"{self._prefix}{session_id}"
        try:
            if self._redis:
                await self._redis.setex(key, self._ttl, json.dumps(data, ensure_ascii=False))
            return True
        except Exception as e:
            logger.error(f"保存会话失败: {e}")
            return False

    async def load(self, session_id: str) -> Optional[dict]:
        """加载会话数据"""
        key = f"{self._prefix}{session_id}"
        try:
            if self._redis:
                data = await self._redis.get(key)
                if data:
                    return json.loads(data)
        except Exception as e:
            logger.error(f"加载会话失败: {e}")
        return None

    async def delete(self, session_id: str) -> bool:
        """删除会话数据"""
        key = f"{self._prefix}{session_id}"
        try:
            if self._redis:
                await self._redis.delete(key)
            return True
        except Exception as e:
            logger.error(f"删除会话失败: {e}")
            return False

    async def exists(self, session_id: str) -> bool:
        """检查会话是否存在"""
        key = f"{self._prefix}{session_id}"
        try:
            if self._redis:
                return await self._redis.exists(key) > 0
        except Exception:
            pass
        return False


# 全局单例
session_store = SessionStore()
