from neo4j import GraphDatabase
from matplotlib.pylab import *
from abc import ABC, abstractmethod
import specification
import SPmodelling.Interface as intf


class Monitor(ABC):
    """
    Class implements a viewer for the system which outputs a grid of graphs during run time and saves out graphs and
    data collected at end of run
    """

    @abstractmethod
    def __init__(self, show_local=True):
        """
        Sets up clock, records and basic graph. Subclass must implement function to set up graphs and other data needed

        :param show_local: display graph during run
        """
        self.clock = 0
        self.records = {}
        self.orecord = None
        self.nrecord = None
        self.show = show_local
        # Set up plot
        self.fig = figure()
        self.t = zeros(0)
        self.x = 0

    @abstractmethod
    def snapshot(self, txl, ctime):
        """
        Captures data from a single time step in database. Subclass must implement to capture wanted data.

        :param txl: neo4j read or write transaction
        :param ctime: current time

        :return: True if snapshot is successful.
        """
        if self.x != ctime:
            # Update time
            print(ctime)
            self.records[self.clock] = self.orecord
            self.orecord = self.nrecord
            self.clock = self.clock + 1
            self.t = append(self.t, ctime)
            self.x = ctime
            return True
        return False

    @abstractmethod
    def monitor_close(self, txl):
        """
        subclass must implement to save out data and graphs for analysis

        :param txl: neo4j read or write transaction

        :return: None
        """
        pass


def main(rl):
    """
    Runs the monitor snapshot until clock reaches or exceeds run length. Then closes monitor.

    :param rl: run length

    :return: None
    """
    monitor = specification.Monitor()
    clock = 0
    while clock < rl:
        driver = GraphDatabase.driver(specification.database_uri, auth=specification.Monitor_auth,
                                      max_connection_lifetime=20000)
        with driver.session() as session:
            # modifying and redrawing plot over time and saving plot rather than an animation
            session.write_transaction(monitor.snapshot, clock)
            tx = session.begin_transaction()
            current_time = intf.gettime(tx)
            while clock == current_time:
                current_time = intf.gettime(tx)
            clock = current_time
        driver.close()
    print("Monitor Capture complete")
    driver = GraphDatabase.driver(specification.database_uri, auth=specification.Monitor_auth,
                                  max_connection_lifetime=2000)
    with driver.session() as session:
        session.write_transaction(monitor.monitor_close)
    driver.close()
    print("Monitor closed")
