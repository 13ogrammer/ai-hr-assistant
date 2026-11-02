"""Pure unit tests for the identity-enforcement rule in front of every HR tool,
plus the search tool's role-enforcement and the registry's dispatch.

No Postgres needed: resolve_employee_id never touches the database, which is
deliberate - the security property (a non-HR caller can never be pointed at
someone else's record, no matter what the model or a prompt injection asks
for) should hold regardless of what's in any table. DB-backed lookups
(get_salary, get_leave_balance, call_tool against real records) are covered
in tests/test_employees.py alongside the rest of the employees table tests.
"""

from unittest.mock import patch

from models.chunk import RetrievedChunk
from shared.users import get_user
from tools.hr_tools import call_tool, resolve_employee_id
from tools.registry import call_tool as registry_call_tool
from tools.search_tools import search_policies

maya = get_user("maya.chen")  # employee
tom = get_user("tom.richards")  # manager
priya = get_user("priya.nair")  # hr


def test_employee_is_locked_to_their_own_id_even_if_they_ask_for_someone_else():
    assert resolve_employee_id(maya, "tom.richards") == "maya.chen"


def test_manager_is_locked_to_their_own_id_too():
    assert resolve_employee_id(tom, "priya.nair") == "tom.richards"


def test_hr_can_direct_a_lookup_at_someone_else():
    assert resolve_employee_id(priya, "maya.chen") == "maya.chen"


def test_hr_with_no_requested_id_defaults_to_their_own():
    assert resolve_employee_id(priya, "") == "priya.nair"


def test_prompt_injection_claiming_to_be_the_ceo_does_not_escape_the_callers_own_id():
    assert resolve_employee_id(maya, "michael.hartley") == "maya.chen"


def test_call_tool_rejects_unknown_tool_name_before_touching_the_database():
    result = call_tool("delete_everything", {"employee_id": "maya.chen"}, maya)
    assert "error" in result


def make_chunk(source="policy.md", content="text"):
    return RetrievedChunk(source=source, chunk_index=0, content=content, distance=0.1, access_level="internal")


def test_search_policies_uses_the_callers_role_not_an_argument():
    with patch("tools.search_tools.retrieve", return_value=[make_chunk()]) as mock_retrieve:
        search_policies(tom, "annual leave")

    mock_retrieve.assert_called_once_with("annual leave", "manager")


def test_search_policies_returns_sources_matching_the_retrieved_chunks():
    chunks = [make_chunk(source="a.md"), make_chunk(source="b.md")]
    with patch("tools.search_tools.retrieve", return_value=chunks):
        result, sources = search_policies(maya, "leave policy")

    assert sources == ["a.md", "b.md"]
    assert [r["source"] for r in result["results"]] == ["a.md", "b.md"]


def test_registry_routes_search_policies_to_the_search_tool():
    with patch("tools.registry.search_policies", return_value=({"results": []}, ["a.md"])) as mock_search:
        result, sources = registry_call_tool("search_policies", {"query": "leave"}, maya)

    mock_search.assert_called_once_with(maya, "leave")
    assert result == {"results": []}
    assert sources == ["a.md"]


def test_registry_routes_hr_tool_names_to_hr_tools_call_tool_with_no_sources():
    with patch("tools.registry.call_hr_tool", return_value={"salary": 92000}) as mock_hr_call:
        result, sources = registry_call_tool("get_salary", {"employee_id": "maya.chen"}, maya)

    mock_hr_call.assert_called_once_with("get_salary", {"employee_id": "maya.chen"}, maya)
    assert result == {"salary": 92000}
    assert sources == []
