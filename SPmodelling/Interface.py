from neobolt.exceptions import TransientError


def perception(tx, agent):
    """
    Provides the local environment for the given agent

    :param tx: write transaction for neo4j database
    :param agent: id number for agent

    :return: Node the agent is located at followed by the outgoing edges of that node and those edges end nodes.
    """
    agent_id, agent_label, agent_uid = tuple(agent)
    while True:
        try:
            results = tx.run("MATCH (m:Agent)-[s:LOCATED]->(n:Node) "
                             "WITH n, m "
                             "WHERE m.id=$agent "
                             "MATCH (n)-[r:REACHES]->(a) "
                             "RETURN n, r, a", agent=agent_id).values()
            break
        except TransientError:
            pass
    if results:
        node = results[0][0]
        edges = [edge[1] for edge in results]
        results = [node] + edges
    return results


def locate_agent(tx, agent):
    """
    Finds which node the given agent is currently located at.

    :param tx: read or write transaction for neo4j database
    :param agent: agent id number

    :return: Node the agent is currently located at
    """
    agent_id, agent_label, agent_uid = tuple(agent)
    while True:
        try:
            results = tx.run("MATCH (m:Agent)-[s:LOCATED]->(n:Node) "
                             "WHERE m.id=$agent "
                             "RETURN n", agent=agent_id).values()
            break
        except TransientError:
            pass
    return results[0][0]


def update_contact_edge(tx, node_a, node_b, attribute, value):
    """
    Update a value on a SOCIAL edge based on the nodes at each end.

    :param tx: write transaction for neo4j database
    :param node_a: id of first node
    :param node_b: id of second node
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
            tx.run(query)
            break
        except TransientError:
            pass


def check_node_label(tx, node):
    """
    Return node to check labels of node based on its id, need to provide the type of unique id

    :param tx: read or write transaction for neo4j database
    :param node: unique identifier for node

    :return: neo4j node object
    """
    node_id, node_label, node_uid = tuple(node)
    query = "MATCH (a) WHERE a." + node_uid + "=" + str(node_id) + " RETURN distinct labels(a)"
    while True:
        try:
            results = tx.run(query).values()
            break
        except TransientError:
            pass
    if results:
        results = results[0][0]
        return results
    else:
        return None


def delete_contact(tx, node_a, node_b, contact_type='SOCIAL'):
    """
    Deletes a contact edge in the database.

    :param tx: neo4j write transaction
    :param node_a: id, label and id type of source node
    :param node_b: id, label and id type of target node
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
            tx.run(query)
            break
        except TransientError:
            pass


def agent_relationships(tx, node, rel_type, directed=False):
    """
    Returns outgoing contact edges from a node

    :param tx: neo4j read or write transaction
    :param node: source node id, label and id type
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
            results = tx.run("MATCH (a:" + node_label + ")-[r:" + rel_type + "]-" + direction
                             + "(b) WHERE a." + node_uid + "=$node_a RETURN r, b", node_a=node_a).values()
            break
        except TransientError:
            pass
    return [res[0] for res in results]


def agent_contacts(tx, node_a, contact_label=None):
    """
    Returns outgoing contact edges from a node

    :param tx: neo4j read or write transaction
    :param node_a: source node id, label and id type
    :param contact_label: type of out going relationship

    :return: relationships and end nodes
    """
    node_a, label_a, uid_a = tuple(node_a)
    if not contact_label:
        contact_label = label_a
    query = "MATCH (a:" + label_a + ")-[r:SOCIAL]-(b:" + contact_label + ") WHERE a." + uid_a + "=" + str(node_a) \
            + " RETURN r, b"
    while True:
        try:
            results = tx.run(query).values()
            break
        except TransientError:
            pass
    return [res[0] for res in results]


def co_located(tx, agent):
    """
    Find agents at the same physical node as the given agent

    :param tx: neo4j read or write transaction
    :param agent: agent id, label and id type

    :return: List of co-located agents
    """
    agent_id, agent_label, agent_uid = tuple(agent)
    while True:
        try:
            results = tx.run("MATCH (m:" + agent_label + ")-[s:LOCATED]->(n:Node) "
                             "WITH n "
                             "WHERE m." + agent_uid + "=$agent "
                             "MATCH (a:Agent)-[s:LOCATED]->(n:Node) "
                             "RETURN a", agent=agent_id).values()
            break
        except TransientError:
            pass
    results = [res[0] for res in results]
    return results


def get_node(tx, node):
    """
    Returns a given node

    :param tx: neo4j read or write transaction
    :param node: node id, label and id type

    :return: Node object
    """
    node_id, label, uid = tuple(node)
    if not uid:
        uid = "id"
    if label == "Agent":
        query = "MATCH (n:Agent) ""WHERE n." + uid + " = $id ""RETURN n"
        while True:
            try:
                results = tx.run(query, id=node_id, lab=label).values()
                break
            except TransientError:
                pass
    elif label:
        query = "MATCH (n:" + label + ") ""WHERE n." + uid + " = $id ""RETURN n"
        while True:
            try:
                results = tx.run(query, id=node_id).values()
                break
            except TransientError:
                pass
    else:
        query = "MATCH (n) ""WHERE n." + uid + " = $id ""RETURN n"
        while True:
            try:
                results = tx.run(query, id=node_id).values()
                break
            except TransientError:
                pass
    node = results[0][0]
    return node


def get_node_agents(tx, node):
    """
    Finds all agents currently located at a node

    :param tx: neo4j read or write transaction
    :param node

    :return: List of agents at node
    """
    node_id, node_label, uid = tuple(node)
    query = "MATCH (a)-[r:LOCATED]->(n) ""WHERE n." + uid + " = '" + str(node_id) + "' RETURN a.id"
    while True:
        try:
            results = tx.run(query).values()
            break
        except TransientError:
            pass
    results = [(res[0], "Agent", "id") for res in results]
    return results


def get_node_value(tx, node, value):
    """
    Retrieves a particular value from a node

    :param tx: neo4j read or write transaction
    :param node: id, label and type of id of the node
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
            results = tx.run(query).value()
            break
        except TransientError:
            pass
    return results[0]


