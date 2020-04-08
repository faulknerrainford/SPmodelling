from neo4j import GraphDatabase
from matplotlib.pylab import *
from abc import ABC, abstractmethod
import specification
import Interface


class Monitor(ABC):

    @abstractmethod
    def __init__(self, show_local=True):
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
    def close(self, txl):
        pass


def main(rl):
    monitor = specification.Monitor.Monitor()
    clock = 0
    interface = Interface.Interface()
    while clock < rl:
        driver = GraphDatabase.driver(specification.database_uri, auth=specification.Monitor_auth,
                                      max_connection_lifetime=20000)
        with driver.session() as session:
            # modifying and redrawing plot over time and saving plot rather than an animation
            session.write_transaction(monitor.snapshot, clock)
            tx = session.begin_transaction()
            current_time = interface.gettime(tx)
            while clock == current_time:
                current_time = interface.gettime(tx)
            clock = current_time
        driver.close()
    print("Monitor Capture complete")
    driver = GraphDatabase.driver(specification.database_uri, auth=specification.Monitor_auth,
                                  max_connection_lifetime=2000)
    with driver.session() as session:
        session.write_transaction(monitor.close)
    driver.close()
    print("Monitor closed")
