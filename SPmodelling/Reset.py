#!/usr/bin/env python
from abc import ABC, abstractmethod
from neo4j import GraphDatabase


class Reset(ABC):
    """
    Reset database to initial settings for new run.
    """

    def __init__(self, reset_tag):
        """
        Set up reset run

        :param reset_tag: label for the reset script defining the starting conditions of the model, used as part of the
                          run tag
        """
        self.reset_name = reset_tag      

    def set_output(self, dri, run_number, pop_size, run_length):
        """
        Set name of run for output files

        :param dri: neo4j database driver
        :param run_number: run number
        :param pop_size: size of initial population
        :param run_length: number of time steps in run

        :return: None
        """
        import specification
        tag = specification.specname + "_" + self.reset_name + "_" + str(pop_size) + "_" + str(run_length) + "_" + str(
            run_number)
        ses = dri.session()
        ses.run("CREATE (a:Tag {tag:$tag})", tag=tag)
        ses.close()
        print("set output")

    @staticmethod
    def clear_database(dri):
        """
        Remove all nodes and relationships from database

        :param dri: neo4j driver

        :return: NOne
        """
        ses = dri.session()
        ses.run("MATCH ()-[r]->() "
               "DELETE r")
        ses.run("MATCH (a) "
               "DELETE a")
        ses.close()
        print("clear database")

    @staticmethod
    def set_clock(dri):
        """
        Initialise a clock node to zero

        :param dri: neo4j driver

        :return: None
        """
        ses = dri.session()
        ses.run("CREATE (a:Clock {time:0})")
        ses.close()

    @staticmethod
    @abstractmethod
    def set_nodes(dri):
        """
        Subclass must implement this to set up the initial environment nodes for a run

        :param dri: neo4j driver

        :return: None
        """
        pass

    @staticmethod
    @abstractmethod
    def set_edges(dri):
        """
        Subclass must implement this to set up the initial environment edges and relationships for a run

        :param dri: neo4j driver

        :return: None
        """
        pass

    @staticmethod
    @abstractmethod
    def generate_population(dri, pop_size):
        """
        Subclass must implement this to set up the initial population of the run

        :param dri: neo4j driver
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
    reset = specification.Reset.Reset()
    reset.clear_database(dri)
    reset.set_output(dri, rn, ps, rl)
    reset.set_clock(dri)
    reset.set_nodes(dri)
    reset.set_edges(dri)
    reset.set_service(dri)
    reset.generate_population(dri, ps)
    dri.close()
