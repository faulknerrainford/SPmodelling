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
    dri = GraphDatabase.driver(uri, auth=specification.Flow_auth,
                               max_connection_lifetime=36000)
    clock = 0
    while clock < rl:
        agents = intf.get_agents(dri, "Agent")
        agents = [(agent[0], "Agent", "id") for agent in agents]
        for agent in agents:
            if labels := intf.check_node_label(dri, agent):
                for label in labels:
                    if label in specification.AgentClasses.keys():
                        Agclass = specification.AgentClasses[label]
                        agclass = Agclass(agent[0])
                        agclass.socialise(dri)
        clock = intf.get_time(dri)
    dri.close()
    print("Social closed")
