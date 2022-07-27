from typing import List, Optional

from collect_release_notes.release_note import ReleaseNote
from collect_release_notes.release_note_category_structure import ReleaseNoteCategoryStructure, ReleaseNoteCategory
from collect_release_notes.release_note_writer import ReleaseNoteWriter


class MarkdownReleaseNoteWriter(ReleaseNoteWriter):

    def write(self, notes: List[ReleaseNote], category_structure: ReleaseNoteCategoryStructure) -> str:
        lines: List[str] = []
        for category in category_structure.categories:
            lines.extend(self._write_release_notes(notes, category))
            lines.append("")

        return "\n".join(lines)

    def _write_release_notes(self,
                             notes: List[ReleaseNote],
                             category: ReleaseNoteCategory,
                             indent: Optional[int] = 0) -> List[str]:
        result: List[str] = []
        category_is_headline: bool = indent == 0

        if category_is_headline:
            result.append(f"## {category.title}")
            result.append("")

        else:
            title: str = category.title
            if not title.endswith(":"):
                title += ":"

            title_indent: str = " " * (indent - 1) * 4
            result.append(f"{title_indent}* **{title}**")

        note_indent: str = " " * indent * 4
        note_first_line_prefix: str = f"{note_indent}*"
        note_further_lines_prefix: str = f"{note_indent} "
        for note in category.get_contained_release_notes(notes):
            for i in range(len(note.lines)):
                is_first_line: bool = i == 0
                line: str = note.lines[i]

                if is_first_line:
                    result.append(f"{note_first_line_prefix} {line}")

                else:
                    result.append(f"{note_further_lines_prefix} {line}")

        for sub_category in category.categories:
            result.extend(self._write_release_notes(notes, sub_category, indent + 1))

        return result
