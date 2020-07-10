def perception(tx, agent):
    """
    Provides the local environment for the given agent

    :param tx: write transaction for neo4j database
    :param agent: id number for agent

    :return: Node the agent is located at followed by the outgoing edges of that node and those edges end nodes.
    """
    results = tx.run("MATCH (m:Agent)-[s:LOCATED]->(n:Node) "
                     "WITH n, m "
                     "WHERE m.id={agent} "
                     "MATCH (n)-[r:REACHES]->(a) "
                     "RETURN n, r, a", agent=agent).values()
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
    results = tx.run("MATCH (m:Agent)-[s:LOCATED]->(n:Node) "
                     "WHERE m.id={agent} "
                     "RETURN n", agent=agent).values()
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
    query = "MATCH (a"
    if label_a:
        query = query + ":" + label_a
    query = query + ")-[r:SOCIAL]->(b"
    if label_b:
        query = query + ":" + label_b
    query = query + ") WHERE a.id={node_a} and b.id={node_b} SET r." + attribute + "={value} "
    tx.run(query, node_a=node_a, node_b=node_b, value=value)


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
    query = query + "]->(b:" + label_b + ") WHERE a.id=" + str(node_a) + " and b.id=" + str(node_b)
    query = query + " DELETE r RETURN COUNT(r)"
    tx.run(query)


def agentcontacts(tx, node_a, label, contact_label=None):
    """
    Returns outgoing contact edges from a node

    :param tx: neo4j read or write transaction
    :param node_a: source node id
    :param label: source node label
    :param contact_label: type of out going relationship

    :return: relationships and end nodes
    """
    if contact_label:
        contact_label = ": " + contact_label
    else:
        contact_label = ": " + label
    results = tx.run("MATCH (a:" + label + ")-[r:SOCIAL]->(b" + contact_label + ") "
                                                                                "WHERE a.id={node_a} "
                                                                                "RETURN r, b", node_a=node_a).values()
    return [res[0] for res in results]


def colocated(tx, agent):
    """
    Find agents at the same physical node as the given agent

    :param tx: neo4j read or write transaction
    :param agent: agent id

    :return: List of co-located agents
    """
    results = tx.run("MATCH (m:Agent)-[s:LOCATED]->(n:Node) "
                     "WITH n "
                     "WHERE m.id={agent} "
                     "MATCH (a:Agent)-[s:LOCATED]->(n:Node) "
                     "RETURN a", agent=agent).values()
    results = [res[0] for res in results]
    return results


def getnode(tx, nodeid, label=None, uid=None):
    """
    Returns the details of a given node

    :param tx: neo4j read or write transaction
    :param nodeid: id for wanted node
    :param label: node label
    :param uid: type of id

    :return: Node object
    """
    if not uid:
        uid = "id"
    if label == "Agent":
        query = "MATCH (n:Agent) ""WHERE n." + uid + " = {id} ""RETURN n"
        results = tx.run(query, id=nodeid, lab=label).values()
    elif label:
        query = "MATCH (n:" + label + ") ""WHERE n." + uid + " = {id} ""RETURN n"
        results = tx.run(query, id=nodeid).values()
    else:
        query = "MATCH (n) ""WHERE n." + uid + " = {id} ""RETURN n"
        results = tx.run(query, id=nodeid).values()
    node = results[0][0]
    return node


def getnodeagents(tx, nodeid, uid="name"):
    """
    Finds all agents currently located at a node

    :param tx: neo4j read or write transaction
    :param nodeid: id of node
    :param uid: type of id node uses

    :return: List of agents at node
    """
    query = "MATCH (a)-[r:LOCATED]->(n) ""WHERE n." + uid + " ={id} ""RETURN a"
    results = tx.run(query, id=nodeid).values()
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
    if label:
        query = "MATCH (a:" + label + ") ""WHERE a." + uid + "=" + str(node) + " ""RETURN a." + value
    else:
        query = "MATCH (a:Node) ""WHERE a." + uid + "=" + str(node) + " ""RETURN a." + value
    results = tx.run(query, node=node).value()
    return results[0]


def getrunname(tx):
    """
    Retrieve the label formed for this run, saved in node in database

    :param tx: neo4j read or write transaction

    :return: run name string
    """
    query = "MATCH (a:Tag) ""RETURN a.tag"
    return tx.run(query).value()[0]


def gettime(tx):
    """
    Retrieves the current time on the database clock

    :param tx: neo4j read or write transaction

    :return: Current time on clock
    """
    query = "MATCH (a:Clock) ""RETURN a.time"
    return tx.run(query).value()[0]


def tick(tx):
    """
    Increment the clock in the database

    :param tx: neo4j write transaction

    :return: New time
    """
    time = 1 + gettime(tx)
    query = "MATCH (a:Clock) ""SET a.time={time} "
    return tx.run(query, time=time)


def shortestpath(tx, node_a, node_b, node_label, edge_label, directed=False):
    """
    Returns the length of the shortest path between two nodes

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
    sp = tx.run(query).values()[0]
    return sp[0]


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
    tx.run(query, start=start[uid], end=end[uid], val=value)


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
    tx.run(query, node=node, value=value)


def updateagent(tx, node, attr, value, uid=None):
    """
    Update and agents attribute value.

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
    tx.run(query, node=node, value=value)


def deleteagent(tx, agent, uid=None):
    """
    Delete an agent and it's location in database

    :param tx: neo4j write transaction
    :param agent: agent id
    :param uid: type of id used

    :return: None
    """
    if not uid:
        uid = "id"
    tx.run("MATCH (n:Agent)-[r:LOCATED]->() ""WHERE n." + uid + "={ID} ""DELETE r", ID=agent[uid])
    tx.run("MATCH (n:Agent) ""WHERE n." + uid + "={ID} ""DELETE n", ID=agent[uid])


def addagent(tx, node, label, params, uid=None):
    """
    Insert a new agent into the system

    :param tx: neo4j write transaction
    :param node: node to locate agent at
    :param label: label of node
    :param params: list of parameters of agent
    :param uid: type of id used by node

    :return: None
    """
    if not uid:
        uid = "id"
    query = "MATCH (n: " + label + ") ""WITH n ""ORDER BY n.id DESC ""RETURN n.id"
    highest_id = tx.run(query).values()
    if highest_id:
        agent_id = highest_id[0][0] + 1
    else:
        agent_id = 0
    query = "CREATE (a:" + label + " {id:" + str(agent_id)
    for param in params:
        query = query + ", " + param + ":" + str(params[param])
    query = query + "})-[r:LOCATED]->(n)"
    tx.run("MATCH (n:Node) ""WHERE n." + uid + "= '" + node[uid] + "' " + query)


def createedge(tx, node_a, node_b, label_a, label_b, edge_label, parameters=None):
    """
    Adds and edge between to nodes with attributes and label as given
    :param tx: neo4j write transaction
    :param node_a: source node id
    :param node_b: target node id
    :param label_a: source node label
    :param label_b: target node label
    :param edge_label: label of new edge
    :param parameters: parameters of new edge

    :return: None
    """
    query = "MATCH (a:" + label_a + ") WHERE a.id=" + str(node_a) + " WITH a MATCH (b:" + label_b + ") " \
                                                                                                    "WHERE b.id=" + str(
        node_b) + " " \
                  "WITH a, b " \
                  "CREATE (a)-[n:" + edge_label
    if parameters:
        query = query + " {" + str(parameters) + "}"
    query = query + "]->(b) "
    tx.run(query)
