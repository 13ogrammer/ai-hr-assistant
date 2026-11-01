"""A fake user directory standing in for a real login/session system.

There's no auth yet. The web UI lets the person at the keyboard pick one of
these users before asking a question, and the request carries that user's
id. The API then looks up the role server-side from this trusted list,
rather than trusting a role sent directly by the client - the closest
honest approximation of "identity comes from the session" without
building real auth yet.
"""

from dataclasses import dataclass


@dataclass(frozen=True)
class User:
    id: str
    name: str
    title: str
    role: str  # one of shared.access.ROLES


FAKE_USERS = [
    User(id="maya.chen", name="Maya Chen", title="Senior Consultant", role="employee"),
    User(id="tom.richards", name="Tom Richards", title="Head of Technology", role="manager"),
    User(id="priya.nair", name="Priya Nair", title="HR Manager", role="hr"),
]

USERS_BY_ID = {user.id: user for user in FAKE_USERS}


def get_user(user_id: str) -> User | None:
    return USERS_BY_ID.get(user_id)
