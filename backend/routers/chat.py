import json
from fastapi import APIRouter
from fastapi.responses import StreamingResponse
from langchain_core.messages import HumanMessage

from logger import get_logger
from database.db import insert_chat_by_session_id
from database.semantic_cache import get_cache
from models import ChatRequest
from agents.workflow import get_app_graph

router = APIRouter()
logger = get_logger("Router:Chat")
cache = get_cache()

@router.post("/chat")
async def chat_endpoint(request: ChatRequest):
    logger.info(f"📩 Query [{request.session_id}]: {request.query}")
    insert_chat_by_session_id(request.session_id, request.query, "user")

    async def event_generator():
        cached_ans = await cache.check_cache(request.query)
        if cached_ans:
            logger.info("⚡ Cache Hit")
            yield f"data: {json.dumps({'type': 'step', 'node': 'cache'})}\n\n"
            yield f"data: {json.dumps({'type': 'answer', 'content': cached_ans})}\n\n"
            return

        try:
            inputs = {"messages": [HumanMessage(content=request.query)]}
            config = {
                "configurable": {"thread_id": request.session_id},
                "metadata": {"user_id": "user", "session_id": request.session_id} 
            }
            graph = get_app_graph()

            if graph is None:
                yield f"data: {json.dumps({'type': 'error', 'content': 'Graph not initialized'})}\n\n"
                return

            final_answer = ""
            async for output in graph.astream(inputs, config=config, stream_mode="updates"):
                for node_name, state_update in output.items():
                    
                    yield f"data: {json.dumps({'type': 'step', 'node': node_name})}\n\n"
                    
                    if node_name in ["generate", "guardrail", "general", "clarifier"]:
                         if "messages" in state_update:
                             final_answer = state_update["messages"][-1].content

            if final_answer:
                await cache.update_cache(request.query, final_answer)
                insert_chat_by_session_id(request.session_id, final_answer, "assistant")
                yield f"data: {json.dumps({'type': 'answer', 'content': final_answer})}\n\n"
            
        except Exception as e:
            logger.error(f"Agent Failure: {e}", exc_info=True)
            yield f"data: {json.dumps({'type': 'error', 'content': str(e)})}\n\n"

    return StreamingResponse(event_generator(), media_type="text/event-stream")