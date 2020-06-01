from SPmodelling import Monitor, Reset, Balancer, Flow, Population
# import Structure
import concurrent.futures
import sys
# TODO: Add flags for the modules to be run. eg ['F','B','P','S','I','M'] for flow, balance, population, structure and
#  infomation default would be ['F','M'] which gives a very basic system with a monitor.

def main(runs, length, population):
    """
    This function takes the number of runs required, the time-step length of each run and the size of population and
    runs a SPmodel based on the local specification file. It saves all output to a run name as defined by the parameters
    given and the specification. This uses concurrent.futures to run the Monitor, Population, Structure, Balancer and
    Flow concurrently.

    :param runs: Number of models runs required
    :param length: Time-step length of each run
    :param population: Size of initial and maintained population for each run

    :return: None
    """
    # TODO: Add flags to turn structure and balancer on and off in the system
    for i in range(runs):
        Reset.main(i, population, length)
        print("Finished Reset")
        with concurrent.futures.ProcessPoolExecutor(max_workers=4) as executor:
            executor.submit(Monitor.main, length)
            executor.submit(Population.main, length, population)
            # executor.submit(Structure.main, rl)
            executor.submit(Balancer.main, length)
            executor.submit(Flow.main, length, i)
    print("Main thread exit")


if __name__ == '__main__':
    if len(sys.argv) > 1:
        nr = sys.argv[1]
        rl = sys.argv[2]
        ps = sys.argv[3]
    else:
        nr = 1
        rl = 10
        ps = 200
    main(nr, rl, ps)
