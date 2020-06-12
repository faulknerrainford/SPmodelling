from SPmodelling import Monitor, Reset, Balancer, Flow, Population, Structure, Social
import concurrent.futures
import sys


def main(runs, length, population, modules):
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

    :return: None
    """
    for i in range(runs):
        Reset.main(i, population, length)
        print("Finished Reset")
        with concurrent.futures.ProcessPoolExecutor(max_workers=len(modules)) as executor:
            if "Monitor" in modules:
                executor.submit(Monitor.main, length)
            if "Population" in modules:
                executor.submit(Population.main, length, population)
            if "Structure" in modules:
                executor.submit(Structure.main, length)
            if "Balancer" in modules:
                executor.submit(Balancer.main, length)
            if "Flow" in modules:
                executor.submit(Flow.main, length, i)
            if "Social" in modules:
                executor.submit(Social.main, length)
    print("Main thread exit")


if __name__ == '__main__':
    if len(sys.argv) > 1:
        nr = sys.argv[1]
        rl = sys.argv[2]
        ps = sys.argv[3]
        md = sys.argv[4]
    else:
        nr = 1
        rl = 10
        ps = 200
        md = ['Monitor', 'Flow', 'Population', 'Social', 'Balancer', 'Structure']
    main(nr, rl, ps, md)
