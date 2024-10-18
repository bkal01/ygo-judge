from abc import ABC, abstractmethod

class Completer(ABC):
    @abstractmethod
    def attach_context(self, query: str) -> str:
        pass

    @abstractmethod
    def complete(self, query: str) -> str:
        pass