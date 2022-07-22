import json
from typing import Any, Dict, Union, List
from unittest import TestCase

from varname import nameof


class TypeAssertions:

    def __init__(self):
        raise AssertionError("This utility class must not be instantiated")

    @staticmethod
    def json_equals(test: TestCase, actual: str, expected: Union[str, Dict[str, Any]]) -> None:
        a: Dict[str, Any] = json.loads(actual)

        if isinstance(expected, str):
            e: Dict[str, Any] = json.loads(expected)

        elif isinstance(expected, Dict):
            e: Dict[str, Any] = expected

        else:
            raise TypeError(f"The given '{nameof(expected)}' must be of type str or Dict.")

        test.assertDictEqual(a, e)

    @staticmethod
    def contains_exactly(test: TestCase, actual: List[Any], *expected: Any) -> None:
        TypeAssertions.contains_all(test, actual, *expected)
        TypeAssertions.contains_all(test, list(expected), *actual)

    @staticmethod
    def contains_all(test: TestCase, actual: List[Any], *expected: Any) -> None:
        test.assertTrue(len(actual) >= len(expected))

        for e in expected:
            found: bool = False

            for a in actual:
                if a == e:
                    found = True
                    break

            test.assertTrue(found, f"Element {e} is not contained in {actual}.")
