from __future__ import annotations

from dataclasses import dataclass, field
from threading import Lock
from uuid import uuid4


@dataclass
class Conversation:
    id: str
    messages: list[dict] = field(default_factory=list)
    running_summary: str = ""


class ConversationStore:
    def __init__(self) -> None:
        self._lock = Lock()
        self._items: dict[str, Conversation] = {}

    def create(self) -> Conversation:
        conv = Conversation(id=str(uuid4()))
        with self._lock:
            self._items[conv.id] = conv
        return conv

    def get(self, conversation_id: str) -> Conversation | None:
        with self._lock:
            return self._items.get(conversation_id)

    def get_or_create(self, conversation_id: str | None) -> Conversation:
        if conversation_id:
            existing = self.get(conversation_id)
            if existing:
                return existing
        return self.create()


store = ConversationStore()
