"""Salary and leave-balance lookups exposed to the model as tools.

The model proposes an employee_id argument from the question text, but that
argument is never trusted on its own: resolve_employee_id overwrites it from
the caller's verified session identity before any lookup runs, the same way
shared.access keeps role out of the question text for retrieval. An employee
can only ever end up reading their own record; HR can direct a lookup at
anyone, and every lookup - allowed or blocked - is logged.

Run with: uv run python -m tools.hr_tools <user_id> <get_salary|get_leave_balance> [requested_employee_id]
"""

import logging
import sys

from shared.employees import get_employee
from shared.users import User, get_user

logger = logging.getLogger("hr_tools.audit")
logging.basicConfig(level=logging.INFO, format="%(message)s")

TOOL_SCHEMAS = [
    {
        "type": "function",
        "function": {
            "name": "get_salary",
            "description": (
                "Look up an employee's current base salary. Use this for any question about "
                "pay, salary, or compensation amount for a specific person, instead of guessing "
                "a figure from policy documents."
            ),
            "parameters": {
                "type": "object",
                "properties": {
                    "employee_id": {
                        "type": "string",
                        "description": (
                            "The employee ID to look up, e.g. 'maya.chen'. Use the asker's own "
                            "ID for 'my salary'."
                        ),
                    }
                },
                "required": ["employee_id"],
            },
        },
    },
    {
        "type": "function",
        "function": {
            "name": "get_leave_balance",
            "description": (
                "Look up an employee's current annual leave balance in days. Use this for any "
                "question about how much leave a specific person has left."
            ),
            "parameters": {
                "type": "object",
                "properties": {
                    "employee_id": {
                        "type": "string",
                        "description": (
                            "The employee ID to look up, e.g. 'maya.chen'. Use the asker's own "
                            "ID for 'my leave balance'."
                        ),
                    }
                },
                "required": ["employee_id"],
            },
        },
    },
]


def resolve_employee_id(caller: User, requested_id: str) -> str:
    """Decide whose record a tool call is actually allowed to read.

    requested_id comes from the model, which took it from the question text -
    so a non-HR caller is hard-locked to their own id no matter what they (or
    an injected prompt) ask for. Only HR can direct a lookup at someone else.
    """
    if caller.role != "hr":
        if requested_id != caller.id:
            logger.info(
                "BLOCKED employee_id override: caller=%s(%s) requested=%s -> resolved=%s",
                caller.id,
                caller.role,
                requested_id,
                caller.id,
            )
        return caller.id
    return requested_id or caller.id


def get_salary(caller: User, requested_id: str) -> dict:
    employee_id = resolve_employee_id(caller, requested_id)
    logger.info("AUDIT get_salary: caller=%s(%s) resolved=%s", caller.id, caller.role, employee_id)
    employee = get_employee(employee_id)
    if employee is None:
        return {"error": f"No employee record found for '{employee_id}'"}
    return {"employee_id": employee.id, "name": employee.name, "salary": employee.salary}


def get_leave_balance(caller: User, requested_id: str) -> dict:
    employee_id = resolve_employee_id(caller, requested_id)
    logger.info("AUDIT get_leave_balance: caller=%s(%s) resolved=%s", caller.id, caller.role, employee_id)
    employee = get_employee(employee_id)
    if employee is None:
        return {"error": f"No employee record found for '{employee_id}'"}
    return {"employee_id": employee.id, "name": employee.name, "leave_balance_days": employee.leave_balance_days}


TOOLS_BY_NAME = {
    "get_salary": get_salary,
    "get_leave_balance": get_leave_balance,
}


def call_tool(name: str, arguments: dict, caller: User) -> dict:
    """Dispatch a model-proposed tool call, after identity enforcement.

    arguments comes straight from tool_call.function.arguments - untrusted
    input, same as the question text it was derived from.
    """
    tool = TOOLS_BY_NAME.get(name)
    if tool is None:
        return {"error": f"Unknown tool '{name}'"}
    return tool(caller, arguments.get("employee_id", caller.id))


if __name__ == "__main__":
    if len(sys.argv) < 3:
        sys.exit(
            "Usage: uv run python -m tools.hr_tools <user_id> <get_salary|get_leave_balance> "
            "[requested_employee_id]"
        )
    user = get_user(sys.argv[1])
    if user is None:
        sys.exit(f"Unknown user_id: {sys.argv[1]}")
    tool_name = sys.argv[2]
    requested_id = sys.argv[3] if len(sys.argv) > 3 else user.id
    print(call_tool(tool_name, {"employee_id": requested_id}, user))
