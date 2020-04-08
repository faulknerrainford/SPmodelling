

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
            edges = [edge[1]for edge in results]
            results = [node] + edges
        return results

    @staticmethod
    def getnode(tx, nodeid, label=None, uid=None):
        if not uid:
            uid = "id"
        if label == "Agent":
            query = "MATCH (n:Agent) ""WHERE n." + uid + " = {id} ""RETURN n"
            results = tx.run(query, id=nodeid, lab=label).values()
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
            query = "MATCH (a:" + label + ") ""WHERE a." + uid + "={node} ""RETURN a." + value
        else:
            query = "MATCH (a:Node) ""WHERE a." + uid + "={node} ""RETURN a." + value
        return tx.run(query, node=node).value()[0]

    @staticmethod
    def getrunname(tx):
        query = "MATCH (a:Tag) ""RETURN a.tag"
        return tx.run(query).value()[0]

    @staticmethod
    def gettime(tx):
        query = "MATCH (a:Clock) ""RETURN a.time"
        return tx.run(query).value()[0]

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
        query = "MATCH (a:Node)-[r:REACHES]->(b:Node) ""WHERE a." + uid + "={start} AND b." + uid +\
                "={end} ""SET r." + prop + "={val}"
        tx.run(query, start=start[uid], end=end[uid], val=value)

    @staticmethod
    def updatenode(tx, node, prop, value, uid=None):
        if not uid:
            uid = "id"
        query = "MATCH (a:Node) ""WHERE a." + uid + "={node} ""SET a." + prop + "={value}"
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
        query = "MATCH (n:"+label+") ""WITH n ""ORDER BY n.id DESC ""RETURN n.id"
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

        # TODO: Integrate toy functionality back in by updating toy files to use new system

        # CODE FOR TOY
        # switch = random()
        # values = ""
        # for val in params:
        #     values = values + ", " + val[0] + ":"+str(val[1])+" "
        # query = "CREATE (a:"+label+" {" + uid + ":{aID}, switch:{SWITCH}"+values+"})-[r:LOCATED]->(n)"
        # tx.run("MATCH (n:Node) ""WHERE n." + uid + "={nID} "+query, aID=agentid, SWITCH=switch, nID=node[uid])
