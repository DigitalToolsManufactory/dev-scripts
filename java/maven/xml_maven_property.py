from java.maven.maven_property import MavenProperty
from utility.xml.xml_node import XmlNode


class XmlMavenProperty(MavenProperty):

    def __init__(self, xml_node: XmlNode):
        self._xml_node: XmlNode = xml_node

    @property
    def name(self) -> str:
        return self._xml_node.name

    @property
    def value(self) -> str:
        return self._xml_node.value

    def _set_value(self, value: str) -> None:
        self._xml_node.value = value

    @property
    def node(self) -> XmlNode:
        return self._xml_node
