"""Policy-document search exposed to the model as a tool, backed by retrieval.retrieve.

The model proposes a query string, but the role used to filter results is the
caller's verified session role - never anything from the model - the same rule
shared.access enforces for plain retrieval. This is retrieval reached through a
tool call instead of a pre-fetch, so Chapter 2's access control is unchanged.
"""

from retrieval.retrieve import retrieve
from shared.users import User

SEARCH_TOOL_SCHEMA = {
    "type": "function",
    "function": {
        "name": "search_policies",
        "description": (
            "Search the company's HR policy documents and employee handbook for rules, "
            "processes, and general entitlements or rates. Not for a specific person's "
            "current salary or leave balance - use get_salary or get_leave_balance for those."
        ),
        "parameters": {
            "type": "object",
            "properties": {
                "query": {
                    "type": "string",
                    "description": "The policy topic or question to search for.",
                }
            },
            "required": ["query"],
        },
    },
}


def search_policies(caller: User, query: str) -> tuple[dict, list[str]]:
    chunks = retrieve(query, caller.role)
    result = {"results": [{"source": chunk.source, "content": chunk.content} for chunk in chunks]}
    sources = [chunk.source for chunk in chunks]
    return result, sources
