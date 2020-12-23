from neo4j import GraphDatabase
import specification
from abc import abstractmethod, ABC
# import SPmodelling.Interface as intf


class Structure(ABC):
    """
    Implements structural changes in model
    """

    @abstractmethod
    def __init__(self):
        pass

    @abstractmethod
    def applychange(self, dri):
        """
        This function must be implemented by the subclass to check for events and apply structural changes to the system
        environment.

        :param dri: neo4j driver

        :return: None
        """
        pass


def main(rl):
    """
    Runs to apply structural change to the system checks continue until clock reaches or exceeds run length

    :param rl: run length

    :return: None
    """
    clock = 0
    while clock < rl:
        dri = GraphDatabase.driver(specification.database_uri, auth=specification.Structure_auth,
                                   max_connection_lifetime=2000)
        specification.Structure.applychange(dri)
        time = intf.gettime(dri)
        while clock == time:
            time = intf.gettime(dri)
        clock = time
        print(clock)
        dri.close()
