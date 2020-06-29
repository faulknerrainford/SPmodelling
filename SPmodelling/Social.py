from neo4j import GraphDatabase
from SPmodelling.Interface import Interface
import specification


def main(rl, rn):
    verbose = False
    uri = specification.database_uri
    dri = GraphDatabase.driver(uri, auth=specification.Flow_auth, max_connection_lifetime=2000)
    intf = Interface()
    with dri.session() as ses:
        clock = 0
        while clock < rl:
            tx = ses.begin_transaction()
            agents = tx.run("MATCH (a:Agent) "
                            "RETURN a.id").values()
            for agent in agents:
                ag = specification.Agent(agent)
                ag.socialise(tx, intf)
            clock = intf.gettime(tx)
            print("T: " + clock.__str__())
            tx.close()
    dri.close()
    print("Social closed")
