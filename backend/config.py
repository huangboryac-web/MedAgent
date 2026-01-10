from typing import Optional
from functools import lru_cache
from pydantic_settings import BaseSettings, SettingsConfigDict

class Settings(BaseSettings):
    website_host: str = "http://localhost:5173"
    test: bool = False

    redis_host: str = "localhost"
    redis_port: int = 6379

    tavily_api_key: Optional[str] = None

    llm_provider: str = "ollama" 
    llm_model: str = "llama3"

    openai_api_key: Optional[str] = None
    
    google_application_credentials: Optional[str] = None
    vertex_project_id: Optional[str] = None

    model_config = SettingsConfigDict(env_file=".env", extra="ignore")

@lru_cache
def get_settings():
    return Settings()