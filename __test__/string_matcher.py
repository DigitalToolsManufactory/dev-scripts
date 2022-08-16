import re
from dataclasses import dataclass
from typing import Callable, Optional, Pattern, Union


@dataclass(frozen=True)
class StringMatcher:
    delegate: Callable[[str], bool]

    def matches(self, command: str) -> bool:
        return self.delegate(command)

    @staticmethod
    def any() -> Optional["StringMatcher"]:
        return None

    @staticmethod
    def contains_regex(regex: Union[str, Pattern]) -> "StringMatcher":
        if isinstance(regex, str):
            compiled_pattern: Pattern = re.compile(r"^.*" + regex + ".*$")

        elif isinstance(regex, Pattern):
            compiled_pattern: Pattern = re.compile(r"^.*" + regex.pattern + ".*$")

        else:
            raise TypeError(
                f"The given 'regex' ('{regex}') must be either of type 'str' or 'Pattern'"
            )

        return StringMatcher.regex(compiled_pattern)

    @staticmethod
    def regex(regex: Union[str, Pattern]) -> "StringMatcher":
        if isinstance(regex, str):
            compiled_regex: Pattern = re.compile(regex)

        elif isinstance(regex, Pattern):
            compiled_regex: Pattern = regex

        else:
            raise TypeError(
                f"The given 'regex' ('{regex}') must be either of type 'str' or 'Pattern'"
            )

        def try_match(string: str) -> bool:
            try:
                return compiled_regex.match(string) is not None

            except:
                return False

        return StringMatcher(try_match)

    @staticmethod
    def contains_exact(expected: str) -> "StringMatcher":
        return StringMatcher(lambda x: expected in x)

    @staticmethod
    def exact(expected: str) -> "StringMatcher":
        return StringMatcher(lambda x: x == expected)
