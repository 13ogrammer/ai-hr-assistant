"""Pure unit tests for the identity-enforcement rule in front of every HR tool.

No Postgres needed: resolve_employee_id never touches the database, which is
deliberate - the security property (a non-HR caller can never be pointed at
someone else's record, no matter what the model or a prompt injection asks
for) should hold regardless of what's in any table. DB-backed lookups
(get_salary, get_leave_balance, call_tool against real records) are covered
in tests/test_employees.py alongside the rest of the employees table tests.
"""

from shared.users import get_user
from tools.hr_tools import call_tool, resolve_employee_id

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
