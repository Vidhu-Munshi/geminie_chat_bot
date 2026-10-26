from __future__ import annotations

from google import genai
from google.genai import errors as genai_errors
from google.genai import types

from app.config import (
    GEMINI_API_KEY,
    MODEL_FALLBACKS,
    REQUEST_TIMEOUT_SECONDS,
)


class ChatServiceError(Exception):
    def __init__(self, user_message: str, status_code: int = 502) -> None:
        super().__init__(user_message)
        self.user_message = user_message
        self.status_code = status_code


def _client() -> genai.Client:
    if not GEMINI_API_KEY:
        raise ChatServiceError(
            "The chatbot is not configured yet. Add GEMINI_API_KEY to your .env file.",
            status_code=503,
        )
    return genai.Client(api_key=GEMINI_API_KEY)


def generate_reply(history: list[dict]) -> str:
    system_parts = [item["content"] for item in history if item["role"] == "system"]
    chat_turns = [item for item in history if item["role"] in ("user", "assistant")]

    contents: list[types.Content] = []
    for item in chat_turns:
        role = "user" if item["role"] == "user" else "model"
        contents.append(
            types.Content(role=role, parts=[types.Part(text=item["content"])])
        )

    config = types.GenerateContentConfig(
        system_instruction="\n\n".join(system_parts),
        http_options=types.HttpOptions(timeout=REQUEST_TIMEOUT_SECONDS * 1000),
    )

    models = list(dict.fromkeys(MODEL_FALLBACKS))
    last_error: Exception | None = None
    client = _client()

    for model in models:
        try:
            response = client.models.generate_content(
                model=model,
                contents=contents,
                config=config,
            )
        except ChatServiceError:
            raise
        except genai_errors.APIError as exc:
            last_error = exc
            code = getattr(exc, "code", None) or getattr(exc, "status_code", None)
            if code in (404, 503) and model != models[-1]:
                continue
            raise ChatServiceError(
                _friendly_api_error(exc),
                status_code=int(code or 502),
            ) from exc
        except TimeoutError as exc:
            raise ChatServiceError(
                "ByteBaaz timed out waiting for Gemini. Try again in a moment.",
                status_code=504,
            ) from exc
        except Exception as exc:
            last_error = exc
            message = str(exc).lower()
            if "timeout" in message or "timed out" in message:
                raise ChatServiceError(
                    "ByteBaaz timed out waiting for Gemini. Try again in a moment.",
                    status_code=504,
                ) from exc
            if "429" in message or "resource exhausted" in message or "rate" in message:
                raise ChatServiceError(
                    "Gemini rate limit hit. Wait a few seconds and send the message again.",
                    status_code=429,
                ) from exc
            if ("404" in message or "503" in message) and model != models[-1]:
                continue
            raise ChatServiceError(
                "Could not reach Gemini. Check your internet connection and API key, then retry.",
                status_code=502,
            ) from exc
        else:
            text = (getattr(response, "text", None) or "").strip()
            if text:
                return text
            last_error = ChatServiceError(
                "Gemini returned an empty reply. Try rephrasing your message.",
                status_code=502,
            )

    if isinstance(last_error, ChatServiceError):
        raise last_error
    if isinstance(last_error, genai_errors.APIError):
        code = getattr(last_error, "code", None) or 502
        raise ChatServiceError(_friendly_api_error(last_error), status_code=int(code)) from last_error
    raise ChatServiceError(
        "Gemini is temporarily unavailable. Please try again shortly.",
        status_code=503,
    ) from last_error


def _friendly_api_error(exc: genai_errors.APIError) -> str:
    code = getattr(exc, "code", None) or getattr(exc, "status_code", None)
    if code in (401, 403):
        return "Gemini rejected the API key. Check GEMINI_API_KEY in your .env file."
    if code == 429:
        return "Gemini rate limit hit. Wait a few seconds and send the message again."
    if code in (500, 502, 503):
        return "Gemini is temporarily unavailable. Please try again shortly."
    return "Gemini could not complete this reply. Please try again."
