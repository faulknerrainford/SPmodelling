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
    def check(self, dri, params=None):
        """
        Method for checking if changes need to be made to the system

        :param dri: neo4j database driver
        :param params: any further parameters the intervenor might need

        :return: None
        """
        pass

    @abstractmethod
    def apply_change(self, dri, params=None):
        """
        Method for applying changes to system

        :param dri: neo4j driver
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
