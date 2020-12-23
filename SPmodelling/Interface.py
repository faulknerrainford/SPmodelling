from neobolt.exceptions import TransientError, CypherTypeError, ClientError
from neo4j.exceptions import TransientError as n4jTE
from neo4j import GraphDatabase

"""
Module for interacting with cypher databases. Uses node and agent id's in the form of tuples: (id, label, id_type)
"""


def perception(dri, agent):
    """
    Provides the local physical environment of available outgoing "REACHES" edges for the given agent

    :param dri: neo4j database driver
    :param agent: agent id tuple

    :return: Node the agent is located at followed by the outgoing edges of that node and those edges end nodes.
    """
    agent_id, agent_label, agent_uid = tuple(agent)
    while True:
        try:
            ses = dri.session()
            results = ses.run("MATCH (m:Agent)-[s:LOCATED]->(n:Node) "
                              "WITH n, m "
                              "WHERE m.id=$agent "
                              "MATCH (n)-[r:REACHES]->(a) "
                              "RETURN n, r, a", agent=agent_id).values()
            ses.close()
            break
        except (TransientError, n4jTE):
            pass
    if results:
        node = results[0][0]
        edges = [edge[1] for edge in results]
        results = [node] + edges
    return results


def locate_agent(dri, agent):
    """
    Finds which node the given agent is currently located at.

    :param dri: driver for neo4j database
    :param agent: agent id tuple

    :return: Node object the agent is currently located at
    """
    agent_id, agent_label, agent_uid = tuple(agent)
    query = "MATCH (m:Agent)-[s:LOCATED]->(n:Node) WHERE m.id=" + str(agent_id) + " RETURN n"
    while True:
        try:
            ses = dri.session()
            results = ses.run(query).values()
            ses.close()
            break
        except (TransientError, n4jTE):
            pass
    return results[0][0]


def update_contact_edge(dri, node_a, node_b, attribute, value):
    """
    Update a value on a SOCIAL edge based on the nodes at each end.

    :param dri: driver for neo4j database
    :param node_a: id tuple of source node
    :param node_b: id tuple of target node
    :param attribute: attribute to be updated
    :param value: new value of attribute

    :return: None
    """
    node_a, label_a, uid = tuple(node_a)
    node_b, label_b, uid = tuple(node_b)
    if not isinstance(value, str):
        value = str(value)
    query = "MATCH (a"
    if label_a:
        query = query + ":" + label_a
    query = query + ")-[r:SOCIAL]-(b"
    if label_b:
        query = query + ":" + label_b
    query = query + ") WHERE a.id=" + str(node_a) + " and b.id=" + str(node_b) + " SET r." + attribute + "=" + value
    while True:
        try:
            ses = dri.session()
            ses.run(query)
            ses.close()
            break
        except (TransientError, n4jTE):
            pass


def check_node_label(dri, node):
    """
    Return node to check labels of node based on its id, need to provide the type of unique id

    :param dri: driver for neo4j database
    :param node: node id tuple

    :return: neo4j node object
    """
    node_id, node_label, node_uid = tuple(node)
    query = "MATCH (a) WHERE a." + node_uid + "=" + str(node_id) + " RETURN distinct labels(a)"
    while True:
        try:
            ses = dri.session()
            results = ses.run(query).values()
            ses.close()
            break
        except (TransientError, n4jTE):
            pass
    if results:
        results = results[0][0]
        return results
    else:
        return None


def delete_contact(dri, node_a, node_b, contact_type='SOCIAL'):
    """
    Deletes a contact edge in the database.

    :param dri: neo4j driver
    :param node_a: source node id tuple
    :param node_b: target node id tuple
    :param contact_type: label of relationship

    :return: None
    """
    node_a, label_a, uid_a = tuple(node_a)
    node_b, label_b, uid_b = tuple(node_b)
    query = "MATCH (a:" + label_a + ")-[r"
    if contact_type:
        query = query + ":" + contact_type
    query = query + "]-(b:" + label_b + ") WHERE a." + uid_a + "=" + str(node_a) + " and b." + uid_b + "=" + str(node_b)
    query = query + " DELETE r RETURN COUNT(r)"
    while True:
        try:
            ses = dri.session()
            ses.run(query)
            ses.close()
            break
        except (TransientError, n4jTE):
            pass


