from typing import List, Union, Optional, Any, cast

from utility.type_utility import get_or_else


class ReleaseNote:

    def __init__(self, text: Union[str, List[str]], categories: Optional[List[str]] = None):
        self._lines: List[str] = self._text_to_lines(text)
        self._categories: List[str] = get_or_else(categories, list)

    @staticmethod
    def _text_to_lines(text: Union[str, List[str]]) -> List[str]:
        raw_lines: List[str]
        if isinstance(text, list):
            raw_lines = text

        elif isinstance(text, str):
            raw_lines = text.split("\n")

        else:
            raise AssertionError(f"Text must be of type list or str.")

        result: List[str] = []
        for line in raw_lines:
            result.extend(line.split("\n"))

        return result

    @property
    def categories(self) -> List[str]:
        return self._categories

    @property
    def lines(self) -> List[str]:
        return self._lines

    def __eq__(self, other: Optional[Any]) -> bool:
        if not isinstance(other, ReleaseNote):
            return False

        o: ReleaseNote = cast(ReleaseNote, other)

        return o.lines == self.lines and o.categories == self.categories
