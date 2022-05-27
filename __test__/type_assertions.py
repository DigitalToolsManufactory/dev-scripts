import json
from typing import Any, Dict, Union
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