def get_run_name(tx):
    """
    Retrieve the label formed for this run, saved in node in database

    :param tx: neo4j read or write transaction

    :return: run name string
    """
    query = "MATCH (a:Tag) ""RETURN a.tag"
    while True:
        try:
            return tx.run(query).value()[0]
        except TransientError:
            pass


def get_time(tx):
    """
    Retrieves the current time on the database clock

    :param tx: neo4j read or write transaction

    :return: Current time on clock
    """
    query = "MATCH (a:Clock) ""RETURN a.time"
    while True:
        try:
            results = tx.run(query).value()[0]
            break
        except TransientError:
            pass
    return results


def tick(tx):
    """
    Increment the clock in the database

    :param tx: neo4j write transaction

    :return: New time
    """
    time = 1 + get_time(tx)
    query = "MATCH (a:Clock) ""SET a.time=$time "
    while True:
        try:
            return tx.run(query, time=time)
        except TransientError:
            pass


def shortest_path(tx, node_a, node_b, edge_label, directed=False):
    """
    Returns the length of the shortest path between two nodes, using edges of the type given in edge_label

    :param tx: neo4j read or write transaction
    :param node_a: first node id
    :param node_b: second node id
    :param edge_label: label for the type of relationships to use in path
    :param directed: whether to consider direction of path in calculations

    :return: Length of shortest path between two nodes
    """
    # TODO: set up graph
    node_a, label_a, uid_a = tuple(node_a)
    node_b, label_b, uid_b = tuple(node_b)
    if directed:
        directionality = 'OUTGOING'
    else:
        directionality = 'BOTH'
    query = "MATCH (a) WHERE a." + uid_a + "=" + str(node_a) + " WITH a MATCH (b) WHERE b." + uid_b + "=" \
            + str(node_b) + " WITH a, b "
    query = query + "CALL gds.alpha.shortestPath.stream(a, b,null, {relationshipQuery:'" + edge_label
    query = query + "', direction: '" + directionality + "'}) YIELD totalCost RETURN totalCost"
    while True:
        try:
            sp = tx.run(query).values()
            break
        except TransientError:
            pass
    if sp:
        return sp[0][0]


def update_edge(tx, edge, attr, value, uid=None):
    """
    Modify an attribute of an edge

    :param tx: neo4j write transaction
    :param edge: relationship object
    :param attr: attribute to modify
    :param value: new value of attribute
    :param uid: type of id used in system

    :return: None
    """
    if isinstance(edge,list):
        start, start_label, start_uid = tuple(edge[0])
        end, end_label, end_uid = tuple(edge[1])
    else:
        if not uid:
            start_uid = "id"
            end_uid = "id"
        else:
            start_uid = uid
            end_uid = uid
        start_label = "Node"
        end_label = "Node"
        start = edge.start_node[uid]
        end = edge.end_node[uid]
    query = "MATCH (a:" + start_label + ")-[r:REACHES]->(b:" + end_label + ") ""WHERE a." + start_uid \
            + "=$start AND b." + end_uid + "=$end ""SET r." + attr + "=$val"
    while True:
        try:
            tx.run(query, start=start, end=end, val=value)
            break
        except TransientError:
            pass


def update_node(tx, node, attr, value):
    """
    Update attribute of a node

    :param tx: neo4j write transaction
    :param node: node id, label, type of id
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
            tx.run(query, node=node, value=value)
            break
        except TransientError:
            pass


def update_agent(tx, node, attr, value):
    """
    Update an agents attribute value.

    :param tx: neo4j write transaction
    :param node: node id, label and type of id
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
            tx.run(query, node=node, value=value)
            break
        except TransientError:
            pass


def delete_agent(tx, agent):
    """
    Delete an agent and all its relationships in the database

    :param tx: neo4j write transaction
    :param agent: agent id

    :return: None
    """
    agent, label, uid = tuple(agent)
    if not uid:
        uid = "id"
    if not label:
        label = "Agent"
    while True:
        try:
            tx.run("MATCH (n:" + label + ") ""WHERE n." + uid + "=$ID ""DETACH DELETE n", ID=agent[uid])
            break
        except TransientError:
            pass


