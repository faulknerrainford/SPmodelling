#!/usr/bin/env python
from abc import ABC, abstractmethod
from neo4j import GraphDatabase


class Reset(ABC):
    """
    Reset database to initial settings for new run.
    """

    def __init__(self, reset_tag):
        self.reset_name = reset_tag

    def set_output(self, tx, run_number, pop_size, run_length):
        """
        Set name of run for output files

        :param tx: neo4j write transaction
        :param run_number: run number
        :param pop_size: size of initial population
        :param run_length: number of time steps in run

        :return: None
        """
        import specification
        tag = specification.specname + "_" + self.reset_name + "_" + str(pop_size) + "_" + str(run_length) + "_" + str(
            run_number)
        tx.run("CREATE (a:Tag {tag:$tag})", tag=tag)
        print("set output")

    @staticmethod
    def clear_database(tx):
        """
        Remove all nodes and relationships from database

        :param tx: neo4j write transaction

        :return: NOne
        """
        tx.run("MATCH ()-[r]->() "
               "DELETE r")
        tx.run("MATCH (a) "
               "DELETE a")
        print("clear database")

    @staticmethod
    def set_clock(tx):
        """
        Initialise a clock node to zero

        :param tx: neo4j write transaction

        :return: None
        """
        tx.run("CREATE (a:Clock {time:0})")

    @staticmethod
    @abstractmethod
    def set_nodes(tx):
        """
        Subclass must implement this to set up the initial environment nodes for a run

        :param tx: neo4j write transaction

        :return: None
        """
        pass

    @staticmethod
    @abstractmethod
    def set_edges(tx):
        """
        Subclass must implement this to set up the initial environment edges and relationships for a run

        :param tx: neo4j write transaction

        :return: None
        """
        pass

    @staticmethod
    @abstractmethod
    def generate_population(tx, pop_size):
        """
        Subclass must implement this to set up the initial population of the run

        :param tx: neo4j write transaction
        :param pop_size: number of agents to add to system

        :return: None
        """
        pass


def main(rn, ps, rl):
    """
    Runs the rest class functions to  set up database for a run

    :param rn: Number of run of the model
    :param ps: size of population
    :param rl: number of time steps in each run

    :return: None
    """
    import specification
    print("running rest")
    dri = GraphDatabase.driver(specification.database_uri, auth=specification.Reset_auth, max_connection_lifetime=2000)
    print("In code")
    with dri.session() as ses:
        reset = specification.Reset.Reset()
        ses.write_transaction(reset.clear_database)
        ses.write_transaction(reset.set_output, rn, ps, rl)
        ses.write_transaction(reset.set_clock)
        ses.write_transaction(reset.set_nodes)
        ses.write_transaction(reset.set_edges)
        ses.write_transaction(reset.set_service)
        ses.write_transaction(reset.generate_population, ps)
    dri.close()
