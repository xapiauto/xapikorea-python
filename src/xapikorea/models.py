from __future__ import annotations

from dataclasses import dataclass
from typing import Any


@dataclass(frozen=True)
class AccountInfo:
    email: str
    plan: str
    key_label: str
    key_prefix: str
    requests_this_month: int
    monthly_cap: int | None
    remaining: int | None

    @classmethod
    def from_dict(cls, data: dict[str, Any]) -> AccountInfo:
        return cls(
            email=data["email"],
            plan=data["plan"],
            key_label=data["key_label"],
            key_prefix=data["key_prefix"],
            requests_this_month=data["requests_this_month"],
            monthly_cap=data.get("monthly_cap"),
            remaining=data.get("remaining"),
        )

