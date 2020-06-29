from neo4j import GraphDatabase
from SPmodelling.Interface import Interface
import specification

def main(rl, rn):
    print("In to flow")
    verbose = False
    uri = specification.database_uri
    dri = GraphDatabase.driver(uri, auth=specification.Flow_auth, max_connection_lifetime=2000)
    nuid = "name"
    intf = Interface()
    runtype = "dynamic"
    runnum = rn
    runname = "careag_" + runtype + "_" + str(runnum)
    with dri.session() as ses:
        clock = 0
        while clock < rl:
            for node in specification.nodes:
                ses.write_transaction(node.agentsready, intf)
            clock = ses.write_transaction(intf.gettime)
            ses.write_transaction(intf.tick)
            print("T: " + clock.__str__())
        # ses.write_transaction(activeagentsave, nodes[1:], intf, runname)
    dri.close()
    print("Flow closed")
