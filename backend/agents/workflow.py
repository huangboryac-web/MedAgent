from contextlib import asynccontextmanager
from langgraph.graph import StateGraph, END
from langgraph.checkpoint.redis.aio import AsyncRedisSaver

from agents.state import AgentState
from agents.router import route_query
from agents.general import general_node
from agents.clarifier import clarify_node 
from agents.medical_rag import (
    retrieve_node, 
    grade_documents_node, 
    web_search_node, 
    generate_node,
    guardrail_node
)
from agents.hallucination import hallucination_check_node
from constants import REDIS_HOST, REDIS_PORT, REDIS_AGENT_CACHE, MAX_RETRIES
from logger import get_logger

logger = get_logger("Workflow")

app_graph = None

@asynccontextmanager
async def init_workflow():
    global app_graph
    redis_url = f"redis://{REDIS_HOST}:{REDIS_PORT}/{REDIS_AGENT_CACHE}"

    async with AsyncRedisSaver.from_conn_string(redis_url) as saver:
        await saver.asetup()
        app_graph = workflow.compile(checkpointer=saver)
        yield saver

def get_app_graph():
    global app_graph
    return app_graph

workflow = StateGraph(AgentState)

workflow.add_node("router", route_query)
workflow.add_node("general", general_node)
workflow.add_node("clarifier", clarify_node)
workflow.add_node("retrieve", retrieve_node)
workflow.add_node("grade", grade_documents_node)
workflow.add_node("web_search", web_search_node)
workflow.add_node("generate", generate_node)
workflow.add_node("hallucination_check", hallucination_check_node)
workflow.add_node("guardrail", guardrail_node)

workflow.set_entry_point("router")

workflow.add_conditional_edges(
    "router",
    lambda state: state["next"],
    {
        "medical": "retrieve",
        "general": "general",
        "incomplete": "clarifier"
    }
)

workflow.add_edge("general", END)
workflow.add_edge("clarifier", END) 
workflow.add_edge("retrieve", "grade")

def check_relevance(state):
    if state.get("is_answerable", False):
        return "generate"
    return "web_search"

workflow.add_conditional_edges(
    "grade",
    check_relevance,
    {
        "generate": "generate",
        "web_search": "web_search"
    }
)

workflow.add_edge("web_search", "generate")
workflow.add_edge("generate", "hallucination_check")

def check_hallucination(state):
    if state.get("is_grounded", True):
        return "guardrail"
    
    if state.get("retry_count", 0) >= MAX_RETRIES:
        logger.warning("Max retries reached. Moving to guardrails.")
        return "guardrail"
        
    logger.warning("🚨 Hallucination detected - looping back to web search.")
    return "web_search" 

workflow.add_conditional_edges(
    "hallucination_check",
    check_hallucination,
    {
        "guardrail": "guardrail",
        "web_search": "web_search"
    }
)

workflow.add_edge("guardrail", END)
