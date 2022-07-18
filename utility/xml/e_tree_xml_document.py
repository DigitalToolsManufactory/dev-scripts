import xml.etree.ElementTree
from pathlib import Path
from typing import Optional
from xml.etree.ElementTree import ElementTree, Element, XMLParser, TreeBuilder

from utility.xml.e_tree_xml_node import ETreeXmlNode
from utility.xml.xml_document import XmlDocument
from utility.xml.xml_node import XmlNode


class ETreeXmlDocument(XmlDocument):

    def __init__(self, path: Path):
        super().__init__(path)

        parser: XMLParser = XMLParser(target=TreeBuilder(insert_comments=True))
        self._element_tree: ElementTree = xml.etree.ElementTree.parse(self.path, parser=parser)
        self._root_node: Optional[ETreeXmlNode] = None

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

        ns: str = ""
        if self._root_node is not None:
            ns = self._root_node.namespace

        self._element_tree.write(self.path, encoding="UTF-8", xml_declaration=True, default_namespace=ns)
        self._has_been_modified = False

        # workaround to enforce double quotes
        file_content: str = ""
        with self.path.open("r") as r:
            for line in r:
                if line.strip().startswith("<!--"):
                    # don't replace quotes in XML comments
                    file_content += line

                else:
                    file_content += line.replace("'", '"')

        with self.path.open("w") as w:
            w.write(file_content)