def add_agent(tx, node, agent_label, params):
    """
    Insert a new agent into the system at node

    :param tx: neo4j write transaction
    :param node: node to locate agent at, id, label and type of id
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
    highest_id = tx.run(query).values()
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
            tx.run("MATCH (n:" + label + ") ""WHERE n." + uid + "= '" + node[uid] + "' " + query)
            break
        except TransientError:
            pass


def create_edge(tx, node_a, node_b, edge_label=None, parameters=None):
    """
    Adds and edge between two nodes with attributes and label as given

    :param tx: neo4j write transaction
    :param node_a: source node id, label and id type
    :param node_b: target node id, label and id type
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
                tx.run(query)
                break
            except TransientError:
                pass
    else:
        query = "MATCH (a:" + node_a[1] + ") WHERE a." + node_a[2] + "=" + str(node_a[0]) + " WITH a MATCH (b:" \
                + node_b[1] + ") WHERE b." + node_b[2] + "=" + str(node_b[0]) + " WITH a, b CREATE (a)-[n:" + edge_label
        if parameters:
            query = query + " {" + str(parameters) + "}"
        query = query + "]->(b) "
        while True:
            try:
                tx.run(query)
                break
            except TransientError:
                pass


def shortest_social_path(tx, node, agent):
    """
    Returns shortest path using social links from an agent to agents located at a given node

    :param tx: neo4j database read transaction
    :param node: node target agents must be located at, id, label and type of id
    :param agent: id, label and type of id of source agent

    :return:
    """
    node_id, node_label, node_uid = tuple(node)
    agent_id, agent_label, agent_uid = tuple(agent)
    agents = get_node_agents(tx, [node_id, node_label, node_uid])
    paths = [shortest_path(tx, [agent_id, agent_label, agent_uid], [ag, "Agent","id"],
                           edge_label="SOCIAL") for ag in agents]
    if paths:
        return min(paths)
    else:
        return float('inf')


def add_label_node(tx, node, label):
    """
    Add database label to an existing node, nodes only not agents

    :param tx: neo4j write transaction
    :param node: id, label and type of id of node to be updated
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
            tx.run(query)
            break
        except TransientError:
            pass


def add_label_agent(tx, agent, label):
    """
    Add extra label to an agent in the database

    :param tx: neo4j write transaction
    :param agent: id, label and type of id of agent to update
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
            tx.run(query)
            break
        except TransientError:
            pass


def check_services_location(tx, node):
    node_id, node_label, node_uid = tuple(node)
    query = "MATCH (s)-[r:PROVIDE]->(n" + node_label + ") WHERE n." + node_uid + "=" + str(node_id) + "RETURN s"
    res = tx.run(query).values()
    return [(s, s["name"], "Service", "name") for s in res]


def louvain(tx, node_label, edge_label, seed_property=None):
    """
    Returns the clustering of the group of nodes based on the edge type given

    :param tx: neo4j read or write transaction
    :param node_label: label for both nodes
    :param edge_label: label for the type of relationships to use at network over which to cluster
    :param seed_property: property of node which records its most closely associated cluster

    :return: Cluster assignments for nodes
    """
    if not tx.run("CALL gds.graph.exists('louvainGraph') YIELD exists").values()[0][0]:
        query = "CALL gds.graph.create('louvainGraph', '" + node_label + "', '" + edge_label + "')"
        while True:
            try:
                tx.run(query).values()
                break
            except TransientError:
                pass
    query = "CALL gds.louvain.stream('louvainGraph', {includeIntermediateCommunities: true"
    if seed_property:
        query = ", seedProperty:'" + seed_property + "'"
    query = query + "}) YIELD nodeId, communityId, intermediateCommunityIds RETURN gds.util.asNode(nodeId).id, "
    query = query + "communityId, intermediateCommunityIds"
    while True:
        try:
            sp = tx.run(query)
            break
        except TransientError:
            pass
    tx.run("CALL gds.graph.drop('louvainGraph') YIELD graphName;")
    if sp:
        return sp


def add_node(tx, node, params=None):
    """
    Insert a new node into the system at node

    :param tx: neo4j write transaction
    :param node: node id, label and type of id, to add to system
    :param params: list of parameters of node

    :return: None
    """
    node_id, node_label, node_uid = tuple(node)
    query = "CREATE (n:" + node_label + " {" + node_uid + ":" + str(node_id)
    if params:
        for param in params:
            query = query + ", " + param + ":" + str(params[param])
    query = query + "})"
    while True:
        try:
            tx.run(query)
            break
        except TransientError:
            pass


def check_groupings(tx, agent):
    agent_id, agent_label, agent_uid = tuple(agent)
    query = "MATCH (c)-[r:GROUPED]->(a:" + agent_label + ") WHERE a." + agent_uid + "=" + agent_id + " RETURN c.id"
    while True:
        try:
            res = tx.run(query)
            break
        except TransientError:
            pass
    if res:
        return res.values()
    else:
        return None
