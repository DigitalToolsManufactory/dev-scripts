from abc import ABC, abstractmethod
from typing import List

from collect_release_notes.release_note import ReleaseNote
from collect_release_notes.release_note_category_structure import ReleaseNoteCategoryStructure


class ReleaseNoteParser(ABC):

    @property
    def release_notes(self) -> List[ReleaseNote]:
        return self._get_release_notes()

    @abstractmethod
    def _get_release_notes(self) -> List[ReleaseNote]:
        raise NotImplementedError

    @property
    def release_note_category_structure(self) -> ReleaseNoteCategoryStructure:
        return self._get_release_note_category_structure()

    @abstractmethod
    def _get_release_note_category_structure(self) -> ReleaseNoteCategoryStructure:
        raise NotImplementedError
