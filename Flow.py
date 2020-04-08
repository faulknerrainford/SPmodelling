from neo4j import GraphDatabase
from SPmodelling.Interface import Interface
import specification


# def activeagentsave(tx, activenodes, interface, rn):
#     file = open("AgentLogs" + rn + ".p", 'ab')
#     for anode in activenodes:
#         agents = interface.getnodeagents(tx, anode.name)
#         for agent in agents:
#             record = "Agent " + str(agent["id"]) + ": " + agent["log"]
#             pickle.dump(record, file)
#     file.close()


def main(rl, rn):
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
            res = ses.run("MATCH (a:Clock) "
                          "SET a.time = a.time + 1 "
                          "RETURN a.time")
            clock = res.values()[0][0]
            print("T: " + clock.__str__())
        # ses.write_transaction(activeagentsave, nodes[1:], intf, runname)
    dri.close()
    print("Flow closed")
