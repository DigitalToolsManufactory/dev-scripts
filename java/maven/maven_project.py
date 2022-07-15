from abc import ABC, abstractmethod
from typing import List

from java.maven.maven_module import MavenModule


class MavenProject(ABC):

    @property
    @abstractmethod
    def has_been_modified(self) -> bool:
        raise NotImplemented

    @property
    @abstractmethod
    def modules(self) -> List[MavenModule]:
        raise NotImplemented

    @abstractmethod
    def save(self) -> None:
        raise NotImplemented
