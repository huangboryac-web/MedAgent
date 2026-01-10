from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from database.db import get_chat_by_session_id, init_chat_db, insert_chat_by_session_id
from models import ChatRequest
from constants import WEBSITE_HOST, APP_TITLE, TEST

app = FastAPI(title=APP_TITLE)

app.add_middleware(
    CORSMiddleware,
    allow_origins=[WEBSITE_HOST],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

init_chat_db()

@app.get("/history/{session_id}")
async def get_history(session_id: str):
    rows = get_chat_by_session_id(session_id)
    return [dict(row) for row in rows]



@app.post("/chat")
async def chat_endpoint(request: ChatRequest):
    insert_chat_by_session_id(request.session_id, request.query, "user")

    try:
        result = {
            "generation": "Result"
        }
        answer = result.get("generation", "Error.")
    except Exception as e:
        answer = f"System Error: {str(e)}"

    insert_chat_by_session_id(request.session_id, answer, "assistant")

    return {"response": answer}


if __name__ == "__main__":
    import uvicorn
    uvicorn.run("main:app", port=8000, reload=TEST)