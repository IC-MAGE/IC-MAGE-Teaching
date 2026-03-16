from dataclasses import dataclass


@dataclass(frozen=True)
class TestConditions:
    label: str
    e0: float
    p0: float
    q0: float