from neo4j import GraphDatabase
import specification
from abc import abstractmethod, ABC
import SPmodelling.Interface as intf


class Structure(ABC):
    """
    Implements structural changes in model
    """

    @abstractmethod
    def __init__(self):
        pass

    @abstractmethod
    def applychange(self, txl):
        """
        This function must be implemented by the subclass to check for events and apply structural changes to the system
        environment.

        :param txl: neo4j write transaction

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
        with dri.session() as ses:
            ses.write_transaction(specification.Structure.applychange)
            tx = ses.begin_transaction()
            time = intf.gettime(tx)
            while clock == time:
                time = intf.gettime(tx)
            clock = time
        print(clock)
        dri.close()
