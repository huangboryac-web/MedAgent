from config import get_settings

settings = get_settings()

APP_TITLE = "Medical Knowledge Agent"
DB_NAME = "medical_knowledge.db"
VECTOR_DB_PERSIST_DIR = "./chroma_db"
VECTOR_DB_COLLECTION_NAME = "medical_knowledge"
VECTOR_DB_CACHE_COLLECTION = "semantic_cache"

REDIS_HOST = settings.redis_host
REDIS_PORT = settings.redis_port
CACHE_TTL = 300
REDIS_CHAT_CACHE = 1
REDIS_AGENT_CACHE = 0

WEBSITE_HOST = settings.website_host
TEST = settings.test

MAX_RETRIES = 3  