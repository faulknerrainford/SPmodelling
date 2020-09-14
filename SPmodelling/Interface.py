from neobolt.exceptions import TransientError


def perception(tx, agent):
    """
    Provides the local environment for the given agent

    :param tx: write transaction for neo4j database
    :param agent: id number for agent

    :return: Node the agent is located at followed by the outgoing edges of that node and those edges end nodes.
    """
    while True:
        try:
            results = tx.run("MATCH (m:Agent)-[s:LOCATED]->(n:Node) "
                             "WITH n, m "
                             "WHERE m.id={agent} "
                             "MATCH (n)-[r:REACHES]->(a) "
                             "RETURN n, r, a", agent=agent).values()
            break
        except TransientError:
            pass
    if results:
        node = results[0][0]
        edges = [edge[1] for edge in results]
        results = [node] + edges
    return results


def locateagent(tx, agent):
    """
    Finds which node the given agent is currently located at.

    :param tx: read or write transaction for neo4j database
    :param agent: agent id number

    :return: Node the agent is currently located at
    """
    while True:
        try:
            results = tx.run("MATCH (m:Agent)-[s:LOCATED]->(n:Node) "
                             "WHERE m.id={agent} "
                             "RETURN n", agent=agent).values()
            break
        except TransientError:
            pass
    return results[0][0]


def updatecontactedge(tx, node_a, node_b, attribute, value, label_a=None, label_b=None):
    """
    Update a value on a SOCIAL edge based on the nodes at each end.

    :param tx: write transaction for neo4j database
    :param node_a: id of first node
    :param node_b: id of second node
    :param attribute: attribute to be updated
    :param value: new value of attribute
    :param label_a: label of first node
    :param label_b: label of second node

    :return: None
    """
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


def checknodelabel(tx, node_a, uid):
    """
    Return node to check labels of node based on its id, need to provide the type of unique id

    :param tx: read or write transaction for neo4j database
    :param node_a: unique identifier for node
    :param uid: type of unique identifier - name or id

    :return: neo4j node object
    """
    query = "MATCH (a) WHERE a." + uid + "=" + str(node_a) + " RETURN distinct labels(a)"
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


def deletecontact(tx, node_a, node_b, label_a, label_b, contact_type='SOCIAL'):
    """
    Deletes a contact edge in the database.

    :param tx: neo4j write transaction
    :param node_a: id of source node
    :param node_b: id of target node
    :param label_a: label of source node
    :param label_b: label of target node
    :param contact_type: label of relationship

    :return: None
    """
    query = "MATCH (a:" + label_a + ")-[r"
    if contact_type:
        query = query + ":" + contact_type
    query = query + "]-(b:" + label_b + ") WHERE a.id=" + str(node_a) + " and b.id=" + str(node_b)
    query = query + " DELETE r RETURN COUNT(r)"
    while True:
        try:
            tx.run(query)
            break
        except TransientError:
            pass


def agentrelationships(tx, node_a, node_label, rel_type, directed=False):
    """
    Returns outgoing contact edges from a node

    :param tx: neo4j read or write transaction
    :param node_a: source node id
    :param node_label: source node label
    :param rel_type: type of relationship to look for
    :param directed: if the relationship should be considered directed or undirected

    :return: relationships and end nodes
    """
    if directed:
        direction = ">"
    else:
        direction = ""
    while True:
        try:
            results = tx.run("MATCH (a:" + node_label + ")-[r:" + rel_type + "]-" + direction
                             + "(b) WHERE a.id={node_a} RETURN r, b", node_a=node_a).values()
            break
        except TransientError:
            pass
    return [res[0] for res in results]


def agentcontacts(tx, node_a, label, contact_label=None):
    """
    Returns outgoing contact edges from a node

    :param tx: neo4j read or write transaction
    :param node_a: source node id
    :param label: source node label
    :param contact_label: type of out going relationship

    :return: relationships and end nodes
    """
    if not contact_label:
        contact_label = label
    query = "MATCH (a:" + label + ")-[r:SOCIAL]-(b:" + contact_label + ") WHERE a.id=" + str(node_a) + " RETURN r, b"
    while True:
        try:
            results = tx.run(query).values()
            break
        except TransientError:
            pass
    return [res[0] for res in results]


