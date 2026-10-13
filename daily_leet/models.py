from dataclasses import dataclass


@dataclass(frozen=True)
class Problem:
    id: int
    url: str


@dataclass(frozen=True)
class ProblemStats:
    total: int
    unsent: int
