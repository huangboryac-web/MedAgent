from typing import Dict, Any
from langchain_core.prompts import ChatPromptTemplate
from langchain_core.output_parsers import StrOutputParser

from utils.llm_utils import safe_execute
from logger import get_logger
from factories.llm_factory import LLMFactory
from config import get_settings

logger = get_logger("Router")
settings = get_settings()

try:
    llm = LLMFactory.create_llm(settings.llm_provider, settings.llm_model, temperature=0.0)
    logger.info("Router LLM Initialized")
except Exception as e:
    logger.critical(f"Router Init Failed: {e}")
    raise e

router_prompt = ChatPromptTemplate.from_messages([
    ("system", """You are an intent classifier.
    Categories:
    1. 'medical': Symptoms, drugs, treatments, biology.
    2. 'general': Greetings, identity, small talk.
    3. 'incomplete': Vague medical queries needing clarification (e.g., "Is it safe?", "Dosage?").
    
    Return ONLY: 'medical', 'general', or 'incomplete'."""),
    ("human", "{query}")
])

router_chain = router_prompt | llm | StrOutputParser()

async def route_query(state: Dict[str, Any]):
    logger.info("🚦 --- NODE: Router ---")
    query = state["messages"][-1].content
    
    try:
        category = await safe_execute(
            router_chain, 
            {"query": query}
        )
        logger.info(f"Routing '{query[:30]}...' -> {category.upper()}")
        
        if "medical" in category: return {"next": "medical"}
        if "incomplete" in category: return {"next": "incomplete"}
        return {"next": "general"}
        
    except Exception as e:
        logger.error(f"Router Classification Error: {e}", exc_info=True)
        return {"next": "general"}