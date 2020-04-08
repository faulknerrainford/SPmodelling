import Reset
import Monitor
import Population
# import Structure
import Balancer
import Flow
import concurrent.futures
import sys


def main(runs, length, population):
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
