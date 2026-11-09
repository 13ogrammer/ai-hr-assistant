"""Chapter 5's "Check" step: log what actually leaves the system and read it.

Patches the OpenAI client to print every outbound message for a given
user/question before it's sent, then prints the real final answer - so you
can confirm real names and numbers never appear on the wire, only tokens.

Run with: uv run python -m scripts.show_outbound_payload <user_id> "your question here"
"""

import sys
from unittest.mock import patch

from openai.resources.chat.completions import Completions

from generation.generate import generate_answer
from shared.users import get_user

_real_create = Completions.create


def _spy_create(self, *args, **kwargs):
    print("=== outbound request to OpenAI ===")
    for message in kwargs["messages"]:
        content = message.get("content")
        print(f"[{message['role']}]", content if isinstance(content, str) else content)
    print()
    return _real_create(self, *args, **kwargs)


if __name__ == "__main__":
    if len(sys.argv) < 3:
        sys.exit('Usage: uv run python -m scripts.show_outbound_payload <user_id> "your question here"')
    user = get_user(sys.argv[1])
    if user is None:
        sys.exit(f"Unknown user_id: {sys.argv[1]}")
    question = " ".join(sys.argv[2:])

    with patch.object(Completions, "create", _spy_create):
        answer, sources = generate_answer(question, user)

    print("=== final answer returned to the caller ===")
    print(answer)
    if sources:
        print(f"\nSources: {', '.join(sources)}")
