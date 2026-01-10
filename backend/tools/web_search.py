import os
from typing import List
from langchain_community.tools.tavily_search import TavilySearchResults
from langchain_core.documents import Document

from config import get_settings
from logger import get_logger

logger = get_logger("Tools")
settings = get_settings()

if not settings.tavily_api_key:
    logger.warning("TAVILY_API_KEY is not set. Web search will fail.")
else:
    os.environ["TAVILY_API_KEY"] = settings.tavily_api_key

tavily_tool = TavilySearchResults(
    max_results=3,
    search_depth="advanced",
    include_answer=True,
    include_raw_content=True
)

def perform_web_search(query: str) -> List[Document]:
    try:
        logger.info(f"Searching web for: {query}")
        results = tavily_tool.invoke({"query": query})
        
        documents = []
        for result in results:
            content = result.get("content", "")
            url = result.get("url", "")
            
            if not content or len(content) < 50:
                continue

            doc = Document(
                page_content=content,
                metadata={
                    "source": url, 
                    "type": "web_search",
                    "query_context": query
                }
            )
            documents.append(doc)
            
        return documents
    except Exception as e:
        logger.error(f"Error performing web search: {e}")
        return []