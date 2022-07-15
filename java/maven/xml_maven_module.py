from typing import List, Optional

from java.maven.maven_module import MavenModule
from java.maven.xml_maven_module_identifier import XmlMavenModuleIdentifier
from java.maven.xml_maven_property import XmlMavenProperty
from utility.type_utility import get_or_else
from utility.xml.xml_document import XmlDocument


class XmlMavenModule(MavenModule):

    def __init__(self,
                 xml_document: XmlDocument,
                 identifier: XmlMavenModuleIdentifier,
                 parent: Optional["XmlMavenModule"] = None,
                 parent_identifier: Optional[XmlMavenModuleIdentifier] = None,
                 properties: Optional[List[XmlMavenProperty]] = None,
                 dependencies: Optional[List[XmlMavenModuleIdentifier]] = None,
                 modules: Optional[List["XmlMavenModule"]] = None):
        self._xml_document: XmlDocument = xml_document
        self._identifier: XmlMavenModuleIdentifier = identifier
        self._parent: Optional[XmlMavenModule] = parent
        self._parent_identifier: Optional[XmlMavenModuleIdentifier] = parent_identifier
        self._properties: List[XmlMavenProperty] = get_or_else(properties, lambda: [])
        self._dependencies: List[XmlMavenModuleIdentifier] = get_or_else(dependencies, lambda: [])
        self._modules: List[XmlMavenModule] = get_or_else(modules, lambda: [])

    @property
    def xml_document(self) -> XmlDocument:
        return self._xml_document

    @property
    def parent(self) -> Optional["XmlMavenModule"]:
        return self._parent

    @property
    def parent_identifier(self) -> Optional[XmlMavenModuleIdentifier]:
        return self._parent_identifier

    @property
    def identifier(self) -> XmlMavenModuleIdentifier:
        return self._identifier

    @property
    def properties(self) -> List[XmlMavenProperty]:
        return self._properties

    @property
    def dependencies(self) -> List[XmlMavenModuleIdentifier]:
        return self._dependencies

    @property
    def modules(self) -> List["XmlMavenModule"]:
        return self._modules
