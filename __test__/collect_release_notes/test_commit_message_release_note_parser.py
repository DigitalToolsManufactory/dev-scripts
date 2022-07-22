from unittest import TestCase

from __test__.type_assertions import TypeAssertions
from collect_release_notes.commit_message_release_note_parser import CommitMessageReleaseNoteParser
from collect_release_notes.default_release_note import DefaultReleaseNote


class TestCommitMessageReleaseNoteParser(TestCase):

    def test_parse_message_without_release_note(self) -> None:
        sut: CommitMessageReleaseNoteParser = CommitMessageReleaseNoteParser()

        self.assertListEqual(sut.parse([]), [])
        self.assertListEqual(sut.parse(["this is just some random commit message"]), [])
        self.assertListEqual(sut.parse(["release notes must start at the line start -- release note: foo"]), [])

    def test_parse_single_line_release_note(self) -> None:
        sut: CommitMessageReleaseNoteParser = CommitMessageReleaseNoteParser()

        TypeAssertions.contains_exactly(self,
                                        sut.parse(["-- release note: [Category] Text"]),
                                        DefaultReleaseNote("Text", ["Category"]))

        TypeAssertions.contains_exactly(self,
                                        sut.parse(["  -- release note: [C1] T1\n"
                                                   "-- release note: [C2][C3] T2"]),
                                        DefaultReleaseNote("T1", ["C1"]),
                                        DefaultReleaseNote("T2", ["C2", "C3"]))

        TypeAssertions.contains_exactly(self,
                                        sut.parse(["\t-- release note: T1", "-- release note: [C]T2"]),
                                        DefaultReleaseNote("T1"),
                                        DefaultReleaseNote("T2", ["C"]))

    def test_parse_ignores_empty_release_note_in_single_line(self) -> None:
        sut: CommitMessageReleaseNoteParser = CommitMessageReleaseNoteParser()

        self.assertListEqual(sut.parse(["-- release note: [C]"]), [])

    def test_parse_multi_line_release_note(self) -> None:
        sut: CommitMessageReleaseNoteParser = CommitMessageReleaseNoteParser()

        TypeAssertions.contains_exactly(self,
                                        sut.parse(["-- release note: [C1][C2] |\n"
                                                   " Line 1 \n"
                                                   "  \n"
                                                   "Line 2  \n"
                                                   "---"]),
                                        DefaultReleaseNote(["Line 1", "", "Line 2"], ["C1", "C2"]))

        TypeAssertions.contains_exactly(self,
                                        sut.parse(["-- release note: [C1][C2] |\n"
                                                   "L1\n"
                                                   "L2\n"
                                                   "---\n"
                                                   "-- release note: [C3]|\n"
                                                   "L3\n"
                                                   "---"]),
                                        DefaultReleaseNote(["L1", "L2"], ["C1", "C2"]),
                                        DefaultReleaseNote(["L3"], ["C3"]))

        TypeAssertions.contains_exactly(self,
                                        sut.parse(["-- release note: [C1][C2] |\n"
                                                   "L1\n"
                                                   "L2\n"
                                                   "---\n"
                                                   "-- release note: [C3]|\n"
                                                   "L3"]),  # last multiline note doesn't need suffix
                                        DefaultReleaseNote(["L1", "L2"], ["C1", "C2"]),
                                        DefaultReleaseNote(["L3"], ["C3"]))

    def test_parse_ignores_empty_release_note_in_multi_line(self) -> None:
        sut: CommitMessageReleaseNoteParser = CommitMessageReleaseNoteParser()

        self.assertListEqual(sut.parse(["-- release note: [C] |\n"
                                        "---"]), [])
        self.assertListEqual(sut.parse(["-- release note: [C] |"]), [])
