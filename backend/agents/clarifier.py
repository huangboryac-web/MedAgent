import logging
from typing import Dict, Any
from langchain_core.prompts import ChatPromptTemplate
from langchain_core.output_parsers import StrOutputParser
from langchain_core.messages import AIMessage

from utils.llm_utils import safe_execute
from factories.llm_factory import LLMFactory
from config import get_settings
from logger import get_logger

logger = get_logger("Clarifier")
settings = get_settings()

try:
    llm = LLMFactory.create_llm(settings.llm_provider, settings.llm_model, temperature=0.7)
    logger.info(f"Initialized Clarifier LLM with {settings.llm_provider}")
except Exception as e:
    logger.critical(f"Failed to initialize LLM for Clarifier: {e}")
    raise e

clarify_prompt = ChatPromptTemplate.from_messages([
    ("system", """You are a helpful medical assistant.
    The user has asked a medical question that is too vague or missing key details (like the drug name, condition, or patient context).
    
    Your goal is to politely ask follow-up questions to gather the missing information so you can provide an accurate answer later.
    Do not attempt to answer the medical question yet. Just ask for clarification.
    """),
    ("placeholder", "{messages}")
])

clarify_chain = clarify_prompt | llm | StrOutputParser()

async def clarify_node(state: Dict[str, Any]):
    logger.info("🟢 --- NODE: Clarifier Activated ---")
    try:
        last_message = state["messages"][-1].content
        logger.debug(f"Clarifying query: '{last_message[:50]}...'")
        
        response = await safe_execute(
            clarify_chain, 
            {"messages": state["messages"]}
        )
        logger.info("✅ Clarification request generated.")
        
        return {"messages": [AIMessage(content=response)]}
    except Exception as e:
        logger.error(f"❌ Clarifier failed: {e}", exc_info=True)
        return {"messages": [AIMessage(content="Could you please provide more specific details about your question?")]}