import asyncio
import inspect
from typing import Any, Dict

from constants import MAX_RETRIES
from logger import get_logger

logger = get_logger("TaskRunner")

async def safe_execute(
    task: Any, 
    inputs: Dict[str, Any], 
    timeout: int = 60, 
    retries: int = MAX_RETRIES
) -> Any:
    for attempt in range(retries):
        try:
            if hasattr(task, "ainvoke"): # LangChain Async
                coro = task.ainvoke(inputs)
            elif inspect.iscoroutinefunction(task): # Standard Async Def
                coro = task(inputs)
            elif hasattr(task, "invoke"): # LangChain Sync
                coro = asyncio.to_thread(task.invoke, inputs)
            else: # Standard Sync Def
                coro = asyncio.to_thread(task, inputs)

            return await asyncio.wait_for(coro, timeout=timeout)

        except asyncio.TimeoutError:
            logger.warning(f"⏰ Timeout on attempt {attempt + 1}")
        except Exception as e:
            logger.error(f"❌ Execution failed: {e}")
            if attempt == retries - 1:
                raise e
                
    raise asyncio.TimeoutError("Task exceeded time limits after retries.")