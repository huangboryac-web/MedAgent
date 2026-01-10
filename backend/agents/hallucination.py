from typing import Dict, Any
from langchain_core.prompts import ChatPromptTemplate
from langchain_core.output_parsers import JsonOutputParser

from factories.llm_factory import LLMFactory
from utils.llm_utils import safe_execute
from config import get_settings
from logger import get_logger
from constants import MAX_RETRIES

logger = get_logger("HallucinationChecker")
settings = get_settings()

try:
    llm = LLMFactory.create_llm(settings.llm_provider, settings.llm_model, temperature=0.0)
    logger.info("Hallucination Checker LLM Initialized")
except Exception as e:
    logger.critical(f"Hallucination Checker Init Failed: {e}")
    raise e

hallucination_prompt = ChatPromptTemplate.from_messages([
    ("system", """You are a hallucination grader. Given the question, context documents, and generated answer, determine if the answer contains any facts not supported by the context.
    
    Return JSON: {{"is_grounded": true/false, "reason": "brief explanation"}}
    """),
    ("human", "Question: {question}\n\nContext: {context}\n\nAnswer: {generation}")
])

hallucination_chain = hallucination_prompt | llm | JsonOutputParser()

async def hallucination_check_node(state: Dict[str, Any]):
    logger.info("🔍 --- NODE: Hallucination Checker ---")
    question = state["question"]
    documents = state["documents"]
    generation = state["generation"]
    retry_count = state.get("retry_count", 0)

    context_str = "\n\n".join([f"{d.page_content} (Source: {d.metadata.get('source', '?')})" for d in documents])

    if retry_count >= MAX_RETRIES:
        logger.warning(f"Max retries ({MAX_RETRIES}) reached. Forcing proceed despite potential hallucination.")
        return {"is_grounded": True, "retry_count": retry_count} 

    try:
        response = await safe_execute(
            hallucination_chain, 
            {"question": question, "context": context_str, "generation": generation}
        )
        is_grounded = response.get("is_grounded", True)
        reason = response.get("reason", "No issues detected.")
        logger.info(f"Hallucination Check: Grounded? {is_grounded} | Reason: {reason}")
        
        if not is_grounded:
            return {"is_grounded": False, "retry_count": retry_count + 1}  
        return {"is_grounded": True, "retry_count": retry_count}
    except Exception as e:
        logger.error(f"Hallucination Check Error: {e}", exc_info=True)
        return {"is_grounded": True, "retry_count": retry_count} 