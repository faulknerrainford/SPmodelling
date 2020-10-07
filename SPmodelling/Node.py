from abc import ABC, abstractmethod
import specification
import SPmodelling.Interface as intf


class Node(ABC):
    """
    Node class implements physical node locations
    """

    def __init__(self, name, capacity=None, duration=None, queue=None, nuid="name", classname=None):
        """
        Sets name of the node and other properties.

        :param name: Used as node id
        :param capacity: Max number of agents which can be located at node
        :param duration: Number of timesteps all agents spend at node
        :param queue: List of agents and times for them to be processed at nodes with predictions
        :param nuid: defaults to "name" unless another form of id is used.
        """
        self.name = name
        self.capacity = capacity
        self.duration = duration
        self.queue = queue
        self.nuid = nuid
        self.classname = classname

    def available_services(self, tx):
        return intf.check_services_location(tx, (self.name, "Node", "name"))

    @abstractmethod
    def agents_ready(self, tx):
        """
        Identifies the set of current agents for processing, either the correct set in the queue or all the agents at
        the node. It checks for unqueued agents in nodes with queue and runs the nodes prediction function to add them
        to the queue. It then gathers the agents local environment perception and passes that to the agent when calling
        the move function. We then delete the part of the queue that has been processed to save space. Subclass must
        implement this function for any aspects unique to model.

        :param tx: neo4j write transaction

        :return: None
        """
        agents = intf.get_node_agents(tx, [self.name, "Node", "name"])
        clock = intf.get_time(tx)
        if self.queue or self.queue == {}:
            queueagents = [key for time in self.queue.keys() for key in self.queue[time].keys()]
            newagents = [ag for ag in agents if ag[0] not in queueagents]
            # run prediction on each unqueued agent
            for ag in newagents:
                self.agent_prediction(tx, ag)
        for ag in agents:
            if self.queue:
                if clock in self.queue.keys():
                    if ag[0] in self.queue[clock].keys():
                        agper = self.agent_perception(tx, ag, self.queue[clock][ag[0]][0],
                                                      self.queue[clock][ag[0]])
                        for label in intf.check_node_label(tx, ag):
                            if label in specification.agentclasses.keys():
                                Agclass = specification.agentclasses[label]
                                agclass = Agclass(ag[0])
                                agclass.move(tx, agper)
            else:
                agper = self.agent_perception(tx, ag)
                for label in intf.check_node_label(tx, ag):
                    if label in specification.agentclasses.keys():
                        Agclass = specification.agentclasses[label]
                        agclass = Agclass(ag["id"])
                        agclass.move(tx, agper)
        if self.queue and clock in self.queue.keys():
            del self.queue[clock]

    @abstractmethod
    def agent_perception(self, tx, agent, dest=None, waittime=None):
        """
        The local environment of the node filtered by availability to a particular agent. Subclass must implement this
        function to add node filtering for particular model

        :param tx: neo4j read or write transaction
        :param agent: agent id, label and id type
        :param dest: passed by nodes with queues if agent destination has already been determined by prediction.
        :param waittime: time the agent has been waiting at the node

        :return: view of local environment for agent as list of relationships
        """
        if dest:
            view = dest
        else:
            view = intf.perception(tx, agent)[1:]
        if type(view) == list:
            for edge in view:
                if "cap" in edge.end_node.keys():
                    if edge.end_node["cap"] <= edge.end_node["load"]:
                        view.remove(edge)
        return view

    @abstractmethod
    def agent_prediction(self, tx, agent):
        """
        Predict how long the agent will stay at the node and its destination once it leaves. This must be implemented by
        the subclass to predict agent behaviour if node has a queue.

        :param tx: neo4j write transaction
        :param agent: agent id, label and id type

        :return: view of local environment for agent
        """
        view = intf.perception(tx, agent)
        return view
