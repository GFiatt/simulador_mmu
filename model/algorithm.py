from abc import ABC, abstractmethod

class Algorithm(ABC):
    @abstractmethod
    def replace(self, pages: list):
        pass
