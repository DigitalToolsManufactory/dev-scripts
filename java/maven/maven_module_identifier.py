from abc import ABC, abstractmethod

from utility.type_utility import get_or_raise
from utility.xml_node import XmlNode, MutableXmlNode


class MavenModuleIdentifier(ABC):

    @property
    @abstractmethod
    def group_id(self) -> str:
        raise NotImplemented

    @property
    @abstractmethod
    def artifact_id(self) -> str:
        raise NotImplemented

    @property
    @abstractmethod
    def version(self) -> str:
        raise NotImplemented

    def __repr__(self) -> str:
        return self.__str__()

    def __str__(self) -> str:
        return f"{self.group_id}:{self.artifact_id}:{self.version}"


class MutableMavenModuleIdentifier(MavenModuleIdentifier, ABC):

    @property
    @abstractmethod
    def has_been_modified(self) -> bool:
        raise NotImplemented

    @MavenModuleIdentifier.version.setter
    @abstractmethod
    def version(self, version: str) -> None:
        raise NotImplemented

    @abstractmethod
    def save(self) -> None:
        raise NotImplemented


class XmlMavenModuleIdentifier(MutableMavenModuleIdentifier):

    def __init__(self, group_id_node: XmlNode, artifact_id_node: XmlNode, version_node: MutableXmlNode):
        self._group_id_node: XmlNode = group_id_node
        self._artifact_id_node: XmlNode = artifact_id_node
        self._version_node: MutableXmlNode = version_node

    @property
    def has_been_modified(self) -> bool:
        return self._version_node.has_been_modified

    @property
    def group_id(self) -> str:
        return get_or_raise(self._group_id_node.value, lambda: AssertionError("Maven Group Id must be defined"))

    @property
    def artifact_id(self) -> str:
        return get_or_raise(self._artifact_id_node.value, lambda: AssertionError("Maven Artifact Id must be defined"))

    @MavenModuleIdentifier.version.getter
    def version(self) -> str:
        return get_or_raise(self._version_node.value(), lambda: AssertionError("Maven Version must be defined"))

    @MutableMavenModuleIdentifier.version.setter
    def version(self, version: str) -> None:
        self._version_node.value = version

    def save(self) -> None:
        self._version_node.save()
