from abc import ABC, abstractmethod
from typing import List


class ReleaseNote(ABC):

    @property
    def categories(self) -> List[str]:
        return self._get_categories()

    @abstractmethod
    def _get_categories(self) -> List[str]:
        raise NotImplementedError

    @property
    def lines(self) -> List[str]:
        return self._get_lines()

    @abstractmethod
    def _get_lines(self) -> List[str]:
        raise NotImplementedError
