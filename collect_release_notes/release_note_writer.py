from abc import ABC, abstractmethod
from typing import List, Optional

from collect_release_notes.release_note import ReleaseNote
from collect_release_notes.release_note_category_structure import ReleaseNoteCategoryStructure


class ReleaseNoteWriter(ABC):

    @abstractmethod
    def write(self, notes: List[ReleaseNote], category_structure: ReleaseNoteCategoryStructure) -> str:
        raise NotImplementedError