def agent_relationships(dri, node, rel_type, directed=False):
    """
    Returns outgoing contact edges from a node

    :param dri: neo4j driver
    :param node: source node id tuple
    :param rel_type: type of relationship to look for
    :param directed: if the relationship should be considered directed or undirected

    :return: relationships and end nodes
    """
    node_a, node_label, node_uid = tuple(node)
    if directed:
        direction = ">"
    else:
        direction = ""
    while True:
        try:
            ses = dri.session()
            results = ses.run("MATCH (a:" + node_label + ")-[r:" + rel_type + "]-" + direction
                              + "(b) WHERE a." + node_uid + "=$node_a RETURN r, b", node_a=node_a).values()
            ses.close()
            break
        except (TransientError, n4jTE):
            pass
    return [res[0] for res in results]


def agent_contacts(dri, node_a, contact_label=None):
    """
    Returns outgoing contact edges from a node

    :param dri: neo4j database driver
    :param node_a: source node id tuple
    :param contact_label: type of out going relationship

    :return: relationships and end nodes
    """
    node_a, label_a, uid_a = tuple(node_a)
    if not contact_label:
        contact_label = "SOCIAL"
    query = "MATCH (a:" + label_a + ")-[r:" + contact_label + "]-(b) WHERE a." + uid_a + "=" + str(node_a) \
            + " RETURN *"
    while True:
        try:
            ses = dri.session()
            res = ses.run(query).values()
            ses.close()
            break
        except (TransientError, n4jTE):
            pass
    res = [contact[2] for contact in res]
    results = []
    for contact in res:
        if contact.end_node["id"] == node_a:
            results.append([contact, contact.start_node["id"]])
        else:
            results.append([contact, contact.end_node["id"]])
    return results


def co_located(dri, agent):
    """
    Find agents at the same physical node as the given agent

    :param dri: neo4j driver
    :param agent: agent id tuple

    :return: List of co-located agents
    """
    agent_id, agent_label, agent_uid = tuple(agent)
    while True:
        try:
            ses = dri.session()
            results = ses.run("MATCH (m:" + agent_label + ")-[s:LOCATED]->(n:Node) "
                                                          "WITH n "
                                                          "WHERE m." + agent_uid + "=$agent "
                                                                                   "MATCH (a:Agent)-[s:LOCATED]->("
                                                                                   "n:Node) "
                                                                                   "RETURN a.id",
                              agent=agent_id).values()
            ses.close()
            break
        except (TransientError, n4jTE):
            pass
    results = [res[0] for res in results]
    return results


def get_node(dri, node):
    """
    Returns a given node

    :param dri: neo4j driver
    :param node: node id tuple

    :return: Node object
    """
    node_id, label, uid = tuple(node)
    if not uid:
        uid = "id"
    if label == "Agent":
        query = "MATCH (n:Agent) ""WHERE n." + uid + " = $id ""RETURN n"
        while True:
            try:
                ses = dri.session()
                results = ses.run(query, id=node_id, lab=label).values()
                ses.close()
                break
            except (TransientError, n4jTE):
                pass
    elif label:
        query = "MATCH (n:" + label + ") ""WHERE n." + uid + " = $id ""RETURN n"
        while True:
            try:
                ses = dri.session()
                results = ses.run(query, id=node_id).values()
                ses.close()
                break
            except (TransientError, n4jTE):
                pass
    else:
        query = "MATCH (n) ""WHERE n." + uid + " = $id ""RETURN n"
        while True:
            try:
                ses = dri.session()
                results = ses.run(query, id=node_id).values()
                ses.close()
                break
            except (TransientError, n4jTE):
                pass
    if results:
        node = results[0]
    return node


