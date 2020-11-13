from neo4j import GraphDatabase
import SPmodelling.Interface as intf
import SPmodelling.Intervenor
import specification as specification
from abc import ABC, abstractmethod


class Population(SPmodelling.Intervenor.Intervenor):

    def __init__(self):
        super(Population, self).__init__("Population")
        return None

    @abstractmethod
    def check(self, tx, ps):
        super(Population, self).check()
        return None

    @abstractmethod
    def apply_change(self, tx, population_deficit):
        super(Population, self).apply_change(self, tx, population_deficit)
        return None


def main(rl, ps):
    """
    Checks population levels meet requirements and adds additional agents if needed until clock reaches or exceeds run
    length, uses check and replace functions from specification.Population

    :param rl: run length
    :param ps: population size

    :return: None
    """
    clock = 0
    while clock < rl:
        dri = GraphDatabase.driver(specification.database_uri, auth=specification.Population_auth,
                                   max_connection_lifetime=2000)
        pop = specification.Population()
        with dri.session() as ses:
            population_deficit = ses.read_transaction(pop.check, ps)
            if population_deficit:
                ses.write_transaction(pop.apply_change, population_deficit)
            tx = ses.begin_transaction()
            time = intf.get_time(tx)
            while clock == time:
                time = intf.get_time(tx)
            clock = time
        dri.close()
    print("Population closed")
