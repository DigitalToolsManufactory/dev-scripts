from abc import ABC, abstractmethod
from typing import Optional, List

from java.maven.maven_module_identifier import MavenModuleIdentifier, MutableMavenModuleIdentifier
from java.maven.maven_property import MavenProperty, MutableMavenProperty
from utility.type_utility import get_or_else
from utility.xml_node import MutableXmlNode


class MavenModule(ABC):

    @property
    @abstractmethod
    def identifier(self) -> MavenModuleIdentifier:
        raise NotImplemented

    @property
    @abstractmethod
    def parent(self) -> Optional["MavenModule"]:
        raise NotImplemented

    @property
    @abstractmethod
    def children(self) -> List["MavenModule"]:
        raise NotImplemented

    @property
    @abstractmethod
    def properties(self) -> List[MavenProperty]:
        raise NotImplemented

    @abstractmethod
    def find_property(self, property_name: str) -> Optional[MavenProperty]:
        raise NotImplemented


class MutableMavenModule(MavenModule, ABC):

    @property
    @abstractmethod
    def has_been_modified(self):
        raise NotImplemented

    @abstractmethod
    def save(self) -> None:
        raise NotImplemented


class XmlMavenModule(MutableMavenModule):

    def __init__(self,
                 pom_root_node: MutableXmlNode,
                 identifier: MutableMavenModuleIdentifier,
                 parent: Optional["XmlMavenModule"] = None,
                 children: Optional[List["XmlMavenModule"]] = None,
                 properties: Optional[List[MutableMavenProperty]] = None):
        self._pom_root_node: MutableXmlNode = pom_root_node
        self._identifier: MutableMavenModuleIdentifier = identifier
        self._parent: Optional[XmlMavenModule] = parent
        self._children: List[XmlMavenModule] = get_or_else(children, [])
        self._properties: List[MutableMavenProperty] = get_or_else(properties, [])

    @property
    def has_been_modified(self):
        result: bool = False

        result &= self.identifier.has_been_modified
        result &= any(filter(lambda x: x.has_been_modified, self.properties))

        return result

    @property
    def identifier(self) -> MutableMavenModuleIdentifier:
        return self._identifier

    @property
    def parent(self) -> Optional["MavenModule"]:
        return self._parent

    @property
    def children(self) -> List["MavenModule"]:
        return self._children

    @property
    def properties(self) -> List[MavenProperty]:
        return self._properties

    def find_property(self, property_name: str) -> Optional[MavenProperty]:
        for prop in self.properties:
            if prop.name == property_name:
                return prop

        if self.parent is None:
            return None

        return self.parent.find_property(property_name)

    def save(self) -> None:
        if not self.has_been_modified:
            return

        self._pom_root_node.save()