def get_node_agents(dri, node):
    """
    Finds all agents currently located at a node

    :param dri: neo4j driver
    :param node: node id tuple

    :return: List of agent tuples for agents at node
    """
    node_id, node_label, uid = tuple(node)
    query = "MATCH (a)-[r:LOCATED]->(n) ""WHERE n." + uid + " = '" + str(node_id) + "' RETURN a.id"
    while True:
        try:
            ses = dri.session()
            results = ses.run(query).values()
            ses.close()
            break
        except (TransientError, n4jTE):
            pass
    results = [(res[0], "Agent", "id") for res in results]
    return results


def get_node_value(dri, node, value):
    """
    Retrieves a particular value from a node

    :param dri: neo4j driver
    :param node: node id tuple
    :param value: attribute to return

    :return: value of attribute asked for
    """
    node, label, uid = tuple(node)
    if not uid:
        uid = "id"
    elif uid == "name":
        node = "'" + node + "'"
    if label:
        query = "MATCH (a:" + label + ") ""WHERE a." + uid + " = " + str(node) + " ""RETURN a." + value
    else:
        query = "MATCH (a:Node) ""WHERE a." + uid + " = " + str(node) + " ""RETURN a." + value
    while True:
        try:
            ses = dri.session()
            results = ses.run(query).value()
            ses.close()
            break
        except (TransientError, n4jTE):
            pass
    if results:
        return results[0]


def get_run_name(dri):
    """
    Retrieve the label formed for this run, saved in node in database

    :param dri: neo4j driver

    :return: run name string
    """
    query = "MATCH (a:Tag) ""RETURN a.tag"
    while True:
        try:
            ses = dri.session()
            res = ses.run(query).value()[0]
            ses.close()
            return res
        except (TransientError, n4jTE):
            pass


def get_pop_size(dri):
    run_name = get_run_name(dri)
    parts = run_name.split('_')
    return int(parts[2])


def get_run_length(dri):
    run_name = get_run_name(dri)
    parts = run_name.split('_')
    return int(parts[3])


def get_time(dri):
    """
    Retrieves the current time on the database clock

    :param dri: neo4j driver

    :return: Current time on clock
    """
    query = "MATCH (a:Clock) ""RETURN a.time"
    while True:
        try:
            ses = dri.session()
            results = ses.run(query).value()[0]
            ses.close()
            break
        except (TransientError, n4jTE):
            pass
    return results


def tick(dri):
    """
    Increment the clock in the database

    :param dri: neo4j driver

    :return: New time
    """
    time = 1 + get_time(dri)
    query = "MATCH (a:Clock) ""SET a.time=$time "
    while True:
        try:
            ses = dri.session()
            res = ses.run(query, time=time).values()
            ses.close()
            return res
        except (TransientError, n4jTE):
            pass


def shortest_path(dri, node_a, node_b, edge_label, directed=False):
    """
    Returns the length of the shortest path between two nodes, using edges of the type given in edge_label

    :param dri: neo4j driver
    :param node_a: first node id tuple
    :param node_b: second node id tuple
    :param edge_label: label for the type of relationships to use in path
    :param directed: whether to consider direction of path in calculations

    :return: Length of shortest path between two nodes
    """
    node_a, label_a, uid_a = tuple(node_a)
    node_b, label_b, uid_b = tuple(node_b)
    if directed:
        directionality = 'DIRECTED'
    else:
        directionality = 'UNDIRECTED'
    query = "MATCH(start: " + label_a + "{" + uid_a + ": " + str(node_a) + "}), (end:" + label_b \
            + " {" + uid_b + ":" + str(node_b) \
            + "}) CALL gds.alpha.shortestPath.stream({nodeProjection: '" + label_a \
            + "', relationshipProjection: {SOCIAL: {type: '" + edge_label \
            + "', orientation: '" + directionality + "'}}, startNode: start, endNode: end}) YIELD nodeId, cost " \
                                                     "RETURN gds.util.asNode(nodeId).id AS name, cost"
    while True:
        try:
            ses = dri.session()
            sp = ses.run(query)
            sp = sp.values()
            ses.close()
            break
        except (TransientError, n4jTE):
            pass
    if sp:
        return sp[-1][-1]


