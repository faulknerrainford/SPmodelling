class Interface:

    def __init__(self, node_vector_length=0, edge_vector_length=0):
        self.node_vector_length = node_vector_length
        self.edge_vector_length = edge_vector_length

    @staticmethod
    def perception(tx, agent):
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

    @staticmethod
    def locateagent(tx, agent):
        results = tx.run("MATCH (m:Agent)-[s:LOCATED]->(n:Node) "
                         "WHERE m.id={agent} "
                         "RETURN n", agent=agent).values()
        return results[0][0]

    @staticmethod
    def updatecontactedge(tx, node_a, node_b, attribute, value, label_a=None, label_b=None):
        query = "MATCH (a"
        if label_a:
            query = query + ":" + label_a
        query = query + ")-[r:SOCIAL]->(b"
        if label_b:
            query = query + ":" + label_b
        query = query + ") WHERE a.id={node_a} and b.id={node_b} SET r." + attribute + "={value} "
        tx.run(query, node_a=node_a, node_b=node_b, value=value)

    @staticmethod
    def deletecontact(tx, node_a, node_b, label_a, label_b, contact_type='SOCIAL'):
        query = "MATCH (a:" + label_a + ")-[r"
        if contact_type:
            query = query + ":" + contact_type
        query = query + "]->(b:" + label_b + ") WHERE a.id=" + str(node_a) + " and b.id=" + str(node_b) + " DELETE r RETURN COUNT(r)"
        print(query)
        return tx.run(query)

    @staticmethod
    def agentcontacts(tx, node_a, label, contact_label=None):
        if contact_label:
            contact_label = ": " + contact_label
        else:
            contact_label = ": " + label
        results = tx.run("MATCH (a:" + label + ")-[r:SOCIAL]->(b" + contact_label + ") "
                                                                                    "WHERE a.id={node_a} "
                                                                                    "RETURN r, b", node_a=node_a).values()
        return [res[0] for res in results]

    @staticmethod
    def colocated(tx, agent):
        results = tx.run("MATCH (m:Agent)-[s:LOCATED]->(n:Node) "
                         "WITH n "
                         "WHERE m.id={agent} "
                         "MATCH (a:Agent)-[s:LOCATED]->(n:Node) "
                         "RETURN a", agent=agent).values()
        results = [res[0] for res in results]
        return results

    @staticmethod
    def getnode(tx, nodeid, label=None, uid=None):
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

    @staticmethod
    def getnodeagents(tx, nodeid, uid="name"):
        query = "MATCH (a)-[r:LOCATED]->(n) ""WHERE n." + uid + " ={id} ""RETURN a"
        results = tx.run(query, id=nodeid).values()
        results = [res[0] for res in results]
        return results

    @staticmethod
    def getnodevalue(tx, node, value, label=None, uid=None):
        if not uid:
            uid = "id"
        if label:
            query = "MATCH (a:" + label + ") ""WHERE a." + uid + "=" + str(node) + " ""RETURN a." + value
        else:
            query = "MATCH (a:Node) ""WHERE a." + uid + "=" + str(node) + " ""RETURN a." + value
        results = tx.run(query, node=node).value()
        return results[0]

    @staticmethod
    def getrunname(tx):
        query = "MATCH (a:Tag) ""RETURN a.tag"
        return tx.run(query).value()[0]

    @staticmethod
    def gettime(tx):
        query = "MATCH (a:Clock) ""RETURN a.time"
        return tx.run(query).value()[0]

    @staticmethod
    def tick(tx):
        time = 1 + Interface().gettime(tx)
        query = "MATCH (a:Clock) ""SET a.time={time} "
        return tx.run(query, time=time)

    @staticmethod
    def shortestpath(tx, node_a, node_b, node_label, edge_label, directed=False):
        if directed:
            directionality = 'OUTGOING'
        else:
            directionality = 'BOTH'
        query = "MATCH (a) WHERE a.id=" + str(node_a) + " WITH a MATCH (b) WHERE b.id=" + str(node_b) + " WITH a, b "
        query = query + "CALL algo.shortestPath(a, b,null, {relationshipQuery:'" + edge_label
        query = query + "', direction: '" + directionality + "'}) YIELD totalCost RETURN totalCost"
        sp = tx.run(query).values()[0]
        return sp[0]

    @staticmethod
    def getnodevector(node):
        return dict(list(tuple(node.items())))

    @staticmethod
    def getedgevector(edge):
        return dict([tuple(edge.items())[0]])

    @staticmethod
    def updateedge(tx, edge, prop, value, uid=None):
        if not uid:
            uid = "id"
        start = edge.start_node
        end = edge.end_node
        query = "MATCH (a:Node)-[r:REACHES]->(b:Node) ""WHERE a." + uid + "={start} AND b." + uid + \
                "={end} ""SET r." + prop + "={val}"
        tx.run(query, start=start[uid], end=end[uid], val=value)

    @staticmethod
    def updatenode(tx, node, prop, value, uid=None, label=None):
        if not uid:
            uid = "id"
        if not label:
            label = "Node"
        query = "MATCH (a:" + label + ") ""WHERE a." + uid + "={node} ""SET a." + prop + "={value}"
        tx.run(query, node=node, value=value)

    @staticmethod
    def updateagent(tx, node, prop, value, uid=None):
        if not uid:
            uid = "id"
        query = "MATCH (a:Agent) ""WHERE a." + uid + "={node} ""SET a." + prop + "={value}"
        tx.run(query, node=node, value=value)

    @staticmethod
    def deleteagent(tx, agent, uid=None):
        if not uid:
            uid = "id"
        tx.run("MATCH (n:Agent)-[r:LOCATED]->() ""WHERE n." + uid + "={ID} ""DELETE r", ID=agent[uid])
        tx.run("MATCH (n:Agent) ""WHERE n." + uid + "={ID} ""DELETE n", ID=agent[uid])

    @staticmethod
    def addagent(tx, node, label, params, uid=None):
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

    @staticmethod
    def createedge(tx, node_a, node_b, label_a, label_b, edge_label, parameters=None):
        query = "MATCH (a:" + label_a + ") WHERE a.id=" + str(node_a) + " WITH a MATCH (b:" + label_b + ") " \
                                                                  "WHERE b.id=" + str(node_b) + " " \
                                                                  "WITH a, b " \
                                                                  "CREATE (a)-[n:" + edge_label
        if parameters:
            query = query + " {" + str(parameters) + "}"
        query = query + "]->(b) "
        print(query)
        tx.run(query)

        # TODO: Integrate toy functionality back in by updating toy files to use new system

        # CODE FOR TOY
        # switch = random()
        # values = ""
        # for val in params:
        #     values = values + ", " + val[0] + ":"+str(val[1])+" "
        # query = "CREATE (a:"+label+" {" + uid + ":{aID}, switch:{SWITCH}"+values+"})-[r:LOCATED]->(n)"
        # tx.run("MATCH (n:Node) ""WHERE n." + uid + "={nID} "+query, aID=agentid, SWITCH=switch, nID=node[uid])
