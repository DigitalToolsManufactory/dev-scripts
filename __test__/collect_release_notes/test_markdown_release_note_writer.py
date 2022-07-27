from typing import List
from unittest import TestCase

from collect_release_notes.markdown_release_note_writer import MarkdownReleaseNoteWriter
from collect_release_notes.release_note import ReleaseNote
from collect_release_notes.release_note_category_structure import ReleaseNoteCategoryStructure


class TestMarkdownReleaseNoteWriter(TestCase):

    def test_write_without_predefined_structure(self) -> None:
        release_notes: List[ReleaseNote] = [
            ReleaseNote("Single line release note", ["1. Known Issues"]),
            ReleaseNote(["Multi line release note:", "", "```python", "foo = bar", "```"], ["1. Known Issues"]),
            ReleaseNote("Some improvement", ["2. Improvements"]),
            ReleaseNote("Update [Dependency A](link-to-a.example) from `A.B.C` to `A.B.D`",
                        ["2. Improvements", "Updated Dependencies"]),
            ReleaseNote("Update [Dependency B](link-to-b.example) from `X.Y.Z` to `Y.0.0`",
                        ["2. Improvements", "Updated Dependencies"]),
        ]

        category_structure: ReleaseNoteCategoryStructure = ReleaseNoteCategoryStructure.from_titles([
            ["1. Known Issues"],
            ["2. Improvements", "Updated Dependencies"]
        ])

        sut: MarkdownReleaseNoteWriter = MarkdownReleaseNoteWriter()

        markdown: str = sut.write(release_notes, category_structure)

        self.assertEqual(markdown, """## 1. Known Issues

* Single line release note
* Multi line release note:
  
  ```python
  foo = bar
  ```

## 2. Improvements

* Some improvement
* **Updated Dependencies:**
    * Update [Dependency A](link-to-a.example) from `A.B.C` to `A.B.D`
    * Update [Dependency B](link-to-b.example) from `X.Y.Z` to `Y.0.0`
""")
