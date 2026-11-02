"""Combines every tool-providing module into the single list/dispatcher generate.py uses.

Exists because there are now two tool-providing modules (hr_tools, search_tools) -
PLAN.md's "abstract only when a second real case forces it."
"""

from tools.hr_tools import TOOL_SCHEMAS as HR_TOOL_SCHEMAS
from tools.hr_tools import call_tool as call_hr_tool
from tools.search_tools import SEARCH_TOOL_SCHEMA, search_policies
from shared.users import User

ALL_TOOL_SCHEMAS = HR_TOOL_SCHEMAS + [SEARCH_TOOL_SCHEMA]


def call_tool(name: str, arguments: dict, caller: User) -> tuple[dict, list[str]]:
    """Dispatch a model-proposed tool call to whichever module provides it.

    Every tool returns (result, sources) so callers can collect sources without
    caring which tool produced them - non-search tools simply return no sources.
    """
    if name == "search_policies":
        return search_policies(caller, arguments.get("query", ""))
    return call_hr_tool(name, arguments, caller), []
