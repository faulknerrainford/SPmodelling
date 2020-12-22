from abc import ABC, abstractmethod
from neo4j import GraphDatabase
import SPmodelling.Interface as intf


class Intervenor(ABC):

    def __init__(self, name):
        """
        Assign name of intervenor to help track activity and report when its finished

        :param name: name of intervenor used for print statements to track activity of different intervenors
        """
        self.name = name
        pass

    @abstractmethod
    def check(self, tx, params=None):
        """
        Method for checking if changes need to be made to the system

        :param tx: neo4j database read or write transaction
        :param params: any further parameters the intervenor might need

        :return: None
        """
        pass

    @abstractmethod
    def apply_change(self, tx, params=None):
        """
        Method for applying changes to system

        :param tx: neo4j write transaction
        :param params: any further parameters the intervenor might need

        :return: None
        """
        pass

    def main(self):
        """
        default intervenor run set up for subclasses to use.

        :return:None
        """
        import specification
        clock = 0
        dri = GraphDatabase.driver(specification.database_uri, auth=specification.Inter_auth,
                                   max_connection_lifetime=2000)
        with dri.session() as ses:
            length = ses.read_transaction(intf.get_run_length)
            while clock < length:
                ses.write_transaction(self.check)
                ses.write_transaction(self.apply_change)
                tx = ses.begin_transaction()
                time = intf.get_time(tx)
                while clock == time:
                    time = intf.get_time(tx)
                clock = time
        dri.close()
        print(self.name + " closed")
