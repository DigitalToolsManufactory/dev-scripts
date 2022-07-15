from abc import ABC, abstractmethod
from typing import List, Optional

from java.maven.maven_module_identifier import MavenModuleIdentifier
from java.maven.maven_property import MavenProperty


class MavenModule(ABC):

    @property
    @abstractmethod
    def parent(self) -> Optional["MavenModule"]:
        raise NotImplemented

    @property
    @abstractmethod
    def parent_identifier(self) -> Optional[MavenModuleIdentifier]:
        raise NotImplemented

    @property
    @abstractmethod
    def identifier(self) -> MavenModuleIdentifier:
        raise NotImplemented

    @property
    @abstractmethod
    def properties(self) -> List[MavenProperty]:
        raise NotImplemented

    @property
    @abstractmethod
    def dependencies(self) -> List[MavenModuleIdentifier]:
        raise NotImplemented

    @property
    @abstractmethod
    def modules(self) -> List["MavenModule"]:
        raise NotImplemented

    def try_find_property(self, name: str) -> Optional[MavenProperty]:
        for p in self.properties:
            if p.name == name:
                return p

        if self.parent is None:
            return None

        return self.parent.try_find_property(name)
