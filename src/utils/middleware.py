"""
异常处理中间件
提供全局异常捕获、标准化错误响应格式
"""

from fastapi import Request
from fastapi.responses import JSONResponse
from starlette.middleware.base import BaseHTTPMiddleware

from src.utils.logger import logger


class ExceptionHandlerMiddleware(BaseHTTPMiddleware):
    """全局异常处理中间件 - 捕获未处理的异常并返回标准化响应"""

    async def dispatch(self, request: Request, call_next):
        try:
            response = await call_next(request)
            return response
        except Exception as exc:
            logger.error(f"未处理异常 [{request.method} {request.url.path}]: {exc}")

            return JSONResponse(
                status_code=500,
                content={
                    "error": "server_error",
                    "message": "服务器内部错误，请稍后重试",
                    "detail": str(exc) if request.app.debug else None,
                },
            )
