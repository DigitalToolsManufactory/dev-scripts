from abc import ABC, abstractmethod
from pathlib import Path
from typing import List

from java.maven.maven_module import MavenModule


class MavenModuleReader(ABC):
    @abstractmethod
    def read(self, pom: Path) -> MavenModule:
        raise NotImplementedError

    @abstractmethod
    def read_recursive(self, pom: Path) -> List[MavenModule]:
        raise NotImplementedError
