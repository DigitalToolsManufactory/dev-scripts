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

    @value.setter
    def value(self, value: str) -> None:
        self._set_value(value)

    @abstractmethod
    def _set_value(self, value: str) -> None:
        raise NotImplemented
