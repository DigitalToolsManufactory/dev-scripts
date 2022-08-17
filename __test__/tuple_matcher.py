from dataclasses import dataclass
from typing import Any, Callable, Generic, Optional, Tuple, TypeVar

T = TypeVar("T")
K = TypeVar("K")


@dataclass(frozen=True)
class TupleMatcher(Generic[T, K]):
    delegate: Callable[[Tuple[T, K]], bool]

    def matches(self, sut: Tuple[T, K]) -> bool:
        return self.delegate(sut)

    @staticmethod
    def any() -> Optional["TupleMatcher[Any, Any]"]:
        return None

    @staticmethod
    def equals(expected: Tuple[T, K]) -> "TupleMatcher[T, K]":
        return TupleMatcher(lambda x: x == expected)
