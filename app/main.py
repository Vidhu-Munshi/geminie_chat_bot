from __future__ import annotations

from pathlib import Path

from fastapi import FastAPI, HTTPException, Request
from fastapi.exceptions import RequestValidationError
from fastapi.responses import FileResponse, JSONResponse
from fastapi.staticfiles import StaticFiles
from pydantic import BaseModel, Field

from app.context import apply_window
from app.conversations import store
from app.llm import ChatServiceError, generate_reply

ROOT = Path(__file__).resolve().parent.parent
STATIC = ROOT / "static"

app = FastAPI(title="ByteBaaz Gemini Chatbot")
app.mount("/static", StaticFiles(directory=STATIC), name="static")


@app.exception_handler(RequestValidationError)
async def invalid_chat_request(_: Request, __: RequestValidationError) -> JSONResponse:
    return JSONResponse(
        status_code=400,
        content={"detail": "Please type a message before sending."},
    )


@app.exception_handler(Exception)
async def unexpected_error(_: Request, exc: Exception) -> JSONResponse:
    if isinstance(exc, HTTPException):
        return JSONResponse(status_code=exc.status_code, content={"detail": exc.detail})
    return JSONResponse(
        status_code=500,
        content={"detail": "Something went wrong on the server. Please try again."},
    )


class ChatRequest(BaseModel):
    message: str = Field(..., min_length=1, max_length=8000)
    conversation_id: str | None = None


class ChatResponse(BaseModel):
    conversation_id: str
    reply: str


@app.get("/")
def index() -> FileResponse:
    return FileResponse(STATIC / "index.html")


@app.get("/health")
def health() -> dict:
    return {"ok": True}


@app.post("/api/chat", response_model=ChatResponse)
def chat(body: ChatRequest) -> ChatResponse:
    conversation = store.get_or_create(body.conversation_id)
    conversation.messages.append({"role": "user", "content": body.message.strip()})

    try:
        history = apply_window(conversation)
        reply = generate_reply(history)
    except ChatServiceError as exc:
        if conversation.messages and conversation.messages[-1]["role"] == "user":
            conversation.messages.pop()
        raise HTTPException(status_code=exc.status_code, detail=exc.user_message) from exc

    conversation.messages.append({"role": "assistant", "content": reply})
    return ChatResponse(conversation_id=conversation.id, reply=reply)
