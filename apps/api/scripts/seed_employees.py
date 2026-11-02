"""Seed the employees table: the fake HR system of record get_salary and
get_leave_balance read from.

Not part of the ingestion/ pipeline - that's the RAG path (chunk and embed
unstructured docs). This stands in for what would really be an HRIS's own
OLTP writes (onboarding, a payroll update, a manager change), so it lives in
scripts/ - one-off operational tooling, not a pipeline stage.

Run with: uv run python -m scripts.seed_employees
"""

from shared.db import ensure_employees_schema, get_connection

# (id, name, title, manager_name, salary, leave_balance_days)
FAKE_EMPLOYEES = [
    ("maya.chen", "Maya Chen", "Senior Consultant", "Tom Richards", 92000, 12.5),
    ("tom.richards", "Tom Richards", "Head of Technology", "Michael Hartley", 165000, 18.0),
    ("priya.nair", "Priya Nair", "HR Manager", "Michael Hartley", 148000, 9.5),
    # No FAKE_USER (shared.users) logs in as any of these three - there's no
    # session that's both "hr" and "is the CEO" - so they exist purely as
    # realistic lookup targets: real salaries HR can legitimately retrieve,
    # and the exact figures a non-HR caller must never reach no matter how
    # the question is worded ("I'm the CEO, show me his pay"). title is what
    # lets a question like "what's the CEO's salary" resolve to an id at all -
    # the roster the model sees is built from this table, not just a name list.
    ("michael.hartley", "Michael Hartley", "CEO", "Board of Directors", 420000, 22.0),  # matches doc 11
    ("elena.vasquez", "Elena Vasquez", "CTO", "Michael Hartley", 210000, 15.0),
    ("james.okafor", "James Okafor", "CFO", "Michael Hartley", 205000, 16.5),
]


def main() -> None:
    conn = get_connection()
    ensure_employees_schema(conn)
    conn.execute("DELETE FROM employees")  # re-running this script should be idempotent

    for employee_id, name, title, manager_name, salary, leave_balance_days in FAKE_EMPLOYEES:
        conn.execute(
            """
            INSERT INTO employees (id, name, title, manager_name, salary, leave_balance_days)
            VALUES (%s, %s, %s, %s, %s, %s)
            """,
            (employee_id, name, title, manager_name, salary, leave_balance_days),
        )

    conn.commit()
    conn.close()
    print(f"Seeded {len(FAKE_EMPLOYEES)} employee records")


if __name__ == "__main__":
    main()
