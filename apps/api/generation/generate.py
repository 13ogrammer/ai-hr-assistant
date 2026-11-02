"""Turn a question plus retrieved chunks into an answer via OpenAI.

Run with: uv run python -m generation.generate <user_id> "your question here"
"""

import json
import sys

from dotenv import load_dotenv
from openai import OpenAI

from models.chunk import RetrievedChunk
from retrieval.retrieve import retrieve
from shared.employees import list_employees
from shared.users import User, get_user
from tools.hr_tools import TOOL_SCHEMAS, call_tool

load_dotenv()

MODEL = "gpt-4o-mini"

SYSTEM_PROMPT_TEMPLATE = (
    "You are an HR assistant for Pinnacle Solutions. Answer the employee's question using "
    "only the context below, drawn from the company's HR policy documents, or by calling a "
    "tool for anything that is a personal, structured fact - salary or leave balance - "
    "rather than guessing it from policy text. If neither the context nor a tool has the "
    "answer, say you don't know - do not guess, and do not use outside knowledge.\n\n"
    "The person asking is {name} (employee ID: {user_id}). When they ask about 'my' salary "
    "or leave balance, look up this ID.\n\n"
    "Known employee IDs you may propose a lookup for (the caller's own permissions decide "
    "whether the lookup is actually allowed):\n{roster}"
)


def build_system_prompt(user: User) -> str:
    roster = "\n".join(f"- {employee.id}: {employee.name}" for employee in list_employees())
    return SYSTEM_PROMPT_TEMPLATE.format(name=user.name, user_id=user.id, roster=roster)


def build_prompt(question: str, chunks: list[RetrievedChunk]) -> str:
    context = "\n\n---\n\n".join(f"[Source: {chunk.source}]\n{chunk.content}" for chunk in chunks)
    return f"Context:\n{context}\n\nQuestion: {question}"


def _tool_call_messages(message, user: User) -> list[dict]:
    """Run every tool call the model proposed and build the result messages.

    The model's proposed arguments (including whatever employee_id it picked)
    are passed straight through to call_tool as untrusted input - user, the
    caller's real session identity, is what call_tool actually trusts.
    """
    assistant_message = {
        "role": "assistant",
        "content": message.content,
        "tool_calls": [
            {
                "id": tool_call.id,
                "type": "function",
                "function": {"name": tool_call.function.name, "arguments": tool_call.function.arguments},
            }
            for tool_call in message.tool_calls
        ],
    }

    tool_messages = []
    for tool_call in message.tool_calls:
        arguments = json.loads(tool_call.function.arguments)
        result = call_tool(tool_call.function.name, arguments, user)
        tool_messages.append({"role": "tool", "tool_call_id": tool_call.id, "content": json.dumps(result)})

    return [assistant_message, *tool_messages]


def generate_answer(question: str, chunks: list[RetrievedChunk], user: User) -> str:
    client = OpenAI()
    messages = [
        {"role": "system", "content": build_system_prompt(user)},
        {"role": "user", "content": build_prompt(question, chunks)},
    ]

    response = client.chat.completions.create(model=MODEL, messages=messages, tools=TOOL_SCHEMAS)
    message = response.choices[0].message

    if message.tool_calls:
        messages.extend(_tool_call_messages(message, user))
        response = client.chat.completions.create(model=MODEL, messages=messages)
        message = response.choices[0].message

    return message.content


if __name__ == "__main__":
    if len(sys.argv) < 3:
        sys.exit('Usage: uv run python -m generation.generate <user_id> "your question here"')
    user = get_user(sys.argv[1])
    if user is None:
        sys.exit(f"Unknown user_id: {sys.argv[1]}")
    question = " ".join(sys.argv[2:])
    chunks = retrieve(question, user.role)
    print(generate_answer(question, chunks, user))
