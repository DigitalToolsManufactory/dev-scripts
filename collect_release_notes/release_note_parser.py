from abc import ABC, abstractmethod
from typing import List

from collect_release_notes.release_note import ReleaseNote


class ReleaseNoteParser(ABC):

    @abstractmethod
    def parse(self, messages: List[str]) -> List[ReleaseNote]:
        raise NotImplementedError
