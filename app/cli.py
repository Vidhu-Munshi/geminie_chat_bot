from __future__ import annotations

import sys

from app.context import apply_window
from app.conversations import store
from app.llm import ChatServiceError, generate_reply


def main() -> int:
    conversation = store.create()
    print("ByteBaaz CLI — type your message. /new starts a fresh chat. /quit exits.\n")
    while True:
        try:
            text = input("You: ").strip()
        except (EOFError, KeyboardInterrupt):
            print("\nBye.")
            return 0
        if not text:
            continue
        if text in {"/quit", "/exit"}:
            print("Bye.")
            return 0
        if text == "/new":
            conversation = store.create()
            print("(new conversation)\n")
            continue

        conversation.messages.append({"role": "user", "content": text})
        try:
            reply = generate_reply(apply_window(conversation))
        except ChatServiceError as exc:
            conversation.messages.pop()
            print(f"Error: {exc.user_message}\n")
            continue
        conversation.messages.append({"role": "assistant", "content": reply})
        print(f"ByteBaaz: {reply}\n")


if __name__ == "__main__":
    sys.exit(main())
