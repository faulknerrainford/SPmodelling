from neo4j import GraphDatabase
import specification
import SPmodelling.Interface as intf


def main(rl, rn):
    """
    Process agents at each node and call the move function for each. Ticks the clock after all agents have been
    processed. Stops when clock reaches or exceeds run length.

    :param rl: run length
    :param rn: run number

    :return: None
    """
    print("In to flow")
    uri = specification.database_uri
    dri = GraphDatabase.driver(uri, auth=specification.Flow_auth,
                               max_connection_lifetime=36000)
    clock = 0
    while clock < rl:
        for node in specification.nodes:
            node.agents_ready(dri)
        intf.tick(dri)
        clock = intf.get_time(dri)
        print("post Tick: " + clock.__str__())
    dri.close()
    print("Flow closed")
