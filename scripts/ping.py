"""Minimal Gemini connectivity check. Prints one reply and exits."""

from app.llm import ChatServiceError, generate_reply


def main() -> None:
    history = [
        {"role": "system", "content": "You are ByteBaaz. Reply in one short sentence."},
        {"role": "user", "content": "Say hello and confirm you can hear me."},
    ]
    try:
        print(generate_reply(history))
    except ChatServiceError as exc:
        raise SystemExit(exc.user_message) from exc


if __name__ == "__main__":
    main()