def update_edge(dri, edge, attr, value, edge_label="REACHES"):
    """
    Modify an attribute of an edge

    :param dri: neo4j driver
    :param edge: relationship object
    :param attr: attribute to modify
    :param value: new value of attribute
    :param edge_label: label of relationship

    :return: None
    """
    start, start_label, start_uid = tuple(edge[0])
    end, end_label, end_uid = tuple(edge[1])
    if start_uid == "id":
        start = str(start)
    if end_uid == "id":
        end = str(end)
    query = "MATCH (a:" + start_label + ")-[r:" + edge_label + "]-(b:" + end_label + ") ""WHERE a." + start_uid \
            + "=" + str(start) + " AND b." + end_uid + "=" + str(end) + " SET r." + attr + "=" + str(value) + \
            " RETURN r"
    while True:
        try:
            ses = dri.session()
            ses.run(query).values()
            ses.close()
            break
        except (TransientError, n4jTE):
            pass


def update_node(dri, node, attr, value):
    """
    Update attribute of a node

    :param dri: neo4j driver
    :param node: node id tuple
    :param attr: attribute to be updated
    :param value: new value for the attribute

    :return: None
    """
    node, label, uid = tuple(node)
    if not uid:
        uid = "id"
    if not label:
        label = "Node"
    query = "MATCH (a:" + label + ") ""WHERE a." + uid + "=$node ""SET a." + attr + "=$value"
    while True:
        try:
            ses = dri.session()
            ses.run(query, node=node, value=value)
            ses.close()
            break
        except (TransientError, n4jTE):
            pass


def update_agent(dri, node, attr, value):
    """
    Update an agents attribute value.

    :param dri: neo4j driver
    :param node: node id tuple
    :param attr: attribute to be updated
    :param value: new value of attribute

    :return: None
    """
    node, label, uid = tuple(node)
    if not uid:
        uid = "id"
    if not label:
        label = "Agent"
    query = "MATCH (a:" + label + ") ""WHERE a." + uid + "=$node ""SET a." + attr + "=$value"
    while True:
        try:
            ses = dri.session()
            ses.run(query, node=node, value=value)
            ses.close()
            break
        except (TransientError, n4jTE):
            pass


def delete_agent(dri, agent):
    """
    Delete an agent and all its relationships in the database

    :param dri: neo4j driver
    :param agent: agent id tuple

    :return: None
    """
    agent, label, uid = tuple(agent)
    if not uid:
        uid = "id"
    if not label:
        label = "Agent"
    while True:
        try:
            ses = dri.session()
            ses.run("MATCH (n:" + label + ") ""WHERE n." + uid + "=$ID ""DETACH DELETE n", ID=agent)
            ses.close()
            break
        except (TransientError, n4jTE):
            pass


def add_agent(dri, node, agent_label, params):
    """
    Insert a new agent into the system at node

    :param dri: neo4j driver
    :param node: node id tuple for node to locate agent at
    :param agent_label: label for the new agent
    :param params: list of parameters of agent

    :return: None
    """
    node, label, uid = tuple(node)
    if not uid:
        uid = "name"
    if not label:
        label = "Node"
    query = "MATCH (n:Agent) ""WITH n ""ORDER BY n.id DESC ""RETURN n.id"
    while True:
        try:
            ses = dri.session()
            highest_id = ses.run(query).values()
            ses.close()
            break
        except (TransientError, n4jTE):
            pass
    if highest_id:
        agent_id = highest_id[0][0] + 1
    else:
        agent_id = 0
    query = "CREATE (a:" + agent_label + " {id:" + str(agent_id)
    for param in params:
        query = query + ", " + param + ":" + str(params[param])
    query = query + "})-[r:LOCATED]->(n)"
    while True:
        try:
            ses = dri.session()
            ses.run("MATCH (n:" + label + ") ""WHERE n." + uid + "= '" + node + "' " + query)
            ses.close()
            break
        except (TransientError, n4jTE):
            pass