def colocated(tx, agent):
    """
    Find agents at the same physical node as the given agent

    :param tx: neo4j read or write transaction
    :param agent: agent id

    :return: List of co-located agents
    """
    while True:
        try:
            results = tx.run("MATCH (m:Agent)-[s:LOCATED]->(n:Node) "
                             "WITH n "
                             "WHERE m.id={agent} "
                             "MATCH (a:Agent)-[s:LOCATED]->(n:Node) "
                             "RETURN a", agent=agent).values()
            break
        except TransientError:
            pass
    results = [res[0] for res in results]
    return results


def getnode(tx, node_id, label=None, uid=None):
    """
    Returns a given node

    :param tx: neo4j read or write transaction
    :param node_id: id for wanted node
    :param label: node label
    :param uid: type of id

    :return: Node object
    """
    if not uid:
        uid = "id"
    if label == "Agent":
        query = "MATCH (n:Agent) ""WHERE n." + uid + " = {id} ""RETURN n"
        while True:
            try:
                results = tx.run(query, id=node_id, lab=label).values()
                break
            except TransientError:
                pass
    elif label:
        query = "MATCH (n:" + label + ") ""WHERE n." + uid + " = {id} ""RETURN n"
        while True:
            try:
                results = tx.run(query, id=node_id).values()
                break
            except TransientError:
                pass
    else:
        query = "MATCH (n) ""WHERE n." + uid + " = {id} ""RETURN n"
        while True:
            try:
                results = tx.run(query, id=node_id).values()
                break
            except TransientError:
                pass
    node = results[0][0]
    return node


def getnodeagents(tx, node_id, uid="name"):
    """
    Finds all agents currently located at a node

    :param tx: neo4j read or write transaction
    :param node_id: id of node
    :param uid: type of id node uses

    :return: List of agents at node
    """
    query = "MATCH (a)-[r:LOCATED]->(n) ""WHERE n." + uid + " = '" + str(node_id) + "' RETURN a"
    while True:
        try:
            results = tx.run(query).values()
            break
        except TransientError:
            pass
    results = [res[0] for res in results]
    return results


def getnodevalue(tx, node, value, label=None, uid=None):
    """
    Retrieves a particular value from a node

    :param tx: neo4j read or write transaction
    :param node: id of the node
    :param value: attribute to return
    :param label: label of the node
    :param uid: type of id used

    :return: value of attribute asked for
    """
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


def getrunname(tx):
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


def gettime(tx):
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
    time = 1 + gettime(tx)
    query = "MATCH (a:Clock) ""SET a.time={time} "
    while True:
        try:
            return tx.run(query, time=time)
        except TransientError:
            pass


def shortestpath(tx, node_a, node_b, node_label, edge_label, directed=False):
    """
    Returns the length of the shortest path between two nodes, using edges of the type given in edge_label

    :param tx: neo4j read or write transaction
    :param node_a: first node id
    :param node_b: second node id
    :param node_label: label for both nodes
    :param edge_label: label for the type of relationships to use in path
    :param directed: whether to consider direction of path in calculations

    :return: Length of shortest path between two nodes
    """
    if directed:
        directionality = 'OUTGOING'
    else:
        directionality = 'BOTH'
    query = "MATCH (a) WHERE a.id=" + str(node_a) + " WITH a MATCH (b) WHERE b.id=" + str(node_b) + " WITH a, b "
    query = query + "CALL algo.shortestPath(a, b,null, {relationshipQuery:'" + edge_label
    query = query + "', direction: '" + directionality + "'}) YIELD totalCost RETURN totalCost"
    while True:
        try:
            sp = tx.run(query).values()
            break
        except TransientError:
            pass
    if sp:
        return sp[0][0]


def updateedge(tx, edge, attr, value, uid=None):
    """
    Modify an attribute of an edge

    :param tx: neo4j write transaction
    :param edge: relationship object
    :param attr: attribute to modify
    :param value: new value of attribute
    :param uid: type of id used in system

    :return: None
    """
    if not uid:
        uid = "id"
    start = edge.start_node
    end = edge.end_node
    query = "MATCH (a:Node)-[r:REACHES]->(b:Node) ""WHERE a." + uid + "={start} AND b." + uid + \
            "={end} ""SET r." + attr + "={val}"
    while True:
        try:
            tx.run(query, start=start[uid], end=end[uid], val=value)
            break
        except TransientError:
            pass


