from abc import ABC, abstractmethod


class MavenProperty(ABC):

    @property
    @abstractmethod
    def name(self) -> str:
        raise NotImplemented

    @property
    @abstractmethod
    def value(self) -> str:
        raise NotImplemented

    @abstractmethod
    def set_value(self, value: str) -> None:
        raise NotImplemented
