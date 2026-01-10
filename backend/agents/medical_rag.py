import logging
from typing import Dict, Any
from langchain_core.prompts import ChatPromptTemplate
from langchain_core.output_parsers import StrOutputParser, JsonOutputParser
from langchain_core.messages import AIMessage

from utils.llm_utils import safe_execute
from factories.llm_factory import LLMFactory
from config import get_settings
from database.vector_db import retrieve_documents, index_documents
from tools.web_search import perform_web_search
from logger import get_logger

logger = get_logger("MedicalRAG")
settings = get_settings()

try:
    llm = LLMFactory.create_llm(settings.llm_provider, settings.llm_model, temperature=0.0)
    logger.info("Medical RAG LLM Initialized")
except Exception as e:
    logger.critical(f"Medical RAG Init Failed: {e}")
    raise e

def retrieve_node(state: Dict[str, Any]):
    logger.info("🔍 --- NODE: Retrieve ---")
    query = state["messages"][-1].content
    docs = retrieve_documents(query)
    return {"documents": docs, "question": query}


batch_grader_prompt = ChatPromptTemplate.from_messages([
    ("system", """You are a Grader. 
    Evaluate retrieved documents for factual relevance to the user's question.
    Rules:
    - Score 'yes' if it contains the answer.
    - Score 'no' if tangential or unrelated.
    
    Return JSON with key 'scores' (list of 'yes'/'no').
    """),
    ("human", "Question: {question} \n\n Docs: \n {formatted_docs}")
])
batch_grader_chain = batch_grader_prompt | llm | JsonOutputParser()

async def grade_documents_node(state: Dict[str, Any]):
    logger.info("⚖️ --- NODE: Grader ---")
    question = state["question"]
    documents = state["documents"]
    
    if not documents:
        return {"documents": [], "is_answerable": False}
    
    formatted_docs = "\n".join([f"Doc {i}: {d.page_content}" for i, d in enumerate(documents)])
    
    try:
        response = await safe_execute(
            batch_grader_chain, 
            {"question": question, "formatted_docs": formatted_docs}
        )
        scores = response.get("scores", [])
        
        filtered_docs = [
            doc for i, doc in enumerate(documents) 
            if i < len(scores) and scores[i].lower() == "yes"
        ]
        
        is_answerable = len(filtered_docs) > 0
        logger.info(f"Grading: Kept {len(filtered_docs)}/{len(documents)} docs. Answerable: {is_answerable}")
        return {"documents": filtered_docs, "is_answerable": is_answerable}
        
    except Exception as e:
        logger.error(f"Grading Error: {e}", exc_info=True)
        return {"documents": documents, "is_answerable": True} 

reform_prompt = ChatPromptTemplate.from_messages([
    ("system", """Reformulate the user's question into a concise, effective web search query. 
    Focus on key terms, remove conversational filler, and optimize for medical accuracy.
    Output only the reformed query string."""),
    ("human", "{question}")
])
reform_chain = reform_prompt | llm | StrOutputParser()

async def web_search_node(state: Dict[str, Any]):
    logger.info("🌐 --- NODE: Web Search ---")
    question = state["question"]
    
    try:
        reformed_query = await safe_execute(reform_chain, {"question": question})
        logger.info(f"Reformed query: {reformed_query}")
    except Exception as e:
        logger.error(f"Query reform error: {e}. Using original.")
        reformed_query = question
    
    new_docs = perform_web_search(reformed_query)
    
    if new_docs:
        index_documents(new_docs)
        
    return {"documents": new_docs, "is_answerable": True}

generate_prompt = ChatPromptTemplate.from_messages([
    ("system", """Answer using the context. Cite sources.
    If unsure, say "I don't know".
    Context: {context}"""),
    ("human", "{question}")
])
generate_chain = generate_prompt | llm | StrOutputParser()

async def generate_node(state: Dict[str, Any]):
    logger.info("🧠 --- NODE: Generator ---")
    question = state["question"]
    documents = state["documents"]
    
    if not documents:
        return {"generation": "I couldn't find reliable medical information."}
    
    context_str = "\n\n".join([f"{d.page_content} (Source: {d.metadata.get('source','?')})" for d in documents])
    
    try:
        generation = await safe_execute(
            generate_chain, 
            {"context": context_str, "question": question}
        )
        return {"generation": generation}
    except Exception as e:
        logger.error(f"Generation Error: {e}", exc_info=True)
        return {"generation": "Error generating response."}


safety_prompt = ChatPromptTemplate.from_messages([
    ("system", """Check for safety violations:
    1. Dangerous/Illegal content.
    2. Hate speech.
    3. Specific medical diagnosis (advice is okay, diagnosis is not).
    
    Return JSON: {{"status": "SAFE" or "UNSAFE", "reason": "..."}}.
    """),
    ("human", "{generation}")
])
safety_chain = safety_prompt | llm | JsonOutputParser()

async def guardrail_node(state: Dict[str, Any]):
    logger.info("🛡️ --- NODE: Guardrail ---")
    generation = state.get("generation", "")
    
    if not generation: return {"messages": [AIMessage(content="Error: Empty response.")]}

    if any(k in generation.lower() for k in ["suicide", "kill yourself", "bomb"]):
        logger.warning("Blocked by Keyword.")
        return {"messages": [AIMessage(content="Request blocked due to safety guidelines.")]}

    try:
        res = await safe_execute(safety_chain, {"generation": generation})
        if res.get("status") == "UNSAFE":
            logger.warning(f"Blocked by LLM: {res.get('reason')}")
            return {"messages": [AIMessage(content="Response blocked by safety filters.")]}
    except Exception as e:
        logger.error(f"Guardrail Error: {e}")

    if "Disclaimer" not in generation:
        generation += "\n\n*Disclaimer: I am an AI. Consult a professional.*"
        
    return {"messages": [AIMessage(content=generation)]}