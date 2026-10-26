"""Offline check that truncation + running summary work without an API key."""

from app.context import apply_window
from app.conversations import Conversation
from app.config import MAX_RECENT_MESSAGES


def main() -> None:
    conv = Conversation(id="demo")
    for i in range(MAX_RECENT_MESSAGES + 4):
        conv.messages.append({"role": "user", "content": f"My secret token is TOKEN-{i}."})
        conv.messages.append({"role": "assistant", "content": f"Got it, TOKEN-{i}."})

    payload = apply_window(conv)
    assert any(item["role"] == "system" and "ByteBaaz" in item["content"] for item in payload)
    assert conv.running_summary
    assert "TOKEN-0" in conv.running_summary
    recent_user = [m["content"] for m in conv.messages if m["role"] == "user"]
    assert f"TOKEN-{MAX_RECENT_MESSAGES + 3}" in recent_user[-1]
    print("Context window OK")
    print("Recent message count:", len(conv.messages))
    print("Summary preview:\n", conv.running_summary[:400])


if __name__ == "__main__":
    main()
