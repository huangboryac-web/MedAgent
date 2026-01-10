from langgraph.graph import StateGraph, END
from langgraph.checkpoint.memory import MemorySaver

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


workflow = StateGraph(AgentState)

checkpointer = MemorySaver()


workflow.add_node("router", route_query)
workflow.add_node("general", general_node)
workflow.add_node("clarifier", clarify_node)


workflow.add_node("retrieve", retrieve_node)
workflow.add_node("grade", grade_documents_node)
workflow.add_node("web_search", web_search_node)
workflow.add_node("generate", generate_node)
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
    if state["is_answerable"]:
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
workflow.add_edge("generate", "guardrail")
workflow.add_edge("guardrail", END)


app_graph = workflow.compile(checkpointer=checkpointer)