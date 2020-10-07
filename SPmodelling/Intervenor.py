from abc import ABC, abstractmethod


class Intervenor(ABC):

    def __init__(self):
        pass

    @abstractmethod
    def check(self, tx):
        pass

    @abstractmethod
    def apply_change(self, tx):
        pass
