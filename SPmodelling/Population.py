from neo4j import GraphDatabase
import SPmodelling.Interface as intf
import specification as specification


def main(rl, ps):
    """
    Checks population levels meet requirements and adds additional agents if needed until clock reaches or exceeds run
    length

    :param rl: run length
    :param ps: population size

    :return: None
    """
    clock = 0
    agent = specification.Agents(None)
    while clock < rl:
        dri = GraphDatabase.driver(specification.database_uri, auth=specification.Population_auth,
                                   max_connection_lifetime=2000)
        with dri.session() as ses:
            populationdeficite = specification.Population.check(ses, ps)
            if populationdeficite:
                for i in range(populationdeficite):
                    ses.write_transaction(agent.generator, specification.Population.params)
            tx = ses.begin_transaction()
            time = intf.gettime(tx)
            while clock == time:
                time = intf.gettime(tx)
            clock = time
        dri.close()
    print("Population closed")
