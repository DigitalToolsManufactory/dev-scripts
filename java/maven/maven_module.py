from abc import ABC, abstractmethod
from typing import List, Optional

from java.maven.maven_module_identifier import MavenModuleIdentifier
from java.maven.maven_property import MavenProperty


class MavenModule(ABC):

    @property
    def identifier(self) -> MavenModuleIdentifier:
        return self._get_identifier()

    @abstractmethod
    def _get_identifier(self) -> MavenModuleIdentifier:
        raise NotImplementedError

    @property
    def parent_identifier(self) -> Optional[MavenModuleIdentifier]:
        return self._get_parent_identifier()

    @abstractmethod
    def _get_parent_identifier(self) -> Optional[MavenModuleIdentifier]:
        raise NotImplementedError

    @property
    def properties(self) -> List[MavenProperty]:
        return self._get_properties()

    @abstractmethod
    def _get_properties(self) -> List[MavenProperty]:
        raise NotImplementedError

    @property
    def dependencies(self) -> List[MavenModuleIdentifier]:
        return self._get_dependencies()

    @abstractmethod
    def _get_dependencies(self) -> List[MavenModuleIdentifier]:
        raise NotImplementedError

    def __str__(self) -> str:
        return str(self.identifier)
