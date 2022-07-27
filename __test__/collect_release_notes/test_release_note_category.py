from typing import List
from unittest import TestCase

from __test__.type_assertions import TypeAssertions
from collect_release_notes.release_note import ReleaseNote
from collect_release_notes.release_note_category_structure import ReleaseNoteCategory


class TestReleaseNoteCategory(TestCase):

    def test_format_title(self) -> None:
        self.assertEqual(ReleaseNoteCategory.format_title(""), "")
        self.assertEqual(ReleaseNoteCategory.format_title("a"), "A")
        self.assertEqual(ReleaseNoteCategory.format_title("-"), "-")
        self.assertEqual(ReleaseNoteCategory.format_title("_"), "_")
        self.assertEqual(ReleaseNoteCategory.format_title("foo"), "Foo")
        self.assertEqual(ReleaseNoteCategory.format_title("FOO"), "FOO")
        self.assertEqual(ReleaseNoteCategory.format_title("fOo"), "FOo")
        self.assertEqual(ReleaseNoteCategory.format_title("foo bar"), "Foo Bar")
        self.assertEqual(ReleaseNoteCategory.format_title(" foo   bar  "), "Foo Bar")
        self.assertEqual(ReleaseNoteCategory.format_title("foo-bar"), "Foo-Bar")
        self.assertEqual(ReleaseNoteCategory.format_title("foo--bar"), "Foo--Bar")
        self.assertEqual(ReleaseNoteCategory.format_title("foo__bar"), "Foo__Bar")

    def test_get_contained_release_notes(self) -> None:
        parent: ReleaseNoteCategory = ReleaseNoteCategory("a")
        child: ReleaseNoteCategory = ReleaseNoteCategory("b", parent)

        parent.categories.append(child)

        release_notes: List[ReleaseNote] = [
            ReleaseNote("foo", ["a"]),
            ReleaseNote("bar", ["b"]),
            ReleaseNote("baz", ["a", "b"]),
        ]

        parent_notes: List[ReleaseNote] = parent.get_contained_release_notes(release_notes)
        TypeAssertions.contains_exactly(self, parent_notes, ReleaseNote("foo", ["a"]))

        child_notes: List[ReleaseNote] = child.get_contained_release_notes(release_notes)
        TypeAssertions.contains_exactly(self, child_notes, ReleaseNote("baz", ["a", "b"]))
