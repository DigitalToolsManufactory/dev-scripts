from typing import List
from unittest import TestCase

from collect_release_notes.release_note_category_structure import ReleaseNoteCategory, ReleaseNoteCategoryStructure


class TestReleaseNoteCategoryStructure(TestCase):

    def test_from_titles(self) -> None:
        sut: ReleaseNoteCategoryStructure = ReleaseNoteCategoryStructure.from_titles([
            ["A", "B", "C"],
            ["A", "B", "D"],
            ["A", "C"],
            ["B"],
            ["B", "A", "X"]
        ])

        self.assertCategoriesContainExactlyInOrder(sut.categories, "A", "B")

        self.assertCategoriesContainExactlyInOrder(sut.categories[0].categories, "B", "C")
        self.assertCategoriesContainExactlyInOrder(sut.categories[0].categories[0].categories, "C", "D")
        self.assertCategoriesContainExactlyInOrder(sut.categories[0].categories[1].categories)

        self.assertCategoriesContainExactlyInOrder(sut.categories[1].categories, "A")
        self.assertCategoriesContainExactlyInOrder(sut.categories[1].categories[0].categories, "X")

    def test_extend(self) -> None:
        sut: ReleaseNoteCategoryStructure = ReleaseNoteCategoryStructure.from_titles([
            ["A", "A"],
            ["A", "C"],
            ["B", "B"],
            ["D"],
        ])

        # sanity check
        self.assertCategoriesContainExactlyInOrder(sut.categories, "A", "B", "D")

        self.assertCategoriesContainExactlyInOrder(sut.categories[0].categories, "A", "C")
        self.assertCategoriesContainExactlyInOrder(sut.categories[1].categories, "B")
        self.assertCategoriesContainExactlyInOrder(sut.categories[2].categories)

        new_structure: ReleaseNoteCategoryStructure = ReleaseNoteCategoryStructure.from_titles([
            ["A", "B"],
            ["B"],
            ["C"]
        ])

        sut.extend(new_structure)

        self.assertCategoriesContainExactlyInOrder(sut.categories, "A", "B", "D", "C")

        self.assertCategoriesContainExactlyInOrder(sut.categories[0].categories, "A", "C", "B")
        self.assertCategoriesContainExactlyInOrder(sut.categories[1].categories, "B")
        self.assertCategoriesContainExactlyInOrder(sut.categories[2].categories)
        self.assertCategoriesContainExactlyInOrder(sut.categories[3].categories)

    def assertCategoriesContainExactlyInOrder(self, actual: List[ReleaseNoteCategory], *expected_titles: str) -> None:
        self.assertEqual(len(actual), len(expected_titles))
        self.assertListEqual([category.title for category in actual], list(expected_titles))