def create_edge(dri, node_a, node_b, edge_label=None, parameters=None):
    """
    Adds and edge between two nodes with attributes and label as given

    :param dri: neo4j driver
    :param node_a: source node id tuple
    :param node_b: target node id tuple
    :param edge_label: label of new edge
    :param parameters: parameters of new edge

    :return: None
    """
    node_a, label_a, uid_a = tuple(node_a)
    node_b, label_b, uid_b = tuple(node_b)
    if not uid_a:
        uid_a = "id"
    if not uid_b:
        uid_b = "id"
    if label_a and label_b:
        query = "MATCH (a:" + label_a + ") WHERE a." + uid_a + "=" + str(node_a) + " WITH a MATCH (b:" + label_b \
                + ") WHERE b." + uid_b + "=" + str(node_b) + " WITH a, b CREATE (a)-[n:" + edge_label
        if parameters:
            query = query + " {" + str(parameters) + "}"
        query = query + "]->(b) "
        while True:
            try:
                ses = dri.session()
                ses.run(query)
                ses.close()
                break
            except (TransientError, n4jTE):
                pass
    else:
        query = "MATCH (a:" + node_a[1] + ") WHERE a." + node_a[2] + "=" + str(node_a[0]) + " WITH a MATCH (b:" \
                + node_b[1] + ") WHERE b." + node_b[2] + "=" + str(node_b[0]) + " WITH a, b CREATE (a)-[n:" + edge_label
        if parameters:
            query = query + " {" + str(parameters) + "}"
        query = query + "]->(b) "
        while True:
            try:
                ses = dri.session()
                ses.run(query)
                ses.close()
                break
            except (TransientError, n4jTE):
                pass


def shortest_social_path(dri, node, agent):
    """
    Returns shortest path using social links from an agent to agents located at a given node

    :param dri: neo4j database driver
    :param node: node id tuple for target agents must be located at
    :param agent: source agent id tuple

    :return: Length of shortest path
    """
    node_id, node_label, node_uid = tuple(node)
    agent_id, agent_label, agent_uid = tuple(agent)
    agents = get_node_agents(dri, [node_id, node_label, node_uid])
    paths = [shortest_path(dri, agent, ag, edge_label="SOCIAL") for ag in agents]
    paths = [path for path in paths if path]
    if paths:
        return min(paths)
    else:
        return float('inf')


def add_label_node(dri, node, label):
    """
    Add database label to an existing node, nodes only not agents

    :param dri: neo4j driver
    :param node: node id tuple to be updated
    :param label: new label to be added, must be in CamelCase

    :return: None
    """
    node_id, node_label, node_uid = tuple(node)
    if not node_label:
        node_label = "Node"
    if not node_uid:
        node_uid = "name"
    query = "MATCH (a:" + node_label + ") WITH a." + node_uid + "=" + node_id + " SET a :" + label
    while True:
        try:
            ses = dri.session()
            ses.run(query)
            ses.close()
            break
        except (TransientError, n4jTE):
            pass


def add_label_agent(dri, agent, label):
    """
    Add extra label to an agent in the database

    :param dri: neo4j driver
    :param agent: agent to update id tuple
    :param label: new label to be added, must be in CamelCase

    :return: None
    """
    agent_id, agent_label, agent_uid = tuple(agent)
    if not agent_label:
        agent_label = "Agent"
    if not agent_uid:
        agent_uid = "id"
    query = "MATCH (a:" + agent_label + ") WITH a." + agent_uid + "=" + agent_id + " SET a :" + label
    while True:
        try:
            ses = dri.session()
            ses.run(query)
            ses.close()
            break
        except (TransientError, n4jTE):
            pass


