from dataclasses import dataclass
from typing import Any, Callable, Dict, Generic, Optional, TypeVar

K = TypeVar("K")
V = TypeVar("V")


@dataclass(frozen=True)
class DictMatcher(Generic[K, V]):
    delegate: Callable[[Dict[K, V]], bool]

    def matches(self, sut: Dict[K, V]) -> bool:
        return self.delegate(sut)

    @staticmethod
    def any() -> Optional["DictMatcher[Any, Any]"]:
        return None

    @staticmethod
    def contains(key: K, value: V) -> "DictMatcher[K, V]":
        return DictMatcher(lambda x: key in x and x[key] == value)

    @staticmethod
    def contains_key(key: K) -> "DictMatcher[K, Any]":
        return DictMatcher(lambda x: key in x)

    @staticmethod
    def contains_keys(*keys: K) -> "DictMatcher[K, Any]":
        return DictMatcher(lambda x: all([key in x for key in keys]))
