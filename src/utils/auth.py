"""
用户认证中间件
提供 API Key 和 JWT Token 两种认证方式
"""

import hashlib
import hmac
import time
from typing import Optional, Tuple

from fastapi import Header, HTTPException, Request, status

from src.config import get_settings
from src.utils.logger import logger

settings = get_settings()


class AuthService:
    """认证服务"""

    # 简单的 API Key 存储（生产环境应使用数据库）
    _api_keys: dict[str, dict] = {}

    @classmethod
    def register_api_key(cls, key: str, user_id: str, permissions: list[str] = None):
        """注册 API Key"""
        cls._api_keys[key] = {
            "user_id": user_id,
            "permissions": permissions or ["read", "chat"],
            "created_at": time.time(),
        }

    @classmethod
    def verify_api_key(cls, api_key: str) -> Optional[dict]:
        """验证 API Key"""
        return cls._api_keys.get(api_key)

    @classmethod
    def revoke_api_key(cls, api_key: str):
        """撤销 API Key"""
        cls._api_keys.pop(api_key, None)


async def verify_api_key(
    request: Request,
    x_api_key: Optional[str] = Header(None, alias="X-API-Key"),
    authorization: Optional[str] = Header(None),
) -> Tuple[Optional[str], Optional[dict]]:
    """
    验证 API Key 或 Bearer Token
    返回 (user_id, auth_info) 或 (None, None)
    """
    # 尝试 API Key 方式
    if x_api_key:
        auth_info = AuthService.verify_api_key(x_api_key)
        if auth_info:
            logger.info(f"API Key 认证成功: user_id={auth_info['user_id']}")
            return auth_info["user_id"], auth_info

    # 尝试 Bearer Token 方式
    if authorization and authorization.startswith("Bearer "):
        token = authorization[7:]
        auth_info = AuthService.verify_api_key(token)  # 简化实现
        if auth_info:
            logger.info(f"Bearer Token 认证成功: user_id={auth_info['user_id']}")
            return auth_info["user_id"], auth_info

    # 开发环境允许匿名访问
    if settings.app_env == "development":
        return "anonymous", {"user_id": "anonymous", "permissions": ["read", "chat"]}

    raise HTTPException(
        status_code=status.HTTP_401_UNAUTHORIZED,
        detail="无效的认证凭据，请提供有效的 X-API-Key 或 Bearer Token",
    )


class RateLimiter:
    """简单的速率限制器"""

    def __init__(self, max_requests: int = 60, window_seconds: int = 60):
        self.max_requests = max_requests
        self.window_seconds = window_seconds
        self._requests: dict[str, list[float]] = {}

    def is_allowed(self, client_id: str) -> bool:
        """检查是否允许请求"""
        now = time.time()
        cutoff = now - self.window_seconds

        # 清理过期请求
        if client_id in self._requests:
            self._requests[client_id] = [
                req_time for req_time in self._requests[client_id]
                if req_time > cutoff
            ]
        else:
            self._requests[client_id] = []

        # 检查请求数
        if len(self._requests[client_id]) >= self.max_requests:
            logger.warning(f"速率限制触发: client_id={client_id}, requests={len(self._requests[client_id])}")
            return False

        self._requests[client_id].append(now)
        return True

    def get_remaining(self, client_id: str) -> int:
        """获取剩余请求数"""
        if client_id not in self._requests:
            return self.max_requests
        return max(0, self.max_requests - len(self._requests[client_id]))


# 全局实例
auth_service = AuthService()
rate_limiter = RateLimiter()
