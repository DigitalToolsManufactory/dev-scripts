import re
from re import Pattern, Match
from typing import List, ClassVar

from collect_release_notes.default_release_note import DefaultReleaseNote
from collect_release_notes.release_note import ReleaseNote
from collect_release_notes.release_note_parser import ReleaseNoteParser


class CommitMessageReleaseNoteParser(ReleaseNoteParser):
    RELEASE_NOTE_HEADER: ClassVar[str] = "-- release note:"
    CATEGORY_PATTERN: ClassVar[Pattern] = re.compile(r"^\[(?P<category>[^]]+)]")
    MULTI_LINE_TEXT_END: ClassVar[str] = "---"

    def parse(self, messages: List[str]) -> List[ReleaseNote]:
        result: List[ReleaseNote] = []

        for message in messages:
            result.extend(self._parse_message(message))

        return result

    def _parse_message(self, message: str) -> List[ReleaseNote]:
        result: List[ReleaseNote] = []

        lines: List[str] = [line.strip() for line in message.split("\n")]

        for i in range(len(lines)):
            line: str = lines[i]

            if not line.lower().startswith(CommitMessageReleaseNoteParser.RELEASE_NOTE_HEADER):
                continue

            line = line.removeprefix(CommitMessageReleaseNoteParser.RELEASE_NOTE_HEADER).strip()

            # region parse categories

            categories: List[str] = []
            while len(line) > 0:
                match: Match = CommitMessageReleaseNoteParser.CATEGORY_PATTERN.match(line)
                if match is None:
                    break

                categories.append(match.group("category"))
                line = line[match.end():].strip()

            # endregion

            text: str
            if line == "|":
                # region parse multi line text

                text_lines: List[str] = []
                while i + 1 < len(lines):
                    i += 1
                    next_line: str = lines[i].strip()
                    if next_line == CommitMessageReleaseNoteParser.MULTI_LINE_TEXT_END:
                        break

                    text_lines.append(next_line)

                text = "\n".join(text_lines)

                # endregion

            else:
                text = line

            if len(text.strip()) > 0:
                result.append(DefaultReleaseNote(text, categories))

        return result
