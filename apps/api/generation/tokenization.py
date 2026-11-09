"""Per-request tokenization: swap real employee identities and structured
values for opaque placeholders before anything reaches the model, and swap
them back in the final answer text. A TokenMap lives only in the local scope
of one generate_answer() call - never logged, never persisted.

Scoped to structured data only (employee identity, salary, leave balance).
Free text retrieved from documents can still contain real PII embedded in
prose (e.g. a contract's remuneration clause) - that needs PII detection
(Presidio-style NER), not a lookup swap, and isn't touched here. See TODO.md.

Tokenization and access control are orthogonal layers: resolve_employee_id
here only translates the wire format back to a real id - tools.hr_tools's
resolve_employee_id is what actually enforces who's allowed to see it, and
only ever sees real ids, unchanged.
"""

import re
import string


class TokenMap:
    def __init__(self) -> None:
        self._id_to_token: dict[str, str] = {}
        self._token_to_id: dict[str, str] = {}
        self._token_to_display: dict[str, str] = {}
        self._value_counts: dict[str, int] = {}

    def employee_token(self, employee_id: str, display_name: str) -> str:
        if employee_id in self._id_to_token:
            return self._id_to_token[employee_id]
        token = f"EMP_{string.ascii_uppercase[len(self._id_to_token)]}"
        self._id_to_token[employee_id] = token
        self._token_to_id[token] = employee_id
        self._token_to_display[token] = display_name
        return token

    def resolve_employee_id(self, token_or_id: str) -> str:
        """Token -> real id. Passes through unchanged if it isn't a known
        token - e.g. the model ignores instructions and proposes a real id
        directly, which does happen - never raises."""
        return self._token_to_id.get(token_or_id, token_or_id)

    def value_token(self, label: str, display: str) -> str:
        self._value_counts[label] = self._value_counts.get(label, 0) + 1
        token = f"{label}_{self._value_counts[label]}"
        self._token_to_display[token] = display
        return token

    def detokenize(self, text: str) -> str:
        for token, display in self._token_to_display.items():
            text = re.sub(rf"\b{re.escape(token)}\b", display, text)
        return text
