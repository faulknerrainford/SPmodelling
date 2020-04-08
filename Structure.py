from neo4j import GraphDatabase
import specification
from abc import abstractmethod, ABC
import SPmodelling.Interface as Interface
import sys


class Structure(ABC):

    @abstractmethod
    def __init__(self):
        pass

    @abstractmethod
    def applychange(self, txl):
        pass


def main(rl):
    clock = 0
    while clock < rl:
        uri = "bolt://localhost:7687"
        dri = GraphDatabase.driver(specification.database_uri, auth=specification.Structure_auth,
                                   max_connection_lifetime=2000)
        interface = Interface.Interface()
        with dri.session() as ses:
            ses.write_transaction(specification.Structure.applychange)
            tx = ses.begin_transaction()
            time = interface.gettime(tx)
            while clock == time:
                time = interface.gettime(tx)
            clock = time
        print(clock)
        dri.close()
