"""Turn a question into an answer via OpenAI, using an agent loop over tools.

Run with: uv run python -m generation.generate <user_id> "your question here"
"""

import json
import sys

from dotenv import load_dotenv
from openai import OpenAI

from shared.employees import list_employees
from shared.users import User, get_user
from tools.registry import ALL_TOOL_SCHEMAS, call_tool

load_dotenv()

MODEL = "gpt-4o-mini"
MAX_TOOL_ITERATIONS = 5

SYSTEM_PROMPT_TEMPLATE = (
    "You are an HR assistant for Pinnacle Solutions. Answer only using what your tools "
    "return - never guess, and never use outside knowledge. You have two kinds of tools:\n\n"
    "- search_policies: for rules, processes, and general entitlements or rates described "
    "in company policy documents (e.g. 'how do I request leave', 'what is the annual leave "
    "accrual rate').\n"
    "- get_salary / get_leave_balance: for a specific person's current, personal number.\n\n"
    "Any question phrased in the first person about leave or pay - 'how much leave do I have', "
    "'how many days am I entitled to', 'what's my leave balance', 'what do I earn' - is asking "
    "for the asker's own current number, however it's worded, even if the word 'entitled' makes "
    "it sound like a general policy question. Always call get_leave_balance or get_salary for "
    "those, in addition to search_policies if a general rate or rule is also relevant - never "
    "answer a first-person question using only the general rate. Only skip the personal-lookup "
    "tools when the question is explicitly about company-wide rules in the abstract, with no "
    "reference to the asker's own number (e.g. 'what is the annual leave accrual rate', "
    "'how does carryover work').\n\n"
    "The person asking is {name} (employee ID: {user_id}). When they ask about 'my' salary "
    "or leave balance, look up this ID.\n\n"
    "Known employee IDs you may propose a lookup for (the caller's own permissions decide "
    "whether the lookup is actually allowed):\n{roster}\n\n"
    "If no tool has the answer, say you don't know."
)


def build_system_prompt(user: User) -> str:
    roster = "\n".join(f"- {employee.id}: {employee.name} ({employee.title})" for employee in list_employees())
    return SYSTEM_PROMPT_TEMPLATE.format(name=user.name, user_id=user.id, roster=roster)


def _tool_call_messages(message, user: User) -> tuple[list[dict], list[str]]:
    """Run every tool call the model proposed and build the result messages.

    The model's proposed arguments (including whatever employee_id or query it
    picked) are passed straight through to call_tool as untrusted input - user,
    the caller's real session identity, is what call_tool actually trusts.
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
    sources: list[str] = []
    for tool_call in message.tool_calls:
        arguments = json.loads(tool_call.function.arguments)
        result, tool_sources = call_tool(tool_call.function.name, arguments, user)
        sources.extend(tool_sources)
        tool_messages.append({"role": "tool", "tool_call_id": tool_call.id, "content": json.dumps(result)})

    return [assistant_message, *tool_messages], sources


def generate_answer(question: str, user: User) -> tuple[str, list[str]]:
    client = OpenAI()
    messages = [
        {"role": "system", "content": build_system_prompt(user)},
        {"role": "user", "content": question},
    ]
    all_sources: list[str] = []

    for _ in range(MAX_TOOL_ITERATIONS):
        response = client.chat.completions.create(model=MODEL, messages=messages, tools=ALL_TOOL_SCHEMAS)
        message = response.choices[0].message

        if not message.tool_calls:
            return message.content, sorted(set(all_sources))

        tool_messages, sources = _tool_call_messages(message, user)
        messages.extend(tool_messages)
        all_sources.extend(sources)

    # Safety cap hit: force a plain-text answer from whatever's been gathered so far.
    response = client.chat.completions.create(model=MODEL, messages=messages)
    return response.choices[0].message.content, sorted(set(all_sources))


if __name__ == "__main__":
    if len(sys.argv) < 3:
        sys.exit('Usage: uv run python -m generation.generate <user_id> "your question here"')
    user = get_user(sys.argv[1])
    if user is None:
        sys.exit(f"Unknown user_id: {sys.argv[1]}")
    question = " ".join(sys.argv[2:])
    answer, sources = generate_answer(question, user)
    print(answer)
    if sources:
        print(f"\nSources: {', '.join(sources)}")
