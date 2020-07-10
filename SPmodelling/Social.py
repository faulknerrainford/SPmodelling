from neo4j import GraphDatabase
import SPmodelling.Interface as intf
import specification


def main(rl, rn):
    """
    Calls the socialise function for each agent in system until clock reaches or exceeds run length

    :param rl: run length
    :param rn: run number

    :return: None
    """
    verbose = False
    uri = specification.database_uri
    dri = GraphDatabase.driver(uri, auth=specification.Flow_auth, max_connection_lifetime=2000)
    with dri.session() as ses:
        clock = 0
        while clock < rl:
            tx = ses.begin_transaction()
            agents = tx.run("MATCH (a:Agent) "
                            "RETURN a.id").values()
            for agent in agents:
                ag = specification.Agent(agent)
                ag.socialise(tx)
            clock = intf.gettime(tx)
            print("T: " + clock.__str__())
            tx.close()
    dri.close()
    print("Social closed")
