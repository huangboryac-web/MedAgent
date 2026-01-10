from pydantic import BaseModel

class ChatRequest(BaseModel):
    query: str
    session_id: str = "default"

class Message(BaseModel):
    role: str
    content: str