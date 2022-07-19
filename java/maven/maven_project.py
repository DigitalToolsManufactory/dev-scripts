from abc import ABC, abstractmethod
from typing import List

from java.maven.maven_module import MavenModule


class MavenProject(ABC):

    @property
    def modules(self) -> List[MavenModule]:
        return self._get_modules()

    @abstractmethod
    def _get_modules(self) -> List[MavenModule]:
        raise NotImplementedError

    @abstractmethod
    def add_module(self, module: MavenModule) -> None:
        raise NotImplementedError
