from java.maven.maven_module_identifier import MavenModuleIdentifier
from utility.xml.xml_node import XmlNode


class XmlMavenModuleIdentifier(MavenModuleIdentifier):

    def __init__(self, group_id_node: XmlNode, artifact_id_node: XmlNode, version_node: XmlNode):
        self._group_id_node: XmlNode = group_id_node
        self._artifact_id_node: XmlNode = artifact_id_node
        self._version_node: XmlNode = version_node

    @property
    def group_id(self) -> str:
        return self._group_id_node.value

    @property
    def artifact_id(self) -> str:
        return self._artifact_id_node.value

    @property
    def version(self) -> str:
        return self._version_node.value

    @property
    def group_id_node(self) -> XmlNode:
        return self._group_id_node

    @property
    def artifact_id_node(self) -> XmlNode:
        return self._artifact_id_node

    @property
    def version_node(self) -> XmlNode:
        return self._version_node

    def _set_version(self, version: str) -> None:
        self._version_node.value = version
