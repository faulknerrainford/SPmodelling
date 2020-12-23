import SPmodelling
# import concurrent.futures
from multiprocessing import Process, Queue
import specification
print("finished spm imports")


# noinspection PyRedundantParentheses
def main(runs, length, population, coremodules=None, additionalmodules=None, reset=True):
    """
    This function takes the number of runs required, the time-step length of each run and the size of population and
    runs a SPmodel based on the local specification file. It saves all output to a run name as defined by the parameters
    given and the specification. This uses concurrent.futures to run the Monitor, Population, Structure, Balancer and
    Flow concurrently.

    :param runs: Number of models runs required
    :param length: Time-step length of each run
    :param population: Size of initial and maintained population for each run
    :param modules: List of modules to be used in this modelling batch eg. ['Monitor', 'Flow', 'Population', 'Balancer',
                    'Structure', 'Social']
    :param reset: Boolean dictates if the database is reset between runs

    :return: None
    """
    for i in range(runs):
        if reset:
            SPmodelling.Reset.main(i, population, length)
            print("Finished Reset")
        q = Queue()
        current_processes = []
        if coremodules:
            if "Population" in coremodules:
                print("Executing Population")
                inter1 = Process(target=SPmodelling.Population.main, args=(length, population))
                inter1.start()
                current_processes.append(inter1)
            if "Structure" in coremodules:
                inter2 = Process(target=SPmodelling.Structure.main, args=tuple([length]))
                inter2.start()
                current_processes.append(inter2)
            if "Balancer" in coremodules:
                print("Execution Balancer")
                inter3 = Process(target=SPmodelling.Balancer.main, args=tuple([length]))
                inter3.start()
                current_processes.append(inter3)
            if "Cluster" in coremodules:
                print("Executing Cluster")
                inter4 = Process(target=SPmodelling.Cluster.main, args=tuple([length]))
                inter4.start()
                current_processes.append(inter4)
            if "Opinion" in coremodules:
                print("Executing Opinion")
                inter5 = Process(target=specification.Opinion.main, args=tuple([length]))
                inter5.start()
                current_processes.append(inter5)
            if "Flow" in coremodules:
                print("Executing Flow")
                agent1 = Process(target=SPmodelling.Flow.main, args=(length, i))
                agent1.start()
                current_processes.append(agent1)
            if "Social" in coremodules:
                print("Executing Social")
                social1 = Process(target=SPmodelling.Social.main, args=(length, i))
                social1.start()
                current_processes.append(social1)
            if "Monitor" in coremodules:
                monitor = Process(target=SPmodelling.Monitor.main, args=tuple([length]))
                monitor.start()
                current_processes.append(monitor)
        if additionalmodules:
            for module in additionalmodules:
                new_process = Process(target=module.main)
                new_process.start()
                current_processes.append(new_process)
        [pro.join() for pro in current_processes]

    print("Main thread exit")


# if __name__ == '__main__':
#     if len(sys.argv) > 1:
#         nr = sys.argv[1]
#         rl = sys.argv[2]
#         ps = sys.argv[3]
#         md = sys.argv[4]
#     else:
#         nr = 1
#         rl = 10
#         ps = 200
#         md = ['Monitor', 'Flow', 'Population', 'Social', 'Balancer', 'Structure']
#     main(nr, rl, ps, md)
