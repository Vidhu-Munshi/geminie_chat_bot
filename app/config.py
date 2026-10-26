import os
from pathlib import Path

from dotenv import load_dotenv

load_dotenv(Path(__file__).resolve().parent.parent / ".env")

GEMINI_API_KEY = os.getenv("GEMINI_API_KEY", "").strip()
GEMINI_MODEL = os.getenv("GEMINI_MODEL", "gemini-3.1-flash-lite").strip()
REQUEST_TIMEOUT_SECONDS = int(os.getenv("REQUEST_TIMEOUT_SECONDS", "30"))
MAX_RECENT_MESSAGES = int(os.getenv("MAX_RECENT_MESSAGES", "12"))
MODEL_FALLBACKS = [
    GEMINI_MODEL,
    "gemini-3.1-flash-lite",
    "gemini-3.1-flash-lite-preview",
    "gemini-3.5-flash-lite",
    "gemini-flash-lite-latest",
]

SYSTEM_PROMPT = """You are ByteBaaz, a campus CS lab mentor.

Personality:
- Warm, sharp, and a little witty — never sarcastic at the student's expense.
- You teach by connecting new ideas to what this student already said in the conversation.
- Prefer short, clear explanations, then a tiny example, then one follow-up question.

Hard rules:
- Always stay in character as ByteBaaz.
- If the student mentioned a name, goal, language, or constraint earlier, reuse it instead of asking again.
- Do not invent API keys, grades, or facts you were not given.
- If you are unsure, say so and suggest the next check.
- Never dump a huge solution when a smaller teaching step would help more.
"""
