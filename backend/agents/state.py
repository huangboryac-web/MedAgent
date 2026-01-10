import operator
from typing import Annotated, TypedDict, List
from langchain_core.messages import BaseMessage
from langchain_core.documents import Document

class AgentState(TypedDict):
    # Chat History
    messages: Annotated[List[BaseMessage], operator.add]
    
    # Routing logic
    next: str
    
    # RAG Context
    question: str              # The extracted core user question
    documents: List[Document]  # Context retrieved from DB or Web
    is_answerable: bool        # Boolean flag from the Grader node
    generation: str            # The draft answer before guardrails
    
    # Add retry counter to prevent infinite loops
    retry_count: Annotated[int, operator.add] = 0  # Starts at 0, increments on hallucination