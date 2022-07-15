from typing import List, Optional

from java.maven.maven_module import MavenModule
from java.maven.xml_maven_module_identifier import XmlMavenModuleIdentifier
from java.maven.xml_maven_property import XmlMavenProperty
from utility.type_utility import get_or_else


class XmlMavenModule(MavenModule):

    def __init__(self,
                 identifier: XmlMavenModuleIdentifier,
                 parent: Optional["XmlMavenModule"] = None,
                 properties: Optional[List[XmlMavenProperty]] = None,
                 dependencies: Optional[List[XmlMavenModuleIdentifier]] = None,
                 modules: Optional[List["XmlMavenModule"]] = None):
        self._identifier: XmlMavenModuleIdentifier = identifier
        self._parent: Optional[XmlMavenModule] = parent
        self._properties: List[XmlMavenProperty] = get_or_else(properties, lambda: [])
        self._dependencies: List[XmlMavenModuleIdentifier] = get_or_else(dependencies, lambda: [])
        self._modules: List[XmlMavenModule] = get_or_else(modules, lambda: [])

    @property
    def parent(self) -> Optional["XmlMavenModule"]:
        return self._parent

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
