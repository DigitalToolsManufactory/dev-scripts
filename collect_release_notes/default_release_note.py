from typing import List, Optional, cast, Union

from collect_release_notes.release_note import ReleaseNote
from utility.type_utility import get_or_else


class DefaultReleaseNote(ReleaseNote):

    def __init__(self, text: Union[str, List[str]], categories: Optional[List[str]] = None):
        self._lines: List[str] = self._text_to_lines(text)
        self._categories: List[str] = get_or_else(categories, list)

    def _text_to_lines(self, text: Union[str, List[str]]) -> List[str]:
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

    def _get_categories(self) -> List[str]:
        return self._categories

    def _get_lines(self) -> List[str]:
        return self._lines

    def __eq__(self, other: Optional[ReleaseNote]) -> bool:
        if not isinstance(other, DefaultReleaseNote):
            return False

        o: DefaultReleaseNote = cast(DefaultReleaseNote, other)
        return o.lines == self.lines and o.categories == self.categories
