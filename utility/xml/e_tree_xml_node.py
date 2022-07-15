import re
from typing import Optional, ClassVar, List
from xml.etree.ElementTree import Element

from utility.xml.xml_document import XmlDocument
from utility.xml.xml_node import XmlNode


class ETreeXmlNode(XmlNode):
    NAME_PATTERN: ClassVar[re.Pattern] = re.compile(r"^(?P<namespace>\{[^}]+})?(?P<tag>.+)$")

    def __init__(self, document: XmlDocument, element: Element, parent: Optional["ETreeXmlNode"] = None):
        self._document: XmlDocument = document
        self._element: Element = element
        self._parent: Optional[ETreeXmlNode] = parent
        self._name: str = self._element.tag
        self._namespace: str = ""
        self._nodes: Optional[List[XmlNode]] = None

        name_match: re.Match = ETreeXmlNode.NAME_PATTERN.match(self._element.tag)
        if name_match is not None:
            self._name = name_match.group("tag")

            if "namespace" in name_match.groupdict():
                self._namespace = name_match.group("namespace")

    @property
    def name(self) -> str:
        return self._name

    @property
    def path(self) -> List[str]:
        result: List[str] = []

        if self._parent is not None:
            result.extend(self._parent.path)

        result.append(self.name)
        return result

    @property
    def value(self) -> Optional[str]:
        return self._element.text

    def _set_value(self, value: Optional[str]) -> None:
        self._element.text = value
        self._document.mark_as_modified()

    @property
    def nodes(self) -> List["XmlNode"]:
        if self._nodes is None:
            self._nodes = [ETreeXmlNode(self._document, element, self) for element in self._element]

        return self._nodes

    def try_find_node(self, *path_segments: str) -> Optional["XmlNode"]:
        if len(path_segments) < 1:
            return self

        for matching_node in filter(lambda x: x.name == path_segments[0], self.nodes):
            found_node: Optional[XmlNode] = matching_node.try_find_node(*path_segments[1:])

            if found_node is not None:
                return found_node

        return None
