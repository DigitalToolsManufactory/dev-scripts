from abc import ABC, abstractmethod
from typing import Optional, List


class XmlNode(ABC):

    @property
    @abstractmethod
    def name(self) -> str:
        raise NotImplemented

    @property
    @abstractmethod
    def path(self) -> List[str]:
        raise NotImplemented

    @property
    @abstractmethod
    def value(self) -> Optional[str]:
        raise NotImplemented

    @abstractmethod
    def set_value(self, value: Optional[str]) -> None:
        raise NotImplemented

    @property
    def nodes(self) -> List["XmlNode"]:
        raise NotImplemented

    @abstractmethod
    def try_find_node(self, *path_segments: str) -> Optional["XmlNode"]:
        raise NotImplemented
