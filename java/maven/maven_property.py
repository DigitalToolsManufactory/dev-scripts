from abc import ABC, abstractmethod
from typing import Optional

from utility.xml_node import MutableXmlNode


class MavenProperty(ABC):

    @property
    @abstractmethod
    def name(self) -> str:
        raise NotImplemented

    @property
    @abstractmethod
    def value(self) -> str:
        raise NotImplemented


class MutableMavenProperty(MavenProperty, ABC):

    @property
    @abstractmethod
    def has_been_modified(self) -> bool:
        raise NotImplemented

    @MavenProperty.value.setter
    @abstractmethod
    def value(self, value: Optional[str]) -> None:
        raise NotImplemented


class XmlMavenProperty(MutableMavenProperty):

    def __init__(self, node: MutableXmlNode):
        self._node: MutableXmlNode = node

    @property
    def name(self) -> str:
        return self._node.name

    @property
    def has_been_modified(self) -> bool:
        return self._node.has_been_modified

    @MavenProperty.value.getter
    def value(self) -> str:
        return self._node.value

    @MutableMavenProperty.value.setter
    def value(self, value: Optional[str]) -> None:
        self._node.value = value