def check_services_location(dri, node):
    """
    Return a list of services provided at a location

    :param dri: neo4j driver
    :param node: node id tuple for node services should be located at

    :return: list of service id tuples for services at the given node
    """
    node_id, node_label, node_uid = tuple(node)
    if node_uid == "name":
        node_id = "'" + node_id + "'"
    query = "MATCH (s)-[r:PROVIDE]->(n:" + node_label + ") WHERE n." + node_uid + "=" + str(node_id) + " RETURN s.name"
    while True:
        try:
            ses = dri.session()
            res = ses.run(query).value()
            ses.close()
            break
        except (TransientError, n4jTE):
            pass
    return [(s, "Service", "name") for s in res]


def louvain(dri, node_label, edge_label, seed_property=None):
    """
    Returns the clustering of the group of nodes based on the edge type given

    :param dri: neo4j driver
    :param node_label: label for node type to be clustered
    :param edge_label: label for the type of relationships to use as network over which to cluster
    :param seed_property: property of node which records its most closely associated cluster

    :return: Cluster assignments for nodes
    """
    while True:
        try:
            ses = dri.session()
            check = ses.run("CALL gds.graph.exists('louvainGraph') YIELD exists").values()[0][0]
            ses.close()
            break
        except (TransientError, n4jTE):
            pass
    if not check:
        query = "CALL gds.graph.create.cypher('louvainGraph', 'MATCH (a:" + node_label \
                + ") RETURN id(a) AS id', 'MATCH (a)-[r:" + edge_label \
                + "]-(b) RETURN id(a) AS source, id(b) AS target')"
        while True:
            try:
                ses = dri.session()
                ses.run(query).values()
                ses.close()
                break
            except (TransientError, n4jTE):
                pass
    query = "CALL gds.louvain.stream('louvainGraph', {includeIntermediateCommunities:true"
    if seed_property:
        query = query + ", seedProperty:'" + seed_property + "'"
    query = query + "}) YIELD nodeId, communityId, intermediateCommunityIds RETURN gds.util.asNode(nodeId).id, "
    query = query + "communityId, intermediateCommunityIds"
    while True:
        try:
            ses = dri.session()
            sp = ses.run(query).values()
            ses.run("CALL gds.graph.drop('louvainGraph') YIELD graphName;")
            ses.close()
            break
        except (TransientError, n4jTE):
            pass
    if sp:
        return sp


def add_node(dri, node, params=None):
    """
    Insert a new node into the system at node

    :param dri: neo4j driver
    :param node: node id tuple for node to add to system
    :param params: list of parameters of node

    :return: None
    """
    node_id, node_label, node_uid = tuple(node)
    query = "CREATE (n:" + node_label + " {" + node_uid + ":" + str(node_id)
    if params:
        for param in params.keys():
            query = query + ", " + param + ":" + str(params[param])
    query = query + "})"
    while True:
        try:
            ses = dri.session()
            ses.run(query)
            ses.close()
            break
        except (TransientError, n4jTE):
            pass


def check_groupings(dri, agent):
    """
    check which clusters an agent is associated with

    :param dri: neo4j driver
    :param agent: agent id tuple

    :return: list of cluster id numbers
    """
    agent_id, agent_label, agent_uid = tuple(agent)
    query = "MATCH (c)-[r:GROUPED]->(a:" + agent_label + ") WHERE a." + agent_uid + "=" + str(agent_id) + " RETURN c.id"
    while True:
        try:
            ses = dri.session()
            res = ses.run(query).values()
            ses.close()
            break
        except (TransientError, n4jTE):
            pass
    if res:
        return res
    else:
        return None


