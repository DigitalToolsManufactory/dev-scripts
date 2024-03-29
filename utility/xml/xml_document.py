from abc import ABC, abstractmethod
from pathlib import Path
from typing import List, Optional

from utility.xml.xml_node import XmlNode


class XmlDocument(ABC):
    @abstractmethod
    def find_first_node(self, *path_segments: str) -> Optional[XmlNode]:
        raise NotImplementedError

    @abstractmethod
    def find_all_nodes(self, *path_segments: str) -> List[XmlNode]:
        raise NotImplementedError

    @abstractmethod
    def save(self, file: Path) -> None:
        raise NotImplementedError
