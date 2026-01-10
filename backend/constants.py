from config import get_settings

APP_TITLE = "Medical Knowledge Agent"
DB_NAME = "medical_knowledge.db"

WEBSITE_HOST = get_settings().website_host
TEST=get_settings().test