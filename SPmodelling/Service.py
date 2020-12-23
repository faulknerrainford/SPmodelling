from abc import ABC, abstractmethod


class Service(ABC):

    @abstractmethod
    def __init__(self, name, service_type, capacity=None):
        self.name = name
        self.service_type = service_type
        self.capacity = capacity

    @abstractmethod
    def provide_service(self, dri, agent):
        pass
