from dataclasses import dataclass
from typing import Any, Callable, Generic, Optional, TypeVar

T = TypeVar("T")


@dataclass(frozen=True)
class Matcher(Generic[T]):
    delegate: Callable[[T], bool]

    def matches(self, sut: T) -> bool:
        return self.delegate(sut)

    @staticmethod
    def any() -> Optional["Matcher[Any]"]:
        return None

    @staticmethod
    def equals(expected: T) -> "Matcher[T]":
        return Matcher(lambda x: x == expected)

    @staticmethod
    def not_equals(not_expected: T) -> "Matcher[T]":
        return Matcher(lambda x: x != not_expected)
