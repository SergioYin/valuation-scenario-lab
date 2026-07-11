from __future__ import annotations

from dataclasses import dataclass
from typing import Any


BOUNDARIES = [
    "Research-only output.",
    "No live data.",
    "No broker connections.",
    "No orders.",
    "No predictions.",
    "No buy/sell/hold advice.",
]


@dataclass(frozen=True)
class ScenarioResult:
    name: str
    weight: float
    intrinsic_value_per_share: float
    multiple_cross_check_per_share: float
    blended_value_per_share: float
    low_value_per_share: float
    high_value_per_share: float
    margin_of_safety_pct: float
    margin_label: str
    score: float


def as_float(value: Any, field: str) -> float:
    try:
        return float(value)
    except (TypeError, ValueError) as exc:
        raise ValueError(f"{field} must be numeric") from exc
