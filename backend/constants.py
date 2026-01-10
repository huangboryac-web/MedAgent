from config import get_settings

settings = get_settings()

APP_TITLE = "Medical Knowledge Agent"
DB_NAME = "medical_knowledge.db"

REDIS_HOST = settings.redis_host
REDIS_PORT = settings.redis_port
CACHE_TTL = 300
REDIS_CHAT_CACHE = 0
REDIS_AGENT_CACHE = 1

WEBSITE_HOST = settings.website_host
TEST = settings.test