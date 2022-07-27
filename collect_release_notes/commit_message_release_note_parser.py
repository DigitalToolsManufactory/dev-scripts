import re
from re import Pattern, Match, RegexFlag
from typing import List, ClassVar, Optional

from collect_release_notes.release_note import ReleaseNote
from collect_release_notes.release_note_category_structure import ReleaseNoteCategoryStructure, ReleaseNoteCategory
from collect_release_notes.release_note_parser import ReleaseNoteParser


class CommitMessageReleaseNoteParser(ReleaseNoteParser):
    RELEASE_NOTE_HEADER: ClassVar[Pattern] = re.compile(r"^\s*>>\s*release\s+note\s*:\s*", RegexFlag.IGNORECASE)
    CATEGORY_PATTERN: ClassVar[Pattern] = re.compile(r"^\[(?P<category>[^]]+)]")
    MULTI_LINE_TEXT_END: ClassVar[Pattern] = re.compile(r"^\s*<<<\s*$")

    def __init__(self, commit_messages: List[str]):
        self._commit_messages: List[str] = commit_messages
        self._release_notes: Optional[List[ReleaseNote]] = None
        self._release_note_category_structure: Optional[ReleaseNoteCategoryStructure] = None

    def _get_release_notes(self) -> List[ReleaseNote]:
        if self._release_notes is None:
            self._parse()

        return self._release_notes

    def _get_release_note_category_structure(self) -> ReleaseNoteCategoryStructure:
        if self._release_note_category_structure is None:
            self._parse()

        return self._release_note_category_structure

    def _parse(self) -> None:
        release_notes: List[ReleaseNote] = []
        categories: List[ReleaseNoteCategory] = []

        for commit_message in self._commit_messages:
            self._parse_commit_message(commit_message, release_notes, categories)

        categories = self._sort_categories_by_title_recursively(categories)
        self._release_notes = release_notes
        self._release_note_category_structure = ReleaseNoteCategoryStructure(categories)

    def _parse_commit_message(self,
                              commit_message: str,
                              release_notes: List[ReleaseNote],
                              categories: List[ReleaseNoteCategory]) -> None:
        lines: List[str] = [line.strip() for line in commit_message.split("\n")]

        for i in range(len(lines)):
            line: str = lines[i]

            header_match: Match = CommitMessageReleaseNoteParser.RELEASE_NOTE_HEADER.match(line)

            if header_match is None:
                continue

            line = line[header_match.end():].strip()

            # region parse categories

            category_titles: List[str] = []
            while len(line) > 0:
                match: Match = CommitMessageReleaseNoteParser.CATEGORY_PATTERN.match(line)
                if match is None:
                    break

                category_titles.append(match.group("category").strip())
                line = line[match.end():].strip()

            # endregion

            text: str
            if line == "|":
                # region parse multi line text

                text_lines: List[str] = []
                while i + 1 < len(lines):
                    i += 1
                    next_line: str = lines[i].strip()
                    end_match: Match = CommitMessageReleaseNoteParser.MULTI_LINE_TEXT_END.match(next_line)
                    if end_match is not None:
                        break

                    text_lines.append(next_line)

                text = "\n".join(text_lines)

                # endregion

            else:
                text = line

            if len(text.strip()) > 0:
                maybe_category: Optional[ReleaseNoteCategory] = self._get_or_add_category(categories, category_titles)
                titles: List[str] = [] if maybe_category is None else maybe_category.get_titles_recursively()
                release_notes.append(ReleaseNote(text, titles))

    def _get_or_add_category(self,
                             categories: List[ReleaseNoteCategory],
                             category_titles: List[str]) -> Optional[ReleaseNoteCategory]:
        parent_category: Optional[ReleaseNoteCategory] = None
        category: Optional[ReleaseNoteCategory] = None
        for category_title in category_titles:
            title: str = ReleaseNoteCategory.format_title(category_title)
            category = self._find_existing_category(title, categories, parent_category)
            if category is None:
                category = ReleaseNoteCategory(title, parent_category, format_title=False)
                if parent_category is not None:
                    parent_category.categories.append(category)

                else:
                    categories.append(category)

            parent_category = category

        return category

    @staticmethod
    def _find_existing_category(expected_title: str,
                                root_categories: List[ReleaseNoteCategory],
                                parent_category: Optional[ReleaseNoteCategory]) -> Optional[ReleaseNoteCategory]:
        categories: List[ReleaseNoteCategory]
        if parent_category is not None:
            categories = parent_category.categories

        else:
            categories = root_categories

        matching_categories: List[ReleaseNoteCategory] = list(filter(lambda x: x.title == expected_title, categories))
        if len(matching_categories) > 1:
            raise AssertionError(f"Found duplicated category '{expected_title}'.")

        if len(matching_categories) < 1:
            return None

        return matching_categories[0]

    @staticmethod
    def _sort_categories_by_title_recursively(categories: List[ReleaseNoteCategory]) -> List[ReleaseNoteCategory]:
        sorted_categories: List[ReleaseNoteCategory] = sorted(categories, key=lambda x: x.title)

        for category in sorted_categories:
            category.categories = CommitMessageReleaseNoteParser._sort_categories_by_title_recursively(
                category.categories
            )

        return sorted_categories
