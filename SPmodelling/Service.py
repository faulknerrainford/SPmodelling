from abc import ABC, abstractmethod


class Provision(ABC):
    """
    Class for an object that represents the ability to provide a service which can be enabled by another player
    """

    @abstractmethod
    def __init__(self, name, service_type, capacity=None):
        """
        All Provisions are started with a name, service_type and capacity

        :param name: Unique id for provision in system
        :param service_type: Defines the type of provision eg. physio or food or shopping
        :param capacity: Number of times a provision can be used either in total or until a reset
        """
        self.name = name
        self.service_type = service_type
        self.capacity = capacity

    @abstractmethod
    def provide_service(self, dri, player):
        """
        Specific behaviour to modify player given.

        :param dri: neo4j database driver
        :param player: node, agent or other player using provision

        :return: None
        """
        pass
