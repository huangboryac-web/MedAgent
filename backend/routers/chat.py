from fastapi import APIRouter
from langchain_core.messages import HumanMessage

from logger import get_logger
from database.db import insert_chat_by_session_id
from database.semantic_cache import get_cache
from models import ChatRequest
from agents.workflow import app_graph

router = APIRouter()
logger = get_logger("Router:Chat")
cache = get_cache()

@router.post("/chat")
async def chat_endpoint(request: ChatRequest):
    logger.info(f"📩 Query [{request.session_id}]: {request.query}")
    
    insert_chat_by_session_id(request.session_id, request.query, "user")
    
    cached_ans = cache.check_cache(request.query)
    if cached_ans:
        logger.info("⚡ Cache Hit")
        answer = cached_ans
    else:
        try:
            inputs = {"messages": [HumanMessage(content=request.query)]}
            config = {"configurable": {"thread_id": request.session_id}}
            
            output = await app_graph.ainvoke(inputs, config=config)
            answer = output["messages"][-1].content
            
            if "System Error" not in answer:
                cache.update_cache(request.query, answer)
                
        except Exception as e:
            logger.error(f"Agent Failure: {e}", exc_info=True)
            answer = "I'm sorry, I encountered a system error. Please try again."

    insert_chat_by_session_id(request.session_id, answer, "assistant")
    
    return {"response": answer}