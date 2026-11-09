"""Turn a question into an answer via OpenAI, using an agent loop over tools.

Run with: uv run python -m generation.generate <user_id> "your question here"
"""

import json
import re
import sys

from dotenv import load_dotenv
from openai import OpenAI

from generation.tokenization import TokenMap
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
    "- get_salary / get_leave_balance: for a specific person's current, personal number. "
    "These identify people only by opaque token (e.g. EMP_A), never a real name or id - "
    "always pass a token as employee_id. Their results also use a token in place of the real "
    "figure (e.g. SALARY_1, LEAVE_BALANCE_1) - treat that token exactly as if it were the real "
    "value: state it plainly and confidently in your answer, with no hedging, no suggestion to "
    "double-check with HR, and never mention the word 'token', 'placeholder', or that a number "
    "has been hidden - the person asking has no reason to know or care that this happens "
    "internally. A leave-balance token's text already includes its unit (e.g. '12.5 days') - "
    "don't add 'days' again after it. The one thing you genuinely cannot do with a token is "
    "arithmetic on it (e.g. converting it to another unit, adding it to another number) - if a "
    "question needs that, say plainly that you can state the figure itself but can't calculate "
    "with it, and give the figure anyway rather than withholding it.\n\n"
    "Any question phrased in the first person about leave or pay - 'how much leave do I have', "
    "'how many days am I entitled to', 'what's my leave balance', 'what do I earn' - is asking "
    "for the asker's own current number, however it's worded, even if the word 'entitled' makes "
    "it sound like a general policy question. Always call get_leave_balance or get_salary for "
    "those, in addition to search_policies if a general rate or rule is also relevant - never "
    "answer a first-person question using only the general rate. Only skip the personal-lookup "
    "tools when the question is explicitly about company-wide rules in the abstract, with no "
    "reference to the asker's own number (e.g. 'what is the annual leave accrual rate', "
    "'how does carryover work').\n\n"
    "The person asking is {user_token}. When they ask about 'my' salary or leave balance, use "
    "this token as the employee_id.\n\n"
    "Known employee tokens you may propose a lookup for, with their title (the caller's own "
    "permissions decide whether a lookup is actually allowed):\n{roster}\n\n"
    "If the question names a specific person, here is that name's matching token:\n{name_hints}\n\n"
    "If no tool has the answer, say you don't know."
)


def build_system_prompt(user: User, token_map: TokenMap, question: str) -> str:
    user_token = token_map.employee_token(user.id, user.name)
    question_lower = question.lower()

    roster_lines = []
    name_hints = []
    for employee in list_employees():
        token = token_map.employee_token(employee.id, employee.name)
        roster_lines.append(f"- {token}: {employee.title}")
        if re.search(rf"\b{re.escape(employee.name.lower())}\b", question_lower):
            name_hints.append(f'- "{employee.name}" -> {token}')

    roster = "\n".join(roster_lines)
    name_hint_block = "\n".join(name_hints) if name_hints else "(no one mentioned by name)"
    return SYSTEM_PROMPT_TEMPLATE.format(user_token=user_token, roster=roster, name_hints=name_hint_block)


def _tokenize_result(result: dict, token_map: TokenMap) -> dict:
    """Replace a tool result's real identity and figures with tokens before it's
    sent to the model - the real values only ever existed in this process's
    memory, in token_map, for the life of this one request."""
    if "error" in result:
        return result

    tokenized = dict(result)
    if "employee_id" in tokenized:
        real_id = tokenized["employee_id"]
        display_name = tokenized.pop("name", real_id)
        tokenized["employee_id"] = token_map.employee_token(real_id, display_name)
    if "salary" in tokenized:
        tokenized["salary"] = token_map.value_token("SALARY", f"${tokenized['salary']:,}")
    if "leave_balance_days" in tokenized:
        tokenized["leave_balance_days"] = token_map.value_token(
            "LEAVE_BALANCE", f"{tokenized['leave_balance_days']:g} days"
        )
    return tokenized


def _tool_call_messages(message, user: User, token_map: TokenMap) -> tuple[list[dict], list[str]]:
    """Run every tool call the model proposed and build the result messages.

    The model's proposed arguments (including whatever employee_id or query it
    picked) are untrusted input - an employee_id is first translated from a
    token back to a real id (or passed through if it isn't a recognized
    token), then it's call_tool/resolve_employee_id, not this function or the
    model, that decides whether the caller is actually allowed to read it.
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
        if "employee_id" in arguments:
            arguments["employee_id"] = token_map.resolve_employee_id(arguments["employee_id"])

        result, tool_sources = call_tool(tool_call.function.name, arguments, user)
        sources.extend(tool_sources)

        tokenized_result = _tokenize_result(result, token_map)
        tool_messages.append({"role": "tool", "tool_call_id": tool_call.id, "content": json.dumps(tokenized_result)})

    return [assistant_message, *tool_messages], sources


def generate_answer(question: str, user: User) -> tuple[str, list[str]]:
    client = OpenAI()
    token_map = TokenMap()
    messages = [
        {"role": "system", "content": build_system_prompt(user, token_map, question)},
        {"role": "user", "content": question},
    ]
    all_sources: list[str] = []

    for _ in range(MAX_TOOL_ITERATIONS):
        response = client.chat.completions.create(model=MODEL, messages=messages, tools=ALL_TOOL_SCHEMAS)
        message = response.choices[0].message

        if not message.tool_calls:
            return token_map.detokenize(message.content), sorted(set(all_sources))

        tool_messages, sources = _tool_call_messages(message, user, token_map)
        messages.extend(tool_messages)
        all_sources.extend(sources)

    # Safety cap hit: force a plain-text answer from whatever's been gathered so far.
    response = client.chat.completions.create(model=MODEL, messages=messages)
    return token_map.detokenize(response.choices[0].message.content), sorted(set(all_sources))


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
