from abc import ABC, abstractmethod
from pathlib import Path
from typing import Optional, List
from xml.etree.ElementTree import ElementTree, Element


class XmlNode(ABC):

    @property
    @abstractmethod
    def name(self) -> str:
        raise NotImplemented

    @property
    @abstractmethod
    def value(self) -> Optional[str]:
        raise NotImplemented


class MutableXmlNode(XmlNode, ABC):

    def __init__(self, file: Path, document: ElementTree, parent: Optional["MutableXmlNode"] = None):
        self._file: Path = file
        self._document: ElementTree = document
        self._parent: Optional[MutableXmlNode] = parent
        self._has_been_modified: bool = False
        self._children: List[MutableXmlNode] = []

        if self._parent is not None:
            self._parent._children.append(self)

    @property
    def has_been_modified(self) -> bool:
        result: bool = self._has_been_modified

        result &= any(filter(lambda x: x.has_been_modified, self._children))

        return result

    @XmlNode.value.setter
    @abstractmethod
    def value(self, text: Optional[str]) -> None:
        raise NotImplemented

    @abstractmethod
    def save(self) -> None:
        if not self.has_been_modified:
            return

        self._document.write(self._file)
        self._has_been_modified = False
        for child in self._children:
            child._has_been_modified = False


class ETreeXmlNode(MutableXmlNode):

    def __init__(self, file: Path, root: ElementTree, node: Element):
        self._file: Path = file
        self._root: ElementTree = root
        self._node: Element = node
        self._has_been_modified: bool = False

    @property
    def name(self) -> str:
        return self._node.tag

    @property
    def has_been_modified(self) -> bool:
        return self._has_been_modified

    @XmlNode.value.getter
    def value(self) -> Optional[str]:
        return self._node.text

    @MutableXmlNode.value.setter
    def value(self, text: Optional[str]) -> None:
        self._node.text = text
        self._has_been_modified = True

    def save(self) -> None:
        if not self.has_been_modified:
            return

        self._root.write(self._file)
        self._has_been_modified = False


class VirtualXmlNode(MutableXmlNode):

    def __init__(self,
                 actual_node: MutableXmlNode,
                 can_read: bool = True,
                 can_write: bool = False,
                 can_save: bool = False):
        self._delegate: MutableXmlNode = actual_node
        self._can_read: bool = can_read
        self._can_write: bool = can_write
        self._can_save: bool = can_save

    @property
    def name(self) -> str:
        return self._delegate.name

    @property
    def has_been_modified(self) -> bool:
        return self._delegate.has_been_modified

    @XmlNode.value.getter
    def value(self) -> Optional[str]:
        if self._can_read:
            return self._delegate.value()

        return None

    @MutableXmlNode.value.setter
    def value(self, text: Optional[str]) -> None:
        if self._can_write:
            self._delegate.value(text)

    def save(self) -> None:
        if self._can_save:
            self._delegate.save()
