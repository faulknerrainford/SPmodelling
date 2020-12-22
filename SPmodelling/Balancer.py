from neo4j import GraphDatabase
from abc import ABC, abstractmethod
# import specification
import SPmodelling.Interface as intf
import SPmodelling.Intervenor


class Balancer(SPmodelling.Intervenor.Intervenor):
    """
    Class to implement modifications to edges and nodes with out changing the structure of the network. This should be
    based on the movement and behaviours of the agent population or on events in the system.
    """

    @abstractmethod
    def __init__(self):
        """
        The subclass must implement this function. No intial set up is implemented here.
        """
        super(Balancer, self).__init__(self)

    def check(self, tx, params=None):
        """
        Check if rule application is needed. If it is to be used it must be implemented in the subclass

        :param tx: neo4j database read or write transaction
        :param params: Any additional parameters needed by balancer

        :return: True if rule application is needed False otherwise
        """
        pass

    @abstractmethod
    def apply_change(self, txl, params=None):
        """
        The subclass must implement this function to apply a change rule to the system. This rule will be applied
        iteratively and may need a check and wait system to avoid over application depending on the intended use of the
        rule.

        :param txl: write transaction for neo4j database
        :param params: Any additional parameters needed by balancer

        :return: None
        """
        pass


def main(rl):
    """
    Implements a FlowReaction repeatedly until the clock in the database reaches the run length.

    :param rl: run length

    :return: None
    """
    bal = specification.Balancer()
    clock = 0
    while clock < rl:
        dri = GraphDatabase.driver(specification.database_uri, auth=specification.Balancer_auth,
                                   max_connection_lifetime=2000)
        with dri.session() as ses:
            ses.write_transaction(bal.apply_change)
            tx = ses.begin_transaction()
            time = intf.gettime(tx)
            while clock == time:
                time = intf.gettime(tx)
            clock = time
        dri.close()
    print("Balancer closed")
