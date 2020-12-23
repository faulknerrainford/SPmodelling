from abc import ABC, abstractmethod
import SPmodelling.Interface as intf


def filter_resource(dri, agent, edges, resource_edge, resource_agent):
    """
    Filters a set of edges and end nodes based on a resource.

    :param dri: neo4j database driver for database access
    :param agent: list of agent id, label and id type
    :param edges: list of edges
    :param resource_edge: name of resource cost on edges
    :param resource_agent: name of resource contained in agent

    :return: list of edges for which agent has sufficient resources
    """
    agent, agent_label, agent_uid = tuple(agent)
    valid_edges = []
    current_resources = intf.get_node_value(dri, [agent, agent_label, agent_uid], resource_agent)
    if len(edges) > 1:
        for edge in edges:
            cost = 0
            if edge.end_node[resource_edge]:
                cost = cost + edge.end_node[resource_edge]
            if edge[resource_edge]:
                cost = cost + edge[resource_edge]
            if current_resources > -cost:
                valid_edges = valid_edges + [edge]
    else:
        valid_edges = edges
    return valid_edges


def filter_threshold(dri, agent, edges, resource_edge, resource_agent):
    """
    Filter agents available edges based on an agent resource exceeding a threshold

    :param dri: neo4j database driver for access to database
    :param agent: agent tuple - agent id, label and id type
    :param edges: list of edges available
    :param resource_edge: resource threshold given by edge
    :param resource_agent: resource on agent for comparison

    :return: list of filtered edges
    """
    threshold = intf.get_node_value(dri, agent, resource_agent)
    if len(edges) < 2:
        if type(edges) == list and edges:
            choice = edges[0]
        else:
            choice = edges
        return choice
    else:
        options = []
        for edge in edges:
            if edge[resource_edge] <= threshold:
                options = options + [edge]
        return options


class MobileAgent(ABC):
    """
    Class for simulating agents which move between locations in a network
    """

    @abstractmethod
    def __init__(self, agentid, params=None, nuid="id"):
        """
        :param agentid: integer agent id value
        :param params: the dictionary of key value pairs to be set as parameters of the agent
        :param nuid: the name of the unique id field, defaults to "id" indicating an integer numerical id
        """
        self.id = agentid
        self.view = None
        self.params = params
        self.choice = None
        self.nuid = nuid
        self.services = None
        self.core_operations = "default"

    @abstractmethod
    def generator(self, dri, params):
        """
        Subclass should implement code to generate a specialised agent using the interface to insert the new agent into
        the database, the base function does nothing.

        :param dri: driver for a neo4j database
        :param params: paramaters are given as a list to be used by the subclass.

        :return: None
        """
        pass

    @abstractmethod
    def move_perception(self, dri, perc):
        """
        Subclass must implement this class to perform the Agents filtering to remove options the agent considers not
        possible for it. The agent will then reset the agent view to the filtered version.

        :param dri: Driver for neo4j database
        :param perc: Perception passed to agent from local node

        :return: None
        """
        self.view = perc

    @abstractmethod
    def move_choose(self, dri, perc):
        """
        Subclass must implement this function to make a choice between all possible options after node and agent filtering
        This class calls the agent perception function so super call must be made at start of funciton.

        :param dri: Driver for neo4j database
        :param perc: passed by node to give agent current local options

        :return: None
        """
        self.move_perception(dri, perc)

    @abstractmethod
    def move_learn(self, dri, choice, service):
        """
        Subclass must implement this function to make changes to the agent and node after moving.

        :param dri: Driver for neo4j
        :param choice: Relationship object passed from the interface which the agent moved along

        :return: [choice, dri] Relationship object and neo4j write transaction
        """
        return [choice, dri]
        # uses interface to update network based on choice

    @abstractmethod
    def move_payment(self, dri):
        """
        Subclass must implement this function to make changes to the agent, edges and nodes before/during movement.
        Including paying any cost of the movement.

        :param dri: Driver for neo4j database

        :return: None
        """
        return None

    def move_services(self, dri):
        """
        Checks for the existence of services available to the agent

        :param tx: neo4j database read or write transaction

        :return: List of available services or None if no services available
        """
        import specification
        node_class = specification.NodeClasses[self.choice.end_node["name"]]
        node = node_class(self.choice.end_node["name"])
        services = node.available_services(dri)
        if services:
            return services
        else:
            return None

    def move(self, dri, perc):
        """
        This function performs action of the agent. It calls the choice function and checks for a return and a payment
        has been made (if the payment fails the agent doesn't move). The agent is moved and then learns. There is no
        reason for subclasses to implement this function.

        :param dri: neo4j driver
        :param perc: perception of local surroundings passed to agent by it's local node

        :return: If agent moves return the new local node
        """
        self.choice = self.move_choose(dri, perc)
        if self.choice:
            if self.move_payment(dri):
                # Move node based on choice using dri
                intf.relocate_agent(dri, [self.id, "Agent", "id"], [self.choice.end_node["name"], "Node", "name"])
                service = self.move_services(dri)
                self.move_learn(dri, self.choice, service)
                return self.choice.end_node["name"]


class CommunicativeAgent(ABC):
    """
    Agent Class for agents in social networks. These agents act as nodes as well as agents.
    """

    @abstractmethod
    def __init__(self, agentid, params=None, nuid="id"):
        """
        :param agentid: integer agent id value
        :param params: the dictionary of key value pairs to be set as parameters of the agent
        :param nuid: the name of the unique id field, defaults to "id" indicating an integer numerical id
        """
        self.id = agentid
        self.view = None
        self.params = params
        self.nuid = nuid

    def socialise(self, dri):
        """
        This function does not need to be implemented in the subclass. It calls the five functions that an agent
        performs as an action. The agent will: look, update, talk, listen and then react.

        :param dri: neo4j driver

        :return: None
        """
        if not self.social_perception(dri):
            self.social_update(dri)
            self.social_talk(dri)
            self.social_listen(dri)
            self.social_react(dri)

    @abstractmethod
    def social_perception(self, dri):
        """
        The subclass should implement this function to allow the agent to detect other entities in its social network.
        Can also be used to detect agents colocated with it in a physical network.

        :param dri: driver for a neo4j database

        :return: None
        """
        return None

    @abstractmethod
    def social_update(self, dri):
        """
        The subclass should implement this function to allow the agent to update it's own values based on it's local
        social network and colocated agents in physical networks.

        :param dri: driver for a neo4j database

        :return: None
        """
        return None

    @abstractmethod
    def social_talk(self, dri):
        """
        The subclass should implement this function to allow agents to form new social connections possibly through
        existing connections or co-location.

        :param dri: driver for a neo4j database

        :return: None
        """
        return None

    @abstractmethod
    def social_listen(self, dri):
        """
        The subclass should implement this function to allow agents to change their values or form new connections based
        on the situation after talking.

        :param dri: driver for a neo4j database

        :return: None
        """
        return None

    @abstractmethod
    def social_react(self, dri):
        """
        The subclass should implement this function. The agent has a final opportunity to adjust its values and manage
        its social network. This includes managing the number of social links.

        :param dri: driver for neo4j database

        :return: None
        """
        return None
