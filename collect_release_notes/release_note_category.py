import re
from re import Pattern
from typing import Optional, List

from collect_release_notes.release_note import ReleaseNote
from utility.type_utility import get_or_else


class ReleaseNoteCategory:

    def __init__(self,
                 title: str,
                 parent: Optional["ReleaseNoteCategory"] = None,
                 categories: Optional[List["ReleaseNoteCategory"]] = None,
                 format_title: Optional[bool] = True):
        self._title: str = self.format_title(title) if format_title else title
        self._parent: Optional[ReleaseNoteCategory] = parent
        self._categories: List[ReleaseNoteCategory] = get_or_else(categories, list)

    @staticmethod
    def format_title(title: str) -> str:
        result: str = ReleaseNoteCategory._capitalize_words(title, re.compile(r"\s+"), " ")
        result = ReleaseNoteCategory._capitalize_words(result, re.compile(r"-"), "-")
        result = ReleaseNoteCategory._capitalize_words(result, re.compile(r"_"), "_")

        return result

    @staticmethod
    def _capitalize_words(title: str, split_delimiter: Pattern, join_delimiter: str) -> str:
        result: str = ""
        words: List[str] = re.split(split_delimiter, title.strip())
        for i in range(len(words)):
            is_last_word: bool = i == len(words) - 1
            word: str = words[i]

            if len(word) > 0:
                result += word[0].capitalize() + word[1:]

            if not is_last_word:
                result += join_delimiter

        return result

    @property
    def title(self) -> str:
        return self._title

    @property
    def parent(self) -> Optional["ReleaseNoteCategory"]:
        return self._parent

    @property
    def categories(self) -> List["ReleaseNoteCategory"]:
        return self._categories

    def get_titles_recursively(self) -> List[str]:
        if self.parent is None:
            return [self.title]

        titles: List[str] = self.parent.get_titles_recursively()
        titles.append(self.title)

        return titles

    @categories.setter
    def categories(self, categories: List["ReleaseNoteCategory"]) -> None:
        self._categories = categories

    def get_contained_release_notes(self, release_notes: List[ReleaseNote]) -> List[ReleaseNote]:
        titles: List[str] = self.get_titles_recursively()
        return list(filter(lambda x: self._get_category_titles(x) == titles, release_notes))

    @staticmethod
    def _get_category_titles(release_note: ReleaseNote) -> List[str]:
        return [ReleaseNoteCategory.format_title(title) for title in release_note.categories]
