from dataclasses import dataclass, field
from typing import List, Optional

from collect_release_notes.release_note import ReleaseNote
from collect_release_notes.release_note_category_structure import ReleaseNoteCategoryStructure
from collect_release_notes.release_note_parser import ReleaseNoteParser


class MarkdownReleaseNoteParser(ReleaseNoteParser):
    @dataclass(frozen=True)
    class MarkdownNode:
        lines: List[str]
        nodes: List["MarkdownReleaseNoteParser.MarkdownNode"] = field(default_factory=list)

    def __init__(self, markdown_release_notes: str):
        self._markdown_release_notes: str = markdown_release_notes
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
        pass