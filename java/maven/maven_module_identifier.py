from abc import ABC, abstractmethod


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

    @abstractmethod
    def set_version(self, version: str) -> None:
        raise NotImplemented
