"""Integration tests for the employees table and the tools built on it.

These need Postgres running (docker compose up -d) with the fake employee
records seeded (uv run python -m scripts.seed_employees) - they hit the real
database. tests/test_tools.py covers the identity-enforcement rule on its
own, with no database required.
"""

from shared.employees import get_employee, list_employees
from shared.users import FAKE_USERS, get_user
from tools.hr_tools import call_tool, get_leave_balance, get_salary

maya = get_user("maya.chen")  # employee
priya = get_user("priya.nair")  # hr


def test_every_fake_user_has_a_matching_employee_record():
    for user in FAKE_USERS:
        assert get_employee(user.id) is not None


def test_get_employee_returns_none_for_unknown_id():
    assert get_employee("not.a.real.employee") is None


def test_list_employees_includes_the_seeded_executives():
    ids = {employee.id for employee in list_employees()}
    assert {"maya.chen", "tom.richards", "priya.nair", "michael.hartley"} <= ids


def test_salary_and_leave_balance_are_positive():
    for employee in list_employees():
        assert employee.salary > 0
        assert employee.leave_balance_days >= 0


def test_get_salary_returns_the_resolved_employees_salary():
    result = get_salary(priya, "tom.richards")
    assert result["employee_id"] == "tom.richards"
    assert result["salary"] > 0


def test_get_leave_balance_is_locked_to_the_caller_for_a_non_hr_user():
    result = get_leave_balance(maya, "tom.richards")
    assert result["employee_id"] == "maya.chen"


def test_get_salary_for_unknown_employee_id_is_an_error_not_a_crash():
    result = get_salary(priya, "not.a.real.employee")
    assert "error" in result


def test_hr_can_legitimately_see_the_ceos_real_salary():
    # Confirms the lock in test_tools.py is protecting something real, not an
    # id that happens not to exist - matches 11_CEO_EMPLOYMENT_CONTRACT_RESTRICTED.md.
    result = get_salary(priya, "michael.hartley")
    assert result == {"employee_id": "michael.hartley", "name": "Michael Hartley", "salary": 420000}


def test_call_tool_dispatches_by_name():
    result = call_tool("get_salary", {"employee_id": "tom.richards"}, priya)
    assert result["employee_id"] == "tom.richards"


def test_call_tool_enforces_identity_for_an_employee_caller():
    result = call_tool("get_salary", {"employee_id": "priya.nair"}, maya)
    assert result["employee_id"] == "maya.chen"