def updatenode(tx, node, attr, value, uid=None, label=None):
    """
    Update attribute of a node

    :param tx: neo4j write transaction
    :param node: node id
    :param attr: attribute to be updated
    :param value: new value for the attribute
    :param uid: type of id being used
    :param label: lable of node

    :return: None
    """
    if not uid:
        uid = "id"
    if not label:
        label = "Node"
    query = "MATCH (a:" + label + ") ""WHERE a." + uid + "={node} ""SET a." + attr + "={value}"
    while True:
        try:
            tx.run(query, node=node, value=value)
            break
        except TransientError:
            pass


def updateagent(tx, node, attr, value, uid=None):
    """
    Update an agents attribute value.

    :param tx: neo4j write transaction
    :param node: node id
    :param attr: attribute to be updated
    :param value: new value of attribute
    :param uid: type of id used

    :return: None
    """
    if not uid:
        uid = "id"
    query = "MATCH (a:Agent) ""WHERE a." + uid + "={node} ""SET a." + attr + "={value}"
    while True:
        try:
            tx.run(query, node=node, value=value)
            break
        except TransientError:
            pass


def deleteagent(tx, agent, uid=None):
    """
    Delete an agent and all its relationships in the database

    :param tx: neo4j write transaction
    :param agent: agent id
    :param uid: type of id used

    :return: None
    """
    if not uid:
        uid = "id"
    while True:
        try:
            tx.run("MATCH (n:Agent) ""WHERE n." + uid + "={ID} ""DETACH DELETE n", ID=agent[uid])
            break
        except TransientError:
            pass


def addagent(tx, node, label, params, uid=None):
    """
    Insert a new agent into the system at node

    :param tx: neo4j write transaction
    :param node: node to locate agent at
    :param label: label of node
    :param params: list of parameters of agent
    :param uid: type of id used by node

    :return: None
    """
    if not uid:
        uid = "id"
    query = "MATCH (n:Agent) ""WITH n ""ORDER BY n.id DESC ""RETURN n.id"
    highest_id = tx.run(query).values()
    if highest_id:
        agent_id = highest_id[0][0] + 1
    else:
        agent_id = 0
    query = "CREATE (a:" + label + " {id:" + str(agent_id)
    for param in params:
        query = query + ", " + param + ":" + str(params[param])
    query = query + "})-[r:LOCATED]->(n)"
    while True:
        try:
            tx.run("MATCH (n:Node) ""WHERE n." + uid + "= '" + node[uid] + "' " + query)
            break
        except TransientError:
            pass


def createedge(tx, node_a, node_b, label_a, label_b, edge_label, parameters=None):
    """
    Adds and edge between two nodes with attributes and label as given

    :param tx: neo4j write transaction
    :param node_a: source node id
    :param node_b: target node id
    :param label_a: source node label
    :param label_b: target node label
    :param edge_label: label of new edge
    :param parameters: parameters of new edge

    :return: None
    """
    query = "MATCH (a:" + label_a + ") WHERE a.id=" + str(node_a) + " WITH a MATCH (b:" + label_b + ") WHERE b.id=" \
            + str(node_b) + " WITH a, b CREATE (a)-[n:" + edge_label
    if parameters:
        query = query + " {" + str(parameters) + "}"
    query = query + "]->(b) "
    while True:
        try:
            tx.run(query)
            break
        except TransientError:
            pass


def shortestsocialpath(tx, node_id, agent_id, agent_label=None, node_label=None):
    """
    Returns shortest path using social links from an agent to agents located at a given node

    :param node_id: node target agents must be located at
    :param agent_id: id of source agent
    :param agent_label: type of source agent
    :param node_label: type of target node

    :return:
    """
    agents = getnodeagents(tx, node_id, "name")
    paths = [shortestpath(tx, agent_id, ag, edge_label="SOCIAL") for ag in agents]
    if paths:
        return min(paths)
    else:
        return float('inf')


def addlabelnode(tx, node_id, label):
    """
    Add database label to an existing node, nodes only not agents

    :param tx: neo4j write transaction
    :param node_id: name of node to be updated
    :param label: new label to be added, must be in CamelCase

    :return: None
    """
    query = "MATCH (a:Node) WITH a.name=" + node_id + " SET a :" + label
    while True:
        try:
            tx.run(query)
            break
        except TransientError:
            pass


def addlabelagent(tx, agent_id, label):
    """
    Add extra label to an agent in the database

    :param tx: neo4j write transaction
    :param agent_id: id number of agent to update
    :param label: new label to be added, must be in CamelCase

    :return: None
    """
    query = "MATCH (a:Agent) WITH a.id=" + agent_id + " SET a :" + label
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
