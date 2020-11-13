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
    verbose = False
    uri = specification.database_uri
    dri = GraphDatabase.driver(uri, auth=specification.Flow_auth, max_connection_lifetime=2000)
    nuid = "name"
    runtype = "dynamic"
    runnum = rn
    runname = "careag_" + runtype + "_" + str(runnum)
    with dri.session() as ses:
        clock = 0
        while clock < rl:
            for node in specification.nodes:
                ses.write_transaction(node.agents_ready)
            ses.write_transaction(intf.tick)
            clock = ses.write_transaction(intf.get_time)
            print("post Tick: " + clock.__str__())
        # ses.write_transaction(activeagentsave, nodes[1:], intf, runname)
    dri.close()
    print("Flow closed")
