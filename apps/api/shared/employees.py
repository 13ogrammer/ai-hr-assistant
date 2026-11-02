"""Query layer for the employees table: what get_salary and get_leave_balance
read from.

This is deliberately a separate table from the fake login directory in
shared.users - that module is who's logged in (identity, role); this table
is the real HR system of record those identities look things up in, queried
from Postgres like any other structured data a production backend would
hold. The only link between the two is the employee id, which is why every
lookup must go through tools.hr_tools.resolve_employee_id rather than
trusting an id the model proposes directly.

Seeded by scripts/seed_employees.py - run that (after docker compose up -d)
before anything here will return a row.
"""

from dataclasses import dataclass

from shared.db import get_connection


@dataclass(frozen=True)
class EmployeeRecord:
    id: str
    name: str
    manager_name: str | None
    salary: int
    leave_balance_days: float


def get_employee(employee_id: str) -> EmployeeRecord | None:
    conn = get_connection()
    row = conn.execute(
        "SELECT id, name, manager_name, salary, leave_balance_days FROM employees WHERE id = %s",
        (employee_id,),
    ).fetchone()
    conn.close()
    return EmployeeRecord(*row) if row else None


def list_employees() -> list[EmployeeRecord]:
    conn = get_connection()
    rows = conn.execute(
        "SELECT id, name, manager_name, salary, leave_balance_days FROM employees ORDER BY id"
    ).fetchall()
    conn.close()
    return [EmployeeRecord(*row) for row in rows]
