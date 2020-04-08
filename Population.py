from neo4j import GraphDatabase
from SPmodelling.Interface import Interface
import specification as specification


def main(rl, ps):
    uri = "bolt://localhost:7687"
    interface = Interface()
    clock = 0
    agent = specification.Agents.Agent(None)
    while clock < rl:
        dri = GraphDatabase.driver(specification.database_uri, auth=specification.Population_auth,
                                   max_connection_lifetime=2000)
        with dri.session() as ses:
            populationdeficite = specification.Population.check(ses, ps)
            if populationdeficite:
                for i in range(populationdeficite):
                    ses.write_transaction(agent.generator, interface, specification.Population.params)
            tx = ses.begin_transaction()
            time = interface.gettime(tx)
            while clock == time:
                time = interface.gettime(tx)
            clock = time
        dri.close()
    print("Population closed")
