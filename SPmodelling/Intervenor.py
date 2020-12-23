from abc import ABC, abstractmethod
from neo4j import GraphDatabase
import SPmodelling.Interface as intf


class Intervenor(ABC):

    def __init__(self, name):
        self.name = name
        pass

    @abstractmethod
    def check(self, dri):
        pass

    @abstractmethod
    def apply_change(self, dri):
        pass

    def main(self):
        """
        default intervenor run set up for subclasses to use.

        :param dri:
        :param length:
        :return:
        """
        import specification
        clock = 0
        dri = GraphDatabase.driver(specification.database_uri, auth=specification.Inter_auth,
                                   max_connection_lifetime=36000)
        length = intf.get_run_length(dri)
        while clock < length:
            self.check(dri)
            self.apply_change(dri)
            time = intf.get_time(dri)
            while clock == time:
                time = intf.get_time(dri)
            clock = time
        dri.close()
        print(self.name + " closed")
