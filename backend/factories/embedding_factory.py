import os
import logging
from langchain_core.embeddings import Embeddings

from config import get_settings
from logger import get_logger

logger = get_logger("EmbeddingFactory")
settings = get_settings()

try:
    from langchain_huggingface import HuggingFaceEmbeddings
except ImportError:
    HuggingFaceEmbeddings = None

try:
    from langchain_ollama import OllamaEmbeddings
except ImportError:
    OllamaEmbeddings = None

try:
    from langchain_openai import OpenAIEmbeddings
except ImportError:
    OpenAIEmbeddings = None

try:
    from langchain_google_vertexai import VertexAIEmbeddings
except ImportError:
    VertexAIEmbeddings = None

def get_embedding_model() -> Embeddings:
    provider = settings.llm_provider.lower()
    logger.info(f"Initializing Embeddings for provider: {provider}")

    try:
        if provider == "openai":
            if not OpenAIEmbeddings: raise ImportError("langchain-openai missing")
            return OpenAIEmbeddings(
                model="text-embedding-3-small", 
                api_key=settings.openai_api_key or os.getenv("OPENAI_API_KEY")
            )
        
        elif provider == "vertex":
            if not VertexAIEmbeddings: raise ImportError("langchain-google-vertexai missing")
            if settings.google_application_credentials:
                os.environ["GOOGLE_APPLICATION_CREDENTIALS"] = settings.google_application_credentials
            return VertexAIEmbeddings(model="gemini-embedding-001")
            
        elif provider == "ollama":
            if not OllamaEmbeddings: raise ImportError("langchain-ollama missing")
            return OllamaEmbeddings(model="nomic-embed-text")
            
        else:
            if not HuggingFaceEmbeddings: raise ImportError("langchain-huggingface missing")
            logger.info("Using Local HuggingFace Fallback")
            return HuggingFaceEmbeddings(model_name="sentence-transformers/all-MiniLM-L6-v2")

    except Exception as e:
        logger.error(f"Failed to load {provider} embeddings: {e}. Falling back to HuggingFace.")
        if HuggingFaceEmbeddings:
            return HuggingFaceEmbeddings(model_name="sentence-transformers/all-MiniLM-L6-v2")
        raise RuntimeError("No embedding libraries available.")