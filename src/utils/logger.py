"""
MedAgent 结构化日志系统
基于 loguru，支持 JSON 格式输出和生产级日志轮转
"""

import sys
from pathlib import Path

from loguru import logger

from src.config import get_settings

settings = get_settings()

# 移除默认 handler
logger.remove()

# 开发环境：彩色终端输出
if settings.app_env == "development":
    logger.add(
        sys.stderr,
        level=settings.log_level,
        format=(
            "<green>{time:HH:mm:ss}</green> | "
            "<level>{level: <8}</level> | "
            "<cyan>{name}</cyan>:<cyan>{function}</cyan>:<cyan>{line}</cyan> | "
            "<level>{message}</level>"
        ),
        colorize=True,
    )
else:
    # 生产环境：JSON 格式 + 文件轮转
    log_dir = Path(__file__).resolve().parent.parent.parent / "logs"
    log_dir.mkdir(exist_ok=True)

    logger.add(
        log_dir / "medagent_{time:YYYY-MM-DD}.log",
        level=settings.log_level,
        format="{time} | {level} | {name}:{function}:{line} | {message}",
        rotation="00:00",  # 每天午夜轮转
        retention="30 days",
        compression="gz",
        serialize=True,  # JSON 格式
    )

    # 控制台保留 ERROR 级别
    logger.add(sys.stderr, level="ERROR", format="<red>{level}</red> | {message}")


def get_logger():
    """获取 logger 实例"""
    return logger


__all__ = ["logger", "get_logger"]
