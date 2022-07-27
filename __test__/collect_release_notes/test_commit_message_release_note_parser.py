from typing import List
from unittest import TestCase

from __test__.type_assertions import TypeAssertions
from collect_release_notes.commit_message_release_note_parser import CommitMessageReleaseNoteParser
from collect_release_notes.release_note import ReleaseNote
from collect_release_notes.release_note_category_structure import ReleaseNoteCategory


class TestCommitMessageReleaseNoteParser(TestCase):

    def test_parse_empty_messages(self) -> None:
        sut: CommitMessageReleaseNoteParser = CommitMessageReleaseNoteParser([])

        self.assertListEqual(sut.release_notes, [])
        self.assertListEqual(sut.release_note_category_structure.categories, [])

    def test_parse_commit_message_without_release_note(self) -> None:
        sut: CommitMessageReleaseNoteParser = CommitMessageReleaseNoteParser(["this is just some commit message"])

        self.assertListEqual(sut.release_notes, [])
        self.assertListEqual(sut.release_note_category_structure.categories, [])

    def test_parse_commit_message_with_invalid_release_note_format(self) -> None:
        sut: CommitMessageReleaseNoteParser = CommitMessageReleaseNoteParser([
            "release notes must start at the line start -- release note: foo"
        ])

        self.assertListEqual(sut.release_notes, [])
        self.assertListEqual(sut.release_note_category_structure.categories, [])

    def test_parse_one_single_line_release_note_without_category(self) -> None:
        sut: CommitMessageReleaseNoteParser = CommitMessageReleaseNoteParser([
            "this is just some commit message\n" +
            "\n" +
            ">> release note: Release note without category"
        ])

        TypeAssertions.contains_exactly(self, sut.release_notes, ReleaseNote("Release note without category", []))
        self.assertListEqual(sut.release_note_category_structure.categories, [])

    def test_parse_one_single_line_release_note_with_single_category(self) -> None:
        sut: CommitMessageReleaseNoteParser = CommitMessageReleaseNoteParser([
            "this is just some commit message\n" +
            "\n" +
            ">> release note: [a] Release note without category"
        ])

        TypeAssertions.contains_exactly(self, sut.release_notes,
                                        ReleaseNote("Release note without category", ["A"]))
        self.assertCategoriesContainExactlyInOrder(sut.release_note_category_structure.categories, "A")

    def test_parse_one_single_line_release_note_with_nested_category(self) -> None:
        sut: CommitMessageReleaseNoteParser = CommitMessageReleaseNoteParser([
            "this is just some commit message\n" +
            "\n" +
            ">> release note: [a][b] Release note without category"
        ])

        TypeAssertions.contains_exactly(self, sut.release_notes,
                                        ReleaseNote("Release note without category", ["A", "B"]))
        self.assertCategoriesContainExactlyInOrder(sut.release_note_category_structure.categories, "A")
        self.assertCategoriesContainExactlyInOrder(sut.release_note_category_structure.categories[0].categories, "B")

    def test_parse_multiple_single_line_release_notes_without_categories(self) -> None:
        sut: CommitMessageReleaseNoteParser = CommitMessageReleaseNoteParser([
            "this is just some commit message\n" +
            "\n" +
            ">> release note: First note\n" +
            "some more noise\n" +
            ">> release note: Second note"
        ])

        TypeAssertions.contains_exactly(self,
                                        sut.release_notes,
                                        ReleaseNote("First note", []),
                                        ReleaseNote("Second note", []))
        self.assertListEqual(sut.release_note_category_structure.categories, [])

    def test_parse_multiple_single_line_release_notes_with_single_category(self) -> None:
        sut: CommitMessageReleaseNoteParser = CommitMessageReleaseNoteParser([
            "this is just some commit message\n" +
            "\n" +
            ">> release note: [b] First note\n" +
            "some more noise\n" +
            ">> release note: [a] Second note"
        ])

        TypeAssertions.contains_exactly(self,
                                        sut.release_notes,
                                        ReleaseNote("First note", ["B"]),
                                        ReleaseNote("Second note", ["A"]))
        self.assertCategoriesContainExactlyInOrder(sut.release_note_category_structure.categories, "A", "B")

    def test_parse_multiple_single_line_release_notes_with_nested_categories(self) -> None:
        sut: CommitMessageReleaseNoteParser = CommitMessageReleaseNoteParser([
            "this is just some commit message\n" +
            "\n" +
            ">> release note: [b][a] First note\n" +
            "some more noise\n" +
            ">> release note: [a][b] Second note\n" +
            ">> release note: [a][a] Third note"
        ])

        TypeAssertions.contains_exactly(self,
                                        sut.release_notes,
                                        ReleaseNote("First note", ["B", "A"]),
                                        ReleaseNote("Second note", ["A", "B"]),
                                        ReleaseNote("Third note", ["A", "A"]))
        self.assertCategoriesContainExactlyInOrder(sut.release_note_category_structure.categories, "A", "B")
        self.assertCategoriesContainExactlyInOrder(sut.release_note_category_structure.categories[0].categories,
                                                   "A",
                                                   "B")
        self.assertCategoriesContainExactlyInOrder(sut.release_note_category_structure.categories[1].categories,
                                                   "A")

    def test_parse_one_multi_line_release_note_without_category(self) -> None:
        sut: CommitMessageReleaseNoteParser = CommitMessageReleaseNoteParser([
            "this is just some commit message\n" +
            "\n" +
            ">> release note: |\n" +
            "Line 1\n" +
            "\n" +
            "Line 3\n" +
            "<<<\n" +
            "some more noise"
        ])

        TypeAssertions.contains_exactly(self, sut.release_notes, ReleaseNote(["Line 1", "", "Line 3"], []))
        self.assertListEqual(sut.release_note_category_structure.categories, [])

    def test_parse_one_multi_line_release_note_with_single_category(self) -> None:
        sut: CommitMessageReleaseNoteParser = CommitMessageReleaseNoteParser([
            "this is just some commit message\n" +
            "\n" +
            ">> release note: [a] |\n" +
            "Line 1\n" +
            "\n" +
            "Line 3\n" +
            "<<<\n" +
            "some more noise"
        ])

        TypeAssertions.contains_exactly(self, sut.release_notes, ReleaseNote(["Line 1", "", "Line 3"], ["A"]))
        self.assertCategoriesContainExactlyInOrder(sut.release_note_category_structure.categories, "A")

    def test_parse_one_multi_line_release_note_with_nested_category(self) -> None:
        sut: CommitMessageReleaseNoteParser = CommitMessageReleaseNoteParser([
            "this is just some commit message\n" +
            "\n" +
            ">> release note: [a][b] |\n" +
            "Line 1\n" +
            "\n" +
            "Line 3\n" +
            "<<<\n" +
            "some more noise"
        ])

        TypeAssertions.contains_exactly(self, sut.release_notes, ReleaseNote(["Line 1", "", "Line 3"], ["A", "B"]))
        self.assertCategoriesContainExactlyInOrder(sut.release_note_category_structure.categories, "A")
        self.assertCategoriesContainExactlyInOrder(sut.release_note_category_structure.categories[0].categories, "B")

    def test_parse_multiple_multi_line_release_note_without_categories(self) -> None:
        sut: CommitMessageReleaseNoteParser = CommitMessageReleaseNoteParser([
            "this is just some commit message\n" +
            "\n" +
            ">> release note: |\n" +
            "Line 1\n" +
            "\n" +
            "Line 3\n" +
            "<<<\n" +
            "some more noise\n" +
            ">> release note: |\n" +
            "Line 4\n" +
            "Line 5"
        ])

        TypeAssertions.contains_exactly(self,
                                        sut.release_notes,
                                        ReleaseNote(["Line 1", "", "Line 3"], []),
                                        ReleaseNote(["Line 4", "Line 5"], []))
        self.assertListEqual(sut.release_note_category_structure.categories, [])

    def test_parse_multiple_multi_line_release_note_with_single_category(self) -> None:
        sut: CommitMessageReleaseNoteParser = CommitMessageReleaseNoteParser([
            "this is just some commit message\n" +
            "\n" +
            ">> release note: [b] |\n" +
            "Line 1\n" +
            "\n" +
            "Line 3\n" +
            "<<<\n" +
            "some more noise\n" +
            ">> release note: [a] |\n" +
            "Line 4\n" +
            "Line 5"
        ])

        TypeAssertions.contains_exactly(self,
                                        sut.release_notes,
                                        ReleaseNote(["Line 1", "", "Line 3"], ["B"]),
                                        ReleaseNote(["Line 4", "Line 5"], ["A"]))
        self.assertCategoriesContainExactlyInOrder(sut.release_note_category_structure.categories, "A", "B")

    def test_parse_multiple_multi_line_release_note_with_nested_categories(self) -> None:
        sut: CommitMessageReleaseNoteParser = CommitMessageReleaseNoteParser([
            "this is just some commit message\n" +
            "\n" +
            ">> release note: [b][a] |\n" +
            "Line 1\n" +
            "\n" +
            "Line 3\n" +
            "<<<\n" +
            "some more noise\n" +
            ">> release note: [a][b] |\n" +
            "Line 4\n" +
            "Line 5\n" +
            "<<<\n" +
            ">> release note: [a][a] |\n" +
            "Line 6"
        ])

        TypeAssertions.contains_exactly(self,
                                        sut.release_notes,
                                        ReleaseNote(["Line 1", "", "Line 3"], ["B", "A"]),
                                        ReleaseNote(["Line 4", "Line 5"], ["A", "B"]),
                                        ReleaseNote(["Line 6"], ["A", "A"]))
        self.assertCategoriesContainExactlyInOrder(sut.release_note_category_structure.categories, "A", "B")
        self.assertCategoriesContainExactlyInOrder(sut.release_note_category_structure.categories[0].categories,
                                                   "A",
                                                   "B")
        self.assertCategoriesContainExactlyInOrder(sut.release_note_category_structure.categories[1].categories,
                                                   "A")

    def assertCategoriesContainExactlyInOrder(self, actual: List[ReleaseNoteCategory], *expected_titles: str) -> None:
        self.assertEqual(len(actual), len(expected_titles))
        self.assertListEqual([category.title for category in actual], list(expected_titles))
