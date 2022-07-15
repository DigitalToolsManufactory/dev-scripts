import xml.etree.ElementTree
from pathlib import Path
from typing import Optional
from xml.etree.ElementTree import ElementTree, Element

from utility.xml.e_tree_xml_node import ETreeXmlNode
from utility.xml.xml_document import XmlDocument
from utility.xml.xml_node import XmlNode


class ETreeXmlDocument(XmlDocument):

    def __init__(self, path: Path):
        super().__init__(path)
        self._element_tree: ElementTree = xml.etree.ElementTree.parse(self.path)
        self._root_node: Optional[ETreeXmlDocument] = None

        root_element: Optional[Element] = self._element_tree.getroot()
        if root_element is not None:
            self._root_node = ETreeXmlNode(self, root_element)

    def try_find_node(self, *path_segments: str) -> Optional[XmlNode]:
        if len(path_segments) < 1:
            return None

        if self._root_node.name != path_segments[0]:
            return None

        return self._root_node.try_find_node(*path_segments[1:])

    def save(self) -> None:
        if not self.has_been_modified:
            return

        self._element_tree.write(self.path)
        self._has_been_modified = False
