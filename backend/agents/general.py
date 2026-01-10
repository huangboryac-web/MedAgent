import logging
from typing import Dict, Any
from langchain_core.prompts import ChatPromptTemplate
from langchain_core.output_parsers import StrOutputParser
from langchain_core.messages import AIMessage

from utils.llm_utils import safe_execute
from factories.llm_factory import LLMFactory
from config import get_settings
from logger import get_logger

logger = get_logger("GeneralAgent")
settings = get_settings()

try:
    llm = LLMFactory.create_llm(settings.llm_provider, settings.llm_model, temperature=0.7)
    logger.info(f"Initialized General Agent LLM with {settings.llm_provider}")
except Exception as e:
    logger.critical(f"Failed to initialize LLM for General Agent: {e}")
    raise e

general_prompt = ChatPromptTemplate.from_messages([
    ("system", """You are 'MedAgent', a helpful AI medical assistant.
    
    Your Role:
    - Handle greetings (e.g., "Hi", "Hello") warmly.
    - Answer questions about what you can do.
    - Politely decline off-topic requests.
    
    Keep responses concise and professional.
    """),
    ("placeholder", "{messages}")
])

general_chain = general_prompt | llm | StrOutputParser()

async def general_node(state: Dict[str, Any]):
    logger.info("🔵 --- NODE: General Agent Activated ---")
    try:
        response = await safe_execute(
            general_chain, 
            {"messages": state["messages"]}
        )
        logger.info("✅ General response generated.")
        return {"messages": [AIMessage(content=response)]}
    except Exception as e:
        logger.error(f"❌ General Agent failed: {e}", exc_info=True)
        return {"messages": [AIMessage(content="I'm having trouble connecting right now.")]}