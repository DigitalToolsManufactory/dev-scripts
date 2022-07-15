from abc import ABC, abstractmethod
from pathlib import Path
from typing import Optional

from utility.xml.xml_node import XmlNode


class XmlDocument(ABC):

    def __init__(self, path: Path):
        self._path: Path = path
        self._has_been_modified: bool = False

    @property
    def path(self) -> Path:
        return self._path

    @property
    def has_been_modified(self) -> bool:
        return self._has_been_modified

    def mark_as_modified(self) -> None:
        self._has_been_modified = True

    @abstractmethod
    def try_find_node(self, *path_segments: str) -> Optional[XmlNode]:
        raise NotImplemented

    @abstractmethod
    def save(self) -> None:
        raise NotImplemented
