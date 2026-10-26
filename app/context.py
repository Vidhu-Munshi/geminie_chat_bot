from __future__ import annotations

from app.config import MAX_RECENT_MESSAGES, SYSTEM_PROMPT
from app.conversations import Conversation


def apply_window(conversation: Conversation) -> list[dict]:
    """Keep the last N turns plus a running summary of older turns.

    Truncation is the hard cap. When older messages fall off the window,
    they are folded into conversation.running_summary so the model can
    still recall names, goals, and earlier facts.
    """
    overflow = conversation.messages[:-MAX_RECENT_MESSAGES]
    recent = conversation.messages[-MAX_RECENT_MESSAGES:]

    if overflow:
        digest = _digest_messages(overflow)
        if conversation.running_summary:
            conversation.running_summary = (
                conversation.running_summary.rstrip() + "\n" + digest
            )
        else:
            conversation.running_summary = digest
        conversation.messages = recent

    payload: list[dict] = [{"role": "system", "content": SYSTEM_PROMPT}]
    if conversation.running_summary:
        payload.append(
            {
                "role": "system",
                "content": (
                    "Running summary of earlier conversation "
                    "(use this as memory of older turns):\n"
                    f"{conversation.running_summary}"
                ),
            }
        )
    payload.extend(conversation.messages)
    return payload


def _digest_messages(messages: list[dict]) -> str:
    lines = []
    for msg in messages:
        role = "Student" if msg["role"] == "user" else "ByteBaaz"
        text = " ".join(msg["content"].split())
        if len(text) > 220:
            text = text[:217] + "..."
        lines.append(f"- {role}: {text}")
    return "Older turns:\n" + "\n".join(lines)
