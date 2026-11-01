"""Access levels: who is allowed to see which chunks.

Every doc in docs/ is tagged with one access level at ingestion time. The
level maps to the set of roles allowed to retrieve its chunks - this
mapping, not the question text, is what the SQL filter in retrieve() uses.
"""

ROLES = ["employee", "manager", "hr"]

ACCESS_LEVELS = {
    "public": ["employee", "manager", "hr"],
    "internal": ["employee", "manager", "hr"],
    "confidential": ["manager", "hr"],
    "restricted": ["hr"],
}

# Every doc defaults to "internal" (all roles) unless listed here - most of
# the corpus is ordinary company-wide policy, so only the exceptions need
# naming.
DOC_ACCESS_LEVELS = {
    "11_EXECUTIVE_COMPENSATION_CONFIDENTIAL.md": "restricted",
    "12_MANAGER_COMPENSATION_CALIBRATION_GUIDE.md": "confidential",
}

DEFAULT_ACCESS_LEVEL = "internal"


def access_level_for_doc(filename: str) -> str:
    return DOC_ACCESS_LEVELS.get(filename, DEFAULT_ACCESS_LEVEL)


def allowed_roles_for_level(access_level: str) -> list[str]:
    return ACCESS_LEVELS[access_level]
