import os
from langchain_core.language_models.chat_models import BaseChatModel

from config import get_settings
from utils.ollama_cleaner import CleanChatOllama

settings = get_settings()

try:
    from langchain_google_genai import ChatGoogleGenerativeAI
except ImportError:
    ChatGoogleGenerativeAI = None

try:
    from langchain_ollama import ChatOllama
except ImportError:
    ChatOllama = None

try:
    from langchain_openai import ChatOpenAI
except ImportError:
    ChatOpenAI = None

class LLMFactory:
    @staticmethod
    def create_llm(provider: str, model_name: str, temperature: float = 0.0) -> BaseChatModel:
        provider = provider.lower()

        if provider == "vertex":
            if not ChatGoogleGenerativeAI:
                raise ImportError("langchain-google-genai is not installed.")
            
            if settings.google_application_credentials:
                os.environ["GOOGLE_APPLICATION_CREDENTIALS"] = settings.google_application_credentials
            
            project_id = settings.vertex_project_id or os.getenv("VERTEX_PROJECT_ID")
            if not project_id:
                raise ValueError("Vertex AI requires a PROJECT_ID in .env")

            return ChatGoogleGenerativeAI(
                model=model_name, 
                temperature=temperature,
                project=project_id,
                convert_system_message_to_human=True
            )
        
        elif provider == "ollama":
            if not ChatOllama:
                raise ImportError("langchain-ollama is not installed.")
            return CleanChatOllama(
                model=model_name, 
                temperature=temperature
            )
        
        elif provider == "openai":
            if not ChatOpenAI:
                raise ImportError("langchain-openai is not installed.")
            
            api_key = settings.openai_api_key or os.getenv("OPENAI_API_KEY")
            if not api_key:
                raise ValueError("OpenAI API Key is missing.")

            return ChatOpenAI(
                model=model_name, 
                temperature=temperature, 
                api_key=api_key
            )
        
        else:
            raise ValueError(f"Unsupported LLM provider: {provider}")