from abc import ABC, abstractmethod
from typing import List, Optional


class XmlNode(ABC):
    @property
    @abstractmethod
    def name(self) -> str:
        raise NotImplementedError

    @property
    def namespace(self) -> str:
        return ""

    @property
    def text(self) -> Optional[str]:
        return self._get_text()

    @abstractmethod
    def _get_text(self) -> Optional[str]:
        raise NotImplementedError

    @text.setter
    def text(self, text: str) -> None:
        self._set_text(text)

    @abstractmethod
    def _set_text(self, text: str) -> None:
        raise NotImplemented

    @property
    def nodes(self) -> List["XmlNode"]:
        return self._get_nodes()

    @abstractmethod
    def _get_nodes(self) -> List["XmlNode"]:
        raise NotImplementedError

    @abstractmethod
    def find_first_node(self, *path_segments: str) -> Optional["XmlNode"]:
        raise NotImplementedError

    @abstractmethod
    def find_all_nodes(self, *path_segments: str) -> List["XmlNode"]:
        raise NotImplementedError
