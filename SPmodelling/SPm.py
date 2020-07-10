# import SPmodelling
import concurrent.futures
print("finished spm imports")


def main(runs, length, population, modules=None):
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
        SPmodelling.Reset.main(i, population, length)
        print("Finished Reset")
        if modules:
            executor = concurrent.futures.ThreadPoolExecutor(max_workers=2)
            if "Monitor" in modules:
                executor.submit(SPmodelling.Monitor.main, length)
            if "Population" in modules:
                executor.submit(SPmodelling.Population.main, length, population)
            if "Structure" in modules:
                executor.submit(SPmodelling.Structure.main, length)
            if "Balancer" in modules:
                executor.submit(SPmodelling.Balancer.main, length)
            if "Flow" in modules:
                print("Executing Flow")
                # SPmodelling.Flow.main(length, i)
                executor.submit(SPmodelling.Flow.main, length, i)
            if "Social" in modules:
                print("Executing Social")
                # SPmodelling.Social.main(length, i)
                executor.submit(SPmodelling.Social.main, length)
            executor.shutdown()
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
