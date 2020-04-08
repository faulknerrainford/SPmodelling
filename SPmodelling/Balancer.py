from neo4j import GraphDatabase
from abc import ABC, abstractmethod
import specification
from SPmodelling.Interface import Interface


class FlowReaction(ABC):

    @abstractmethod
    def __init__(self):
        pass

    @abstractmethod
    def applyrules(self, txl, intf):
        pass


def main(rl):
    flowreaction = specification.Balancer.FlowReaction()
    clock = 0
    interface = Interface()
    while clock < rl:
        dri = GraphDatabase.driver(specification.database_uri, auth=specification.Balancer_auth,
                                   max_connection_lifetime=2000)
        with dri.session() as ses:
            ses.write_transaction(flowreaction.applyrules, interface)
            tx = ses.begin_transaction()
            time = interface.gettime(tx)
            while clock == time:
                time = interface.gettime(tx)
            clock = time
        dri.close()
    print("Balancer closed")
