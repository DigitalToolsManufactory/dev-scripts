from typing import Optional, List

from collect_release_notes.release_note_category import ReleaseNoteCategory
from utility.type_utility import get_or_else


class ReleaseNoteCategoryStructure:

    @staticmethod
    def from_titles(category_titles: List[List[str]]) -> "ReleaseNoteCategoryStructure":
        root_categories: List[ReleaseNoteCategory] = []

        for title_sequence in category_titles:
            ReleaseNoteCategoryStructure._add_categories_recursively(title_sequence, root_categories)

        return ReleaseNoteCategoryStructure(root_categories)

    @staticmethod
    def find_existing_category(expected_title_sequence: List[str],
                               categories: List[ReleaseNoteCategory]) -> Optional[ReleaseNoteCategory]:
        if len(expected_title_sequence) < 1:
            return None

        next_title: str = ReleaseNoteCategory.format_title(expected_title_sequence[0])
        category: Optional[ReleaseNoteCategory] = ReleaseNoteCategoryStructure._find_category(next_title, categories)

        if category is None:
            return None

        if len(expected_title_sequence) == 1:
            return category

        return ReleaseNoteCategoryStructure.find_existing_category(expected_title_sequence[1:], category.categories)

    @staticmethod
    def _add_categories_recursively(title_sequence: List[str],
                                    categories: List[ReleaseNoteCategory],
                                    parent: Optional[ReleaseNoteCategory] = None) -> None:
        if len(title_sequence) < 1:
            return None

        next_title: str = ReleaseNoteCategory.format_title(title_sequence[0])
        category: Optional[ReleaseNoteCategory] = ReleaseNoteCategoryStructure._find_category(next_title, categories)

        if category is None:
            category = ReleaseNoteCategory(next_title, parent, format_title=False)
            categories.append(category)

        ReleaseNoteCategoryStructure._add_categories_recursively(title_sequence[1:], category.categories, category)

    @staticmethod
    def _find_category(expected_title: str, categories: List[ReleaseNoteCategory]) -> Optional[ReleaseNoteCategory]:
        matching_categories: List[ReleaseNoteCategory] = list(filter(lambda x: x.title == expected_title, categories))
        if len(matching_categories) > 1:
            raise AssertionError(f"Found duplicated category '{expected_title}'.")

        if len(matching_categories) < 1:
            return None

        return matching_categories[0]

    def __init__(self, categories: Optional[List[ReleaseNoteCategory]] = None):
        self._categories: List[ReleaseNoteCategory] = get_or_else(categories, list)

    @property
    def categories(self) -> List[ReleaseNoteCategory]:
        return self._categories

    @categories.setter
    def categories(self, categories: List[ReleaseNoteCategory]) -> None:
        self._categories = categories

    def extend(self, structure: "ReleaseNoteCategoryStructure") -> None:
        self._categories = self._merge_structures(self.categories, structure.categories)

    def _merge_structures(self,
                          a: List[ReleaseNoteCategory],
                          b: List[ReleaseNoteCategory]) -> List[ReleaseNoteCategory]:
        result: List[ReleaseNoteCategory] = list(a)

        for category in b:
            matching_categories: List[ReleaseNoteCategory] = list(filter(lambda x: x.title == category.title, a))

            if len(matching_categories) > 1:
                raise AssertionError(f"Found duplicated category '{category.title}'.")

            parent_category: ReleaseNoteCategory
            if len(matching_categories) < 1:
                parent_category = category
                result.append(category)

            else:
                parent_category = matching_categories[0]

            parent_category.categories = self._merge_structures(parent_category.categories, category.categories)

        return result