def delete_edge(dri, node_a, node_b, edge_label=None):
    query = "MATCH (a:" + node_a[1] + ") WHERE a." + node_a[2] + "=" + str(node_a[0]) + " WITH a MATCH (b:" \
            + node_b[1] + ") WHERE b." + node_b[2] + "=" + str(node_b[0]) + " WITH a, b MATCH (a)-[r:" \
            + edge_label + "]->(b) WITH r DELETE r"
    while True:
        try:
            ses = dri.session()
            ses.run(query)
            ses.close()
            break
        except (TransientError, n4jTE):
            pass


def agents_in_cluster(dri, cluster):
    query = "MATCH (a:Agent)<-[:GROUPED]-(c:Cluster) WHERE c.id=" + str(cluster[0]) + " RETURN a.id"
    while True:
        try:
            ses = dri.session()
            res = ses.run(query).value()
            ses.close()
            break
        except (TransientError, n4jTE):
            pass
    if res:
        agents = res
        if agents:
            return [[ag, "Agent", "id"] for ag in agents]


def clusters_in_system(dri):
    query = "MATCH (c:Cluster) RETURN c.id ORDER BY c.id"
    while True:
        try:
            ses = dri.session()
            res = ses.run(query)
            res = res.value()
            ses.close()
            break
        except ((TransientError, n4jTE), CypherTypeError):
            pass
    if res:
        clusters = res
        return clusters


def connectedness(dri, agent, cluster):
    contacts = [ag[1] for ag in agent_contacts(dri, agent, "SOCIAL")]
    group = [ag[0] for ag in agents_in_cluster(dri, cluster)]
    return len(set(group).intersection(set(contacts)))


def delete_agent_location(dri, agent, location_type=None):
    agent_id, agent_label, agent_uid = agent
    if not location_type:
        location_type = "LOCATED"
    query = "MATCH (n:" + agent_label + ")-[r:" + location_type + "]->() WHERE n." + agent_uid + "=" + str(agent_id) \
            + " DELETE r"
    while True:
        try:
            ses = dri.session()
            ses.run(query)
            ses.close()
            break
        except (TransientError, n4jTE):
            pass


def add_agent_location(dri, agent, node, location_type=None):
    agent_id, agent_label, agent_uid = agent
    node_id, node_label, node_uid = node
    if not location_type:
        location_type = "LOCATED"
    query = "MATCH (a:" + agent_label + "), (n:" + node_label + ") WHERE a." + agent_uid + "=" + str(agent_id) \
            + " AND n." + node_uid + "='" + str(node_id) + "' CREATE (a)-[r:" + location_type + "]->(n)"
    while True:
        try:
            ses = dri.session()
            ses.run(query)
            ses.close()
            break
        except (TransientError, n4jTE):
            pass


def relocate_agent(dri, agent, node, location_type=None):
    agent_id, agent_label, agent_uid = agent
    node_id, node_label, node_uid = node
    if not location_type:
        location_type = "LOCATED"
    delete_agent_location(dri, agent, location_type)
    add_agent_location(dri, agent, node, location_type)


def get_agents(dri, agent_type="Agent"):
    query = "MATCH (a:" + agent_type + ") RETURN a.id"
    while True:
        try:
            ses = dri.session()
            res = ses.run(query).values()
            ses.close()
            break
        except (TransientError, n4jTE):
            pass
    if res:
        return res


def get_edge_value(dri, edge, attribute, edge_label):
    node_a, label_a, uid_a = tuple(edge[0])
    node_b, label_b, uid_b = tuple(edge[1])
    query = "MATCH (a:" + label_a + " {" + uid_a + ":" + str(node_a) + "})-[r:" + edge_label + "]-(b:" + label_b \
            + " {" + uid_a + ":" \
            + str(node_b) + "}) RETURN r." + attribute
    while True:
        try:
            ses = dri.session()
            res = ses.run(query).values()
            ses.close()
            break
        except (TransientError, n4jTE):
            pass
    if res:
        return res[0][0]
