from abc import ABC, abstractmethod
from neo4j import GraphDatabase
import SPmodelling.Interface as intf


class Intervenor(ABC):

    def __init__(self, name):
        self.name = name
        pass

    @abstractmethod
    def check(self, tx):
        pass

    @abstractmethod
    def apply_change(self, tx):
        pass

    def main(self):
        """
        default intervenor run set up for subclasses to use.

        :param tx:
        :param length:
        :return:
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