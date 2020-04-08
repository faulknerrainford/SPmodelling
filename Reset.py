#!/usr/bin/env python
from abc import ABC, abstractmethod
from neo4j import GraphDatabase
import specification


class Reset(ABC):

    def __init__(self, reset_tag):
        self.reset_name = reset_tag

    def set_output(self, tx, run_number, pop_size, run_length):
        print(type(specification.specname))
        tag = specification.specname + "_" + self.reset_name + "_" + str(pop_size) + "_" + str(run_length) + "_" + str(
            run_number)
        tx.run("CREATE (a:Tag {tag:{tag}})", tag=tag)
        print("set output")

    @staticmethod
    def clear_database(tx):
        tx.run("MATCH ()-[r]->() "
               "DELETE r")
        tx.run("MATCH (a) "
               "DELETE a")
        print("clear database")

    @staticmethod
    def set_clock(tx):
        tx.run("CREATE (a:Clock {time:0})")

    @staticmethod
    @abstractmethod
    def set_nodes(tx):
        pass

    @staticmethod
    @abstractmethod
    def set_edges(tx):
        pass

    @staticmethod
    @abstractmethod
    def generate_population(tx, pop_size):
        pass


def main(rn, ps, rl):
    uri = "bolt://localhost:7687"
    dri = GraphDatabase.driver(specification.database_uri, auth=specification.Reset_auth, max_connection_lifetime=2000)
    print("In code")
    with dri.session() as ses:
        reset = specification.Reset.Reset()
        ses.write_transaction(reset.clear_database)
        ses.write_transaction(reset.set_output, rn, ps, rl)
        ses.write_transaction(reset.set_clock)
        ses.write_transaction(reset.set_nodes)
        ses.write_transaction(reset.set_edges)
        ses.write_transaction(reset.generate_population, ps)
    dri.close()